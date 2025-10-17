"""
Inference Service
Handles AI model inference and prediction requests
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from utils.logger import get_logger
from .base_service import BaseService

logger = get_logger(__name__)

class InferenceService(BaseService):
    """Service for handling AI inference requests"""
    
    def __init__(self):
        super().__init__()
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load the AI model"""
        try:
            # Import existing code_assist functionality
            from ..code_assist import get_llm, generate_code, debug_code
            from ..rag_pipeline import query_documents
            
            self.llm = get_llm()
            self.generate_code = generate_code
            self.debug_code = debug_code
            self.query_documents = query_documents
            
            self.model_loaded = True
            logger.info("AI model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
            self.model_loaded = False
    
    async def predict(self, 
                     input_data: Dict[str, Any], 
                     request_type: str = "general") -> Dict[str, Any]:
        """
        Main prediction endpoint
        
        Args:
            input_data: Input data for inference
            request_type: Type of request (general, code, research, debug)
        
        Returns:
            Dict containing prediction results
        """
        if not self.model_loaded:
            raise Exception("Model not loaded")
        
        start_time = datetime.now()
        
        try:
            # Extract input text/prompt
            prompt = input_data.get("prompt", "")
            if not prompt:
                raise ValueError("Prompt is required")
            
            # Route to appropriate handler based on request type
            if request_type == "code":
                result = await self._handle_code_request(prompt, input_data)
            elif request_type == "debug":
                result = await self._handle_debug_request(prompt, input_data)
            elif request_type == "research":
                result = await self._handle_research_request(prompt, input_data)
            else:
                result = await self._handle_general_request(prompt, input_data)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "result": result,
                "request_type": request_type,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "model_info": {
                    "model_name": "gemini-2.5-pro",
                    "version": "1.0.0"
                }
            }
            
        except Exception as e:
            logger.error(f"Inference error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "request_type": request_type,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_general_request(self, prompt: str, input_data: Dict[str, Any]) -> str:
        """Handle general inference requests"""
        return self.generate_code(prompt)
    
    async def _handle_code_request(self, prompt: str, input_data: Dict[str, Any]) -> str:
        """Handle code generation requests"""
        code_type = input_data.get("code_type", "general")
        enhanced_prompt = f"Generate {code_type} code: {prompt}"
        return self.generate_code(enhanced_prompt)
    
    async def _handle_debug_request(self, prompt: str, input_data: Dict[str, Any]) -> str:
        """Handle code debugging requests"""
        code = input_data.get("code", "")
        if not code:
            raise ValueError("Code is required for debugging")
        
        return self.debug_code(code)
    
    async def _handle_research_request(self, prompt: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle research/document query requests"""
        try:
            result = self.query_documents(prompt)
            return result
        except Exception as e:
            logger.warning(f"Document query failed: {e}")
            # Fallback to general inference
            return {
                "answer": self.generate_code(prompt),
                "sources": [],
                "fallback": True
            }
    
    async def batch_predict(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Handle batch prediction requests"""
        results = []
        
        for request in requests:
            try:
                result = await self.predict(
                    request.get("input_data", {}),
                    request.get("request_type", "general")
                )
                results.append(result)
            except Exception as e:
                results.append({
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": "gemini-2.5-pro",
            "version": "1.0.0",
            "loaded": self.model_loaded,
            "capabilities": ["text_generation", "code_generation", "debugging", "research"],
            "max_tokens": 8192,
            "temperature": 0.7
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for inference service"""
        return {
            "status": "healthy" if self.model_loaded else "unhealthy",
            "model_loaded": self.model_loaded,
            "service": "inference",
            "timestamp": datetime.now().isoformat()
        }
