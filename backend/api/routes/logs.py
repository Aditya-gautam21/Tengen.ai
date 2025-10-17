"""
Logs Routes
API endpoints for log management and viewing (admin only)
"""

import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

class LogEntry(BaseModel):
    """Log entry model"""
    timestamp: str
    level: str
    message: str
    source: str

@router.get("/logs")
async def get_logs(
    log_type: str = Query(default="all", description="Type of logs to retrieve"),
    lines: int = Query(default=100, description="Number of lines to retrieve"),
    level: Optional[str] = Query(default=None, description="Log level filter")
):
    """
    Get application logs (admin only)
    
    Args:
        log_type: Type of logs (all, access, error, main)
        lines: Number of lines to retrieve
        level: Log level filter
    
    Returns:
        Log entries
    """
    try:
        log_dir = "logs"
        
        if not os.path.exists(log_dir):
            return {"logs": [], "message": "No logs directory found"}
        
        # Determine log file
        if log_type == "access":
            log_file = os.path.join(log_dir, "tengen_access.log")
        elif log_type == "error":
            log_file = os.path.join(log_dir, "tengen_errors.log")
        elif log_type == "main":
            log_file = os.path.join(log_dir, "tengen.log")
        else:
            # Return all logs
            all_logs = []
            for filename in ["tengen.log", "tengen_access.log", "tengen_errors.log"]:
                filepath = os.path.join(log_dir, filename)
                if os.path.exists(filepath):
                    file_logs = await _read_log_file(filepath, lines // 3, level)
                    all_logs.extend(file_logs)
            return {"logs": all_logs[-lines:], "type": "all"}
        
        if not os.path.exists(log_file):
            return {"logs": [], "message": f"Log file {log_type} not found"}
        
        log_entries = await _read_log_file(log_file, lines, level)
        
        return {
            "logs": log_entries,
            "type": log_type,
            "count": len(log_entries)
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")

@router.get("/logs/download")
async def download_logs(
    log_type: str = Query(default="all", description="Type of logs to download")
):
    """
    Download log files (admin only)
    
    Args:
        log_type: Type of logs to download
    
    Returns:
        Log file content as plain text
    """
    try:
        log_dir = "logs"
        
        if log_type == "all":
            # Combine all log files
            content = ""
            for filename in ["tengen.log", "tengen_access.log", "tengen_errors.log"]:
                filepath = os.path.join(log_dir, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content += f"\n=== {filename} ===\n"
                        content += f.read()
        else:
            # Single log file
            if log_type == "access":
                filename = "tengen_access.log"
            elif log_type == "error":
                filename = "tengen_errors.log"
            elif log_type == "main":
                filename = "tengen.log"
            else:
                raise HTTPException(status_code=400, detail="Invalid log type")
            
            filepath = os.path.join(log_dir, filename)
            if not os.path.exists(filepath):
                raise HTTPException(status_code=404, detail="Log file not found")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        
        return PlainTextResponse(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=tengen_{log_type}_logs.txt"}
        )
        
    except Exception as e:
        logger.error(f"Failed to download logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download logs: {str(e)}")

@router.delete("/logs")
async def clear_logs(
    log_type: str = Query(default="all", description="Type of logs to clear")
):
    """
    Clear log files (admin only)
    
    Args:
        log_type: Type of logs to clear
    
    Returns:
        Clear operation result
    """
    try:
        log_dir = "logs"
        
        if not os.path.exists(log_dir):
            return {"message": "No logs directory found"}
        
        cleared_files = []
        
        if log_type == "all":
            for filename in ["tengen.log", "tengen_access.log", "tengen_errors.log"]:
                filepath = os.path.join(log_dir, filename)
                if os.path.exists(filepath):
                    open(filepath, 'w').close()  # Clear file content
                    cleared_files.append(filename)
        else:
            if log_type == "access":
                filename = "tengen_access.log"
            elif log_type == "error":
                filename = "tengen_errors.log"
            elif log_type == "main":
                filename = "tengen.log"
            else:
                raise HTTPException(status_code=400, detail="Invalid log type")
            
            filepath = os.path.join(log_dir, filename)
            if os.path.exists(filepath):
                open(filepath, 'w').close()  # Clear file content
                cleared_files.append(filename)
        
        return {
            "message": f"Cleared {len(cleared_files)} log file(s)",
            "cleared_files": cleared_files
        }
        
    except Exception as e:
        logger.error(f"Failed to clear logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")

async def _read_log_file(filepath: str, lines: int, level: Optional[str] = None) -> List[LogEntry]:
    """
    Read log file and parse entries
    
    Args:
        filepath: Path to log file
        lines: Number of lines to read
        level: Log level filter
    
    Returns:
        List of log entries
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            file_lines = f.readlines()
        
        # Get last N lines
        recent_lines = file_lines[-lines:] if len(file_lines) > lines else file_lines
        
        log_entries = []
        for line in recent_lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse log entry (basic parsing)
            try:
                parts = line.split(' - ', 3)
                if len(parts) >= 4:
                    timestamp = parts[0]
                    logger_name = parts[1]
                    log_level = parts[2]
                    message = parts[3]
                    
                    # Apply level filter
                    if level and log_level.lower() != level.lower():
                        continue
                    
                    log_entries.append(LogEntry(
                        timestamp=timestamp,
                        level=log_level,
                        message=message,
                        source=logger_name
                    ))
            except Exception:
                # If parsing fails, add as raw message
                log_entries.append(LogEntry(
                    timestamp="",
                    level="UNKNOWN",
                    message=line,
                    source="unknown"
                ))
        
        return log_entries
        
    except Exception as e:
        logger.error(f"Failed to read log file {filepath}: {e}")
        return []
