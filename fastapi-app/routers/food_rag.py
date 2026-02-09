"""Food RAG Analysis Router"""
from fastapi import APIRouter, HTTPException
from models.food_models import FoodAnalysisRequest, FoodAnalysisResponse
from services.food_rag_service import FoodRAGPipeline
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/food-rag", tags=["food-rag"])
rag_pipeline = FoodRAGPipeline()

@router.post("/analyze", response_model=FoodAnalysisResponse)
async def analyze_food(request: FoodAnalysisRequest):
    try:
        result = await rag_pipeline.analyze_food(request)
        return result
    except Exception as e:
        logger.error(f"Food RAG failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "chromadb": rag_pipeline.client is not None}
