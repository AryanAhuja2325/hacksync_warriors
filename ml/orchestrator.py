from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from agents.copywriting import generate_copy
from influencer_discovery import discover_influencers, generate_outreach_message
from agents.youtube_discovery import discover_youtube_influencers
from agents.market_change import find_influencers
from agents.outreach import generate_outreach_for_influencer
from agents.content_fetchers import fetch_youtube_content
from agents.content_normalizer import normalize_content_list
from agents.content_summarizer import summarize_content
from agents.visualAgent import VisualAgent
from agents.mediaAgent import generate_media_plan

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


class AIDiscoveryRequest(BaseModel):
    strategy: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy": {
                    "product": "EcoBottle - Reusable Water Bottle",
                    "audience": "environmentally conscious college students",
                    "platforms": ["Instagram", "YouTube"],
                    "stylistics": "sustainability",
                    "location": "India"
                }
            }
        }


class AIDiscoveryResponse(BaseModel):
    status: str
    count: int
    influencers: List[Dict[str, Any]]
    disclaimer: str
    metadata: Dict[str, Any]


class OutreachRequest(BaseModel):
    influencer: Dict[str, Any]
    campaign_details: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "influencer": {
                    "name": "FitWithRhea",
                    "platform": "Instagram",
                    "niche": "Fitness",
                    "followers": "120k",
                    "reason": "Creates college-focused fitness content"
                },
                "campaign_details": {
                    "product": "EcoBottle",
                    "tone": "friendly and inspiring"
                }
            }
        }


class YouTubeDiscoveryRequest(BaseModel):
    domain: str
    audience: str = ""
    country: str = "IN"
    min_followers: int = 10000
    max_followers: int = 500000
    max_results: int = 8
    
    class Config:
        json_schema_extra = {
            "example": {
                "domain": "sustainable fashion",
                "audience": "college students",
                "country": "IN",
                "min_followers": 10000,
                "max_followers": 500000,
                "max_results": 8
            }
        }


class YouTubeDiscoveryResponse(BaseModel):
    status: str
    count: int
    discovery_method: str
    verification_notice: str
    influencers: List[Dict[str, Any]]


class MarketDiscoveryRequest(BaseModel):
    domain: str
    target_audience: str
    platforms: List[str] = ["Instagram", "YouTube"]
    country: str = "IN"
    max_results: int = 10
    
    class Config:
        json_schema_extra = {
            "example": {
                "domain": "sustainable fashion",
                "target_audience": "young women aged 18-30",
                "platforms": ["Instagram", "YouTube"],
                "country": "IN",
                "max_results": 10
            }
        }


class MarketDiscoveryResponse(BaseModel):
    status: str
    count: int
    discovery_method: str
    verification_notice: str
    influencers: List[Dict[str, Any]]


class ContentAwareOutreachRequest(BaseModel):
    influencer: Dict[str, Any]
    brand_name: str
    product_domain: str
    target_audience: str
    message_type: str = "initial_contact"
    collaboration_idea: Optional[str] = None
    analyze_content: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "influencer": {
                    "name": "Tech Creator",
                    "platform": "YouTube",
                    "url": "https://youtube.com/@creator",
                    "niche": "tech reviews"
                },
                "brand_name": "TechGear Pro",
                "product_domain": "tech accessories",
                "target_audience": "tech enthusiasts",
                "message_type": "casual_dm",
                "collaboration_idea": "Product review collaboration",
                "analyze_content": True
            }
        }


class ContentAwareOutreachResponse(BaseModel):
    status: str
    influencer_name: str
    outreach: Dict[str, str]
    content_analysis: Optional[Dict[str, Any]] = None


class VisualMoodBoardRequest(BaseModel):
    strategy: Dict[str, Any]
    num_variations: int = 4
    reference_image_path: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy": {
                    "product": "EcoBottle - Sustainable Water Bottle",
                    "audience": "environmentally conscious college students",
                    "tone": "friendly and inspiring",
                    "stylistics": "sustainability and eco-friendly lifestyle"
                },
                "num_variations": 4,
                "reference_image_path": "path/to/reference.jpg"
            }
        }


class VisualMoodBoardResponse(BaseModel):
    status: str
    product: str
    audience: str
    visual_theme: str
    color_palette: List[str]
    tiles: List[Dict[str, Any]]
    total_generated: int
    json_file: str


class MediaPlanRequest(BaseModel):
    domain: str
    target_audience: str
    competitors: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "domain": "sustainable fashion",
                "target_audience": "environmentally conscious college students",
                "competitors": ["Everlane", "Patagonia", "Reformation"]
            }
        }


