"""
Inference Routes
API endpoints for AI inference and prediction
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field

from services.inference import InferenceService
from utils.logger import get_structured_logger

router = APIRouter()
logger = get_structured_logger()

# Request models
class PredictionRequest(BaseModel):
    """Request model for predictions"""
    prompt: str = Field(..., description="Input prompt for inference")
    request_type: str = Field(default="general", description="Type of request")
    code_type: Optional[str] = Field(None, description="Type of code to generate")
    code: Optional[str] = Field(None, description="Code to debug")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(None, description="Sampling temperature")

class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions"""
    requests: List[Dict[str, Any]] = Field(..., description="List of prediction requests")

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    status: str
    result: Any
    request_type: str
    processing_time: float
    timestamp: str
    model_info: Dict[str, Any]

def get_inference_service(request: Request) -> InferenceService:
    """Dependency to get inference service"""
    return request.app.state.inference_service

@router.post("/predict", response_model=PredictionResponse)
async def predict(
    request_data: PredictionRequest,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Main prediction endpoint
    
    Args:
        request_data: Prediction request data
        inference_service: Inference service instance
    
    Returns:
        Prediction response with results
    """
    try:
        # Convert to dict for service
        input_data = request_data.dict()
        
        # Perform prediction
        result = await inference_service.predict(
            input_data=input_data,
            request_type=request_data.request_type
        )
        
        # Log successful inference
        logger.log_inference(
            request_type=request_data.request_type,
            processing_time=result.get("processing_time", 0),
            status="success"
        )
        
        return result
        
    except Exception as e:
        # Log failed inference
        logger.log_inference(
            request_type=request_data.request_type,
            processing_time=0,
            status="error",
            error=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}"
        )

@router.post("/predict/batch")
async def batch_predict(
    request_data: BatchPredictionRequest,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Batch prediction endpoint
    
    Args:
        request_data: Batch prediction request data
        inference_service: Inference service instance
    
    Returns:
        List of prediction responses
    """
    try:
        results = await inference_service.batch_predict(request_data.requests)
        
        return {
            "status": "success",
            "results": results,
            "total_requests": len(request_data.requests),
            "successful_requests": len([r for r in results if r.get("status") == "success"])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch inference failed: {str(e)}"
        )

@router.get("/model/info")
async def get_model_info(
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Get model information
    
    Returns:
        Model information and capabilities
    """
    try:
        return inference_service.get_model_info()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model info: {str(e)}"
        )

@router.post("/code/generate")
async def generate_code(
    request_data: PredictionRequest,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Code generation endpoint
    
    Args:
        request_data: Code generation request
        inference_service: Inference service instance
    
    Returns:
        Generated code
    """
    try:
        input_data = {
            "prompt": request_data.prompt,
            "code_type": request_data.code_type or "general"
        }
        
        result = await inference_service.predict(
            input_data=input_data,
            request_type="code"
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code generation failed: {str(e)}"
        )

@router.post("/code/debug")
async def debug_code(
    request_data: PredictionRequest,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Code debugging endpoint
    
    Args:
        request_data: Debug request with code
        inference_service: Inference service instance
    
    Returns:
        Debug results
    """
    try:
        if not request_data.code:
            raise HTTPException(
                status_code=400,
                detail="Code is required for debugging"
            )
        
        input_data = {
            "prompt": request_data.prompt,
            "code": request_data.code
        }
        
        result = await inference_service.predict(
            input_data=input_data,
            request_type="debug"
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code debugging failed: {str(e)}"
        )

@router.post("/research")
async def research_topic(
    request_data: PredictionRequest,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Research topic endpoint
    
    Args:
        request_data: Research request
        inference_service: Inference service instance
    
    Returns:
        Research results
    """
    try:
        input_data = {"prompt": request_data.prompt}
        
        result = await inference_service.predict(
            input_data=input_data,
            request_type="research"
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {str(e)}"
        )
