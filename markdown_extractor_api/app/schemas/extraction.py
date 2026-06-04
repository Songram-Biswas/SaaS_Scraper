from pydantic import BaseModel, HttpUrl

class ExtractionRequest(BaseModel):
    url: HttpUrl

class ExtractionResponse(BaseModel):
    status: str
    markdown: str