class MediaPlanResponse(BaseModel):
    status: str
    recommended_platforms: List[Dict[str, Any]]
    best_posting_times: Dict[str, Any]
    content_types: List[str]
    growth_strategies: List[str]
    mistakes_to_avoid: List[str]
    competitor_insights: Dict[str, Any]
    metadata: Dict[str, Any]


# Routes
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Marketing Campaign Orchestrator",
        "version": "2.0.0",
        "available_agents": [
            "copywriting",
            "ai_influencer_discovery",
            "youtube_discovery",
            "market_discovery",
            "content_aware_outreach",
            "visual_mood_board",
            "media_planning"
        ]
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


@app.post("/ai-discover-influencers", response_model=AIDiscoveryResponse)
async def ai_discover_influencers(request: AIDiscoveryRequest):
    """
    AI-powered influencer discovery based on campaign strategy
    
    Uses LLM to suggest relevant micro/nano influencers with justification.
    Results are AI-generated suggestions that should be verified before outreach.
    """
    try:
        logger.info(f"AI discovering influencers for product: {request.strategy.get('product', 'Unknown')}")
        
        result = discover_influencers(request.strategy)
        
        logger.info(f"AI suggested {result['count']} influencers")
        
        return AIDiscoveryResponse(
            status="success",
            count=result['count'],
            influencers=result['influencers'],
            disclaimer=result['disclaimer'],
            metadata=result['metadata']
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"AI discovery error: {e}")
        raise HTTPException(status_code=500, detail=f"AI discovery failed: {str(e)}")


@app.post("/generate-outreach")
async def generate_outreach(request: OutreachRequest):
    """
    Generate personalized outreach message for an influencer
    
    Creates authentic, context-aware collaboration proposals.
    """
    try:
        logger.info(f"Generating outreach for {request.influencer.get('name', 'Unknown')}")
        
        message = generate_outreach_message(
            influencer=request.influencer,
            campaign_details=request.campaign_details
        )
        
        return {
            "status": "success",
            "influencer": request.influencer['name'],
            "message": message
        }
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Outreach generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Outreach generation failed: {str(e)}")


@app.post("/discover-youtube-influencers", response_model=YouTubeDiscoveryResponse)
async def discover_youtube_influencers_endpoint(request: YouTubeDiscoveryRequest):
    """
    Discover real YouTube influencers using YouTube Data API v3
    
    Returns verified creators with real subscriber counts, filtered by niche and region.
    Data sourced directly from YouTube - real channels with verified metrics.
    
    ⚠️ Please verify profiles and content alignment before outreach.
    """
    try:
        logger.info(f"Discovering YouTube influencers: {request.domain} for {request.audience} in {request.country}")
        
        influencers = discover_youtube_influencers(
            domain=request.domain,
            audience=request.audience,
            country=request.country,
            min_followers=request.min_followers,
            max_followers=request.max_followers,
            max_results=request.max_results
        )
        
        logger.info(f"Found {len(influencers)} YouTube influencers")
        
        return YouTubeDiscoveryResponse(
            status="success",
            count=len(influencers),
            discovery_method="youtube_api_v3",
            verification_notice="⚠️ Please verify profiles and content alignment before outreach.",
            influencers=influencers
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"YouTube discovery error: {e}")
        raise HTTPException(status_code=500, detail=f"YouTube discovery failed: {str(e)}")


