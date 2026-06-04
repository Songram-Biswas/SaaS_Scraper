# import sys
# import asyncio
# from fastapi import FastAPI
# from app.api import routes

# # --- Windows specific fix for Playwright subprocesses ---
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# # --------------------------------------------------------

# app = FastAPI(
#     title="Universal URL to Markdown Extractor API",
#     version="1.0.0",
#     docs_url="/docs"
# )

# app.include_router(routes.router)

# @app.get("/")
# def read_root():
#     return {"status": "online", "service": "Markdown Extractor API"}
# import sys
# import asyncio
# from fastapi import FastAPI
# from app.api.endpoints import auth, extract

# # --- Windows specific fix for Playwright subprocesses ---
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# # --------------------------------------------------------

# app = FastAPI(
#     title="Markdown Extractor API SaaS",
#     version="1.0.0",
#     docs_url="/docs"
# )

# # Register our new Authentication and Key Generation routes
# app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# @app.get("/")
# def read_root():
#     return {"status": "online", "service": "Markdown Extractor API SaaS"}

#this version works fine completely api key generation and scraping
# import sys
# import asyncio
# from fastapi import FastAPI
# from app.api.endpoints import auth, extract

# # --- Windows specific fix for Playwright subprocesses ---
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# # --------------------------------------------------------

# app = FastAPI(
#     title="Markdown Extractor API SaaS",
#     version="1.0.0",
#     docs_url="/docs"
# )

# # Register the Authentication and Extraction routes
# app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# app.include_router(extract.router, prefix="/extract", tags=["Extraction"])

# @app.get("/")
# def read_root():
#     return {"status": "online", "service": "Markdown Extractor API SaaS"}

import sys
import asyncio
from fastapi import FastAPI
from app.api.endpoints import auth, extract, webhooks

# --- Windows specific fix for Playwright subprocesses ---
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# --------------------------------------------------------

app = FastAPI(
    title="Markdown Extractor API SaaS",
    version="1.0.0",
    docs_url="/docs"
)

# Register all routing pipelines
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(extract.router, prefix="/extract", tags=["Extraction"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Payments"])

@app.get("/")
def read_root():
    return {"status": "online", "service": "Markdown Extractor API SaaS"}