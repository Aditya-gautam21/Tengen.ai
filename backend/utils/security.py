"""
Security utilities for Tengen.ai
"""

import re
import os
import hashlib
import secrets
from typing import Optional, List
from pathlib import Path
import bleach
from markupsafe import Markup

# Allowed HTML tags and attributes for sanitization
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'code', 'pre']
ALLOWED_ATTRIBUTES = {}

def sanitize_html(content: str) -> str:
    """Sanitize HTML content to prevent XSS"""
    return bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove path separators and dangerous characters
    safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
    # Remove leading dots and ensure not empty
    safe_filename = safe_filename.lstrip('.')
    if not safe_filename:
        safe_filename = f"file_{secrets.token_hex(4)}"
    return safe_filename

def validate_file_path(file_path: Path, allowed_directory: Path) -> bool:
    """Validate that file path is within allowed directory"""
    try:
        resolved_path = file_path.resolve()
        resolved_allowed = allowed_directory.resolve()
        return str(resolved_path).startswith(str(resolved_allowed))
    except (OSError, ValueError):
        return False

def validate_url(url: str, allowed_hosts: Optional[List[str]] = None) -> bool:
    """Validate URL to prevent SSRF attacks"""
    if not url:
        return False
    
    # Basic URL validation
    if not re.match(r'^https?://', url):
        return False
    
    # Extract hostname
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        if not hostname:
            return False
        
        # Check against allowed hosts if provided
        if allowed_hosts:
            return any(hostname == host or hostname.endswith(f'.{host}') 
                      for host in allowed_hosts)
        
        # Default: block private/local addresses
        import ipaddress
        try:
            ip = ipaddress.ip_address(hostname)
            return not (ip.is_private or ip.is_loopback or ip.is_link_local)
        except ValueError:
            # Not an IP address, allow public domains
            return not any(hostname.endswith(blocked) for blocked in 
                          ['localhost', '127.0.0.1', '0.0.0.0', '::1'])
    
    except Exception:
        return False

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)

def hash_password(password: str) -> str:
    """Hash password using secure algorithm"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

def validate_input_length(text: str, max_length: int = 10000) -> bool:
    """Validate input length to prevent DoS"""
    return len(text) <= max_length

def sanitize_log_input(text: str) -> str:
    """Sanitize text for logging to prevent log injection"""
    # Remove control characters and newlines
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    # Limit length
    return sanitized[:1000] if len(sanitized) > 1000 else sanitized

class SecurityHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def get_security_headers() -> dict:
        """Get recommended security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }

def check_file_signature(file_path: Path, expected_extensions: List[str]) -> bool:
    """Check file signature to validate file type"""
    import mimetypes
    
    # Get MIME type from file content
    try:
        import magic
        mime_type = magic.from_file(str(file_path), mime=True)
    except ImportError:
        # Fallback to extension-based detection
        mime_type, _ = mimetypes.guess_type(str(file_path))
    
    if not mime_type:
        return False
    
    # Map extensions to MIME types
    allowed_mimes = {
        '.json': 'application/json',
        '.txt': 'text/plain',
        '.csv': 'text/csv',
        '.md': 'text/markdown'
    }
    
    file_ext = file_path.suffix.lower()
    if file_ext not in expected_extensions:
        return False
    
    expected_mime = allowed_mimes.get(file_ext)
    return expected_mime and mime_type.startswith(expected_mime.split('/')[0])