import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# 1. Define the realistic browser headers
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}

class MarkdownExtractor:
    async def extract(self, url: str) -> dict:
        try:
            # 2. Inject the headers into the httpx client
            async with httpx.AsyncClient(headers=BROWSER_HEADERS, timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                html_content = response.text

            soup = BeautifulSoup(html_content, "html.parser")
            for element in soup(["script", "style", "nav", "footer", "iframe"]):
                element.decompose()

            cleaned_html = str(soup)
            markdown_content = md(cleaned_html, heading_style="ATX").strip()

            if not markdown_content:
                return {"error": "Could not extract meaningful text from this URL."}

            return {"markdown": markdown_content}

        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP Error {e.response.status_code} while fetching the URL."}
        except Exception as e:
            return {"error": f"Extraction failed: {str(e)}"}
# import httpx
# from bs4 import BeautifulSoup
# from markdownify import markdownify as md

# class MarkdownExtractor:
#     async def extract(self, url: str) -> dict:
#         try:
#             async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
#                 response = await client.get(url)
#                 response.raise_for_status()
#                 html_content = response.text

#             soup = BeautifulSoup(html_content, "html.parser")
#             for element in soup(["script", "style", "nav", "footer", "iframe"]):
#                 element.decompose()

#             cleaned_html = str(soup)
#             markdown_content = md(cleaned_html, heading_style="ATX").strip()

#             if not markdown_content:
#                 return {"error": "Could not extract meaningful text from this URL."}

#             return {"markdown": markdown_content}

#         except httpx.HTTPStatusError as e:
#             return {"error": f"HTTP Error {e.response.status_code} while fetching the URL."}
#         except Exception as e:
#             return {"error": f"Extraction failed: {str(e)}"}