@app.post("/discover-market-influencers", response_model=MarketDiscoveryResponse)
async def discover_market_influencers(request: MarketDiscoveryRequest):
    """
    Discover real influencers using Google Custom Search API
    
    Returns verified profiles from Instagram/YouTube with relevance scoring.
    Uses domain-first queries to ensure relevant results.
    
    ⚠️ Please verify profiles and content alignment before outreach.
    """
    try:
        logger.info(f"Discovering market influencers: {request.domain} for {request.target_audience}")
        
        result = find_influencers(
            domain=request.domain,
            target_audience=request.target_audience,
            platforms=request.platforms,
            country=request.country,
            num_results=request.max_results
        )
        
        # Extract influencers list from result dict
        influencers = result.get("influencers", [])
        
        logger.info(f"Found {len(influencers)} market influencers")
        
        return MarketDiscoveryResponse(
            status="success",
            count=len(influencers),
            discovery_method="google_custom_search",
            verification_notice="⚠️ Verify profiles and content alignment before outreach. Relevance scores provided.",
            influencers=influencers
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Market discovery error: {e}")
        raise HTTPException(status_code=500, detail=f"Market discovery failed: {str(e)}")


@app.post("/generate-content-aware-outreach", response_model=ContentAwareOutreachResponse)
async def generate_content_aware_outreach(request: ContentAwareOutreachRequest):
    """
    Generate personalized outreach with optional content analysis
    
    If analyze_content=true and influencer is YouTube creator, fetches and analyzes
    their recent videos to create hyper-personalized outreach referencing actual content.
    
    Message types: casual_dm, initial_contact, follow_up, formal_email, partnership_proposal
    """
    try:
        influencer = request.influencer
        logger.info(f"Generating outreach for {influencer.get('name', 'Unknown')}")
        
        content_summary = None
        
        # Optional: Analyze content if requested and it's YouTube
        if request.analyze_content and influencer.get('platform') == 'YouTube':
            try:
                logger.info("Fetching and analyzing YouTube content...")
                
                # Fetch recent videos
                raw_content = fetch_youtube_content(
                    channel_url=influencer.get('url', ''),
                    max_videos=5
                )
                
                # Normalize content
                normalized_content = normalize_content_list(raw_content, "YouTube")
                
                # Summarize themes
                content_summary = summarize_content(normalized_content)
                
                logger.info("Content analysis complete")
                
            except Exception as e:
                logger.warning(f"Content analysis failed, falling back to basic outreach: {e}")
                content_summary = None
        
        # Generate outreach message
        outreach = generate_outreach_for_influencer(
            influencer=influencer,
            brand_name=request.brand_name,
            product_domain=request.product_domain,
            target_audience=request.target_audience,
            message_type=request.message_type,
            collaboration_idea=request.collaboration_idea,
            content_summary=content_summary
        )
        
        return ContentAwareOutreachResponse(
            status="success",
            influencer_name=influencer.get('name', 'Unknown'),
            outreach=outreach,
            content_analysis=content_summary if request.analyze_content else None
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Outreach generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Outreach generation failed: {str(e)}")


@app.post("/generate-mood-board", response_model=VisualMoodBoardResponse)
async def generate_mood_board(request: VisualMoodBoardRequest):
    """
    Generate visual mood board with 4 images based on campaign strategy
    
    Generates product-specific images showing target audience using the product.
    Supports optional reference image for image-to-image generation.
    Returns JSON file with image URLs and base64 data.
    
    At least 1 image will depict the target audience using the product (lifestyle shot).
    """
    try:
        strategy = request.strategy
        logger.info(f"Generating mood board for product: {strategy.get('product', 'Unknown')}")
        
        # Initialize visual agent
        visual_agent = VisualAgent()
        
        # Generate mood board
        result = visual_agent.generate_mood_board(
            strategy=strategy,
            num_variations=request.num_variations,
            reference_image_path=request.reference_image_path
        )
        
        logger.info(f"Mood board generated: {result['total_generated']}/{result['requested']} tiles")
        
        # Get JSON filename (latest file in output directory)
        import os
        import glob
        json_files = glob.glob(os.path.join(visual_agent.output_dir, "mood_board_*.json"))
        latest_json = max(json_files, key=os.path.getctime) if json_files else "N/A"
        
        return VisualMoodBoardResponse(
            status=result['status'],
            product=result['product'],
            audience=result['audience'],
            visual_theme=result['visual_theme'],
            color_palette=result['color_palette'],
            tiles=result['tiles'],
            total_generated=result['total_generated'],
            json_file=latest_json
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Mood board generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Mood board generation failed: {str(e)}")


@app.post("/generate-media-plan", response_model=MediaPlanResponse)
async def generate_media_plan_endpoint(request: MediaPlanRequest):
    """
    Generate media planning recommendations
    
    Returns platform recommendations, posting times, content strategies,
    and growth tactics based on domain, audience, and competitors.
    """
    try:
        logger.info(f"Generating media plan for domain: {request.domain}")
        
        result = generate_media_plan(
            domain=request.domain,
            target_audience=request.target_audience,
            competitors=request.competitors
        )
        
        logger.info(f"Media plan generated: {len(result['recommended_platforms'])} platforms recommended")
        
        return MediaPlanResponse(
            status="success",
            recommended_platforms=result['recommended_platforms'],
            best_posting_times=result['best_posting_times'],
            content_types=result['content_types'],
            growth_strategies=result['growth_strategies'],
            mistakes_to_avoid=result['mistakes_to_avoid'],
            competitor_insights=result['competitor_insights'],
            metadata=result['metadata']
        )
        
    except Exception as e:
        logger.error(f"Media planning error: {e}")
        raise HTTPException(status_code=500, detail=f"Media planning failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
