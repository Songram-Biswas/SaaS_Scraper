from fastapi import APIRouter, Depends
from app.api.deps import validate_api_key
from app.schemas.extraction import ExtractionRequest, ExtractionResponse
from app.services.extractor import MarkdownExtractor

router = APIRouter()

# The Depends(validate_api_key) is the lock on the door!
@router.post("/", response_model=ExtractionResponse)
async def extract_markdown(
    payload: ExtractionRequest,
    api_key=Depends(validate_api_key) 
):
    extractor = MarkdownExtractor()
    
    # We pass the URL to your engine (it expects a string, so we convert the HttpUrl object)
    result = await extractor.extract(str(payload.url))
    
    # If your engine caught an anti-bot error, return it gracefully
    if "error" in result:
        return {"status": "error", "markdown": result["error"]}
        
    return {"status": "success", "markdown": result["markdown"]}