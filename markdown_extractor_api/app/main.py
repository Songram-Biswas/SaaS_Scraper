from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, extract, webhooks

app = FastAPI(title="Markdown Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(extract.router, prefix="/api", tags=["Extraction"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])