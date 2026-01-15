from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging
from agents.copywriting import generate_copy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Marketing Campaign Orchestrator",
    description="Orchestrates multiple marketing agents to generate complete campaigns",
    version="1.0.0"
)


# Models
class CampaignRequest(BaseModel):
    strategy: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy": {
                    "product": "EcoBottle - Reusable Water Bottle",
                    "audience": "environmentally conscious millennials",
                    "goal": "increase brand awareness",
                    "tone": "friendly and inspiring",
                    "platforms": ["Instagram", "Facebook", "Blog"],
                    "stylistics": "focus on sustainability"
                }
            }
        }


class CampaignResponse(BaseModel):
    status: str
    strategy: Dict[str, Any]
    copywriting: Dict[str, Any]
    # Future: add visual, market, media, outreach


# Routes
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Marketing Campaign Orchestrator",
        "version": "1.0.0",
        "available_agents": ["copywriting"]
    }


@app.post("/generate-campaign", response_model=CampaignResponse)
async def generate_campaign(request: CampaignRequest):
    """
    Orchestrate campaign generation by calling all agents
    """
    try:
        strategy = request.strategy
        
        logger.info(f"Generating campaign for product: {strategy.get('product', 'Unknown')}")
        
        logger.info("Calling copywriting agent...")
        copywriting_result = generate_copy(strategy)
        logger.info("Copywriting agent completed")
        
        # Future: Call other agents in parallel
        # visual_result = generate_visuals(strategy)
        # market_result = analyze_market(strategy)
        # media_result = plan_media(strategy)
        # outreach_result = plan_outreach(strategy)
        
        return CampaignResponse(
            status="success",
            strategy=strategy,
            copywriting=copywriting_result
        )
        
    except Exception as e:
        logger.error(f"Campaign generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Campaign generation failed: {str(e)}")


@app.post("/generate-copy")
async def generate_copy_only(request: CampaignRequest):
    """
    Generate only copywriting content (bypass orchestrator)
    """
    try:
        logger.info("Generating copy only...")
        result = generate_copy(request.strategy)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Copywriting error: {e}")
        raise HTTPException(status_code=500, detail=f"Copywriting failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
