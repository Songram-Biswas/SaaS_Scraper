# import traceback
# from curl_cffi import requests
# from playwright.async_api import async_playwright
# from readability import Document
# from markdownify import markdownify
# from bs4 import BeautifulSoup

# class MarkdownExtractor:
#     @staticmethod
#     async def _fetch_with_curl(url: str) -> str:
#         try:
#             response = requests.get(url, impersonate="chrome", timeout=10)
#             if response.status_code == 200:
#                 return response.text
#             print(f"[Curl Engine] Non-200 response status: {response.status_code}")
#             return ""
#         except Exception as e:
#             print(f"[Curl Engine] Exception: {e}")
#             return ""

#     @staticmethod
#     async def _fetch_with_playwright(url: str) -> str:
#         print(f"[Playwright Engine] Falling back to headless browser for: {url}")
#         try:
#             async with async_playwright() as p:
#                 browser = await p.chromium.launch(headless=True)
#                 context = await browser.new_context(
#                     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#                     viewport={"width": 1280, "height": 720}
#                 )
#                 page = await context.new_page()
                
#                 # Changed wait_until from "networkidle" to "domcontentloaded" to prevent infinite tracking script timeouts
#                 await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
#                 # Give dynamic elements an extra 2 seconds to render explicitly
#                 await page.wait_for_timeout(2000)
                
#                 html = await page.content()
#                 await browser.close()
#                 return html
#         except Exception as e:
#             print(f"[Playwright Engine] Crash or Timeout: {e}")
#             traceback.print_exc()
#             return ""

#     @staticmethod
#     def _is_javascript_heavy(html: str) -> bool:
#         if not html:
#             return True
#         soup = BeautifulSoup(html, "html.parser")
#         paragraphs = soup.find_all("p")
#         if len(paragraphs) < 2:
#             return True
#         text_content = soup.get_text().lower()
#         if "cloudflare" in text_content or "enable javascript" in text_content:
#             return True
#         return False

#     async def extract(self, url: str) -> dict:
#         html = await self._fetch_with_curl(url)
        
#         if self._is_javascript_heavy(html):
#             html = await self._fetch_with_playwright(url)
            
#         if not html:
#             return {"error": "Failed to retrieve content from the target URL. Both stealth request and browser fallback failed."}
            
#         try:
#             doc = Document(html)
#             title = doc.title()
#             summary_html = doc.summary()
#             markdown = markdownify(summary_html, heading_style="ATX").strip()
            
#             if not markdown or len(markdown.strip()) < 10:
#                 return {"error": "Content extracted was empty or completely unreadable layout."}
                
#             return {
#                 "title": title,
#                 "markdown": markdown,
#                 "url": url
#             }
#         except Exception as e:
#             return {"error": f"Parsing failed: {str(e)}"}
# # from curl_cffi import requests
# # from playwright.async_api import async_playwright
# # from readability import Document
# # from markdownify import markdownify
# # from bs4 import BeautifulSoup

# # class MarkdownExtractor:
# #     @staticmethod
# #     async def _fetch_with_curl(url: str) -> str:
# #         try:
# #             response = requests.get(url, impersonate="chrome", timeout=10)
# #             if response.status_code == 200:
# #                 return response.text
# #             return ""
# #         except Exception:
# #             return ""

# #     @staticmethod
# #     async def _fetch_with_playwright(url: str) -> str:
# #         try:
# #             async with async_playwright() as p:
# #                 browser = await p.chromium.launch(headless=True)
# #                 context = await browser.new_context(
# #                     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
# #                 )
# #                 page = await context.new_page()
# #                 await page.goto(url, wait_until="networkidle", timeout=30000)
# #                 html = await page.content()
# #                 await browser.close()
# #                 return html
# #         except Exception:
# #             return ""

# #     @staticmethod
# #     def _is_javascript_heavy(html: str) -> bool:
# #         if not html:
# #             return True
# #         soup = BeautifulSoup(html, "html.parser")
# #         paragraphs = soup.find_all("p")
# #         if len(paragraphs) < 2:
# #             return True
# #         text_content = soup.get_text().lower()
# #         if "cloudflare" in text_content or "enable javascript" in text_content:
# #             return True
# #         return False

# #     async def extract(self, url: str) -> dict:
# #         html = await self._fetch_with_curl(url)
        
# #         if self._is_javascript_heavy(html):
# #             html = await self._fetch_with_playwright(url)
            
# #         if not html:
# #             return {"error": "Failed to retrieve content from the target URL"}
            
# #         try:
# #             doc = Document(html)
# #             title = doc.title()
# #             summary_html = doc.summary()
# #             markdown = markdownify(summary_html, heading_style="ATX").strip()
# #             return {
# #                 "title": title,
# #                 "markdown": markdown,
# #                 "url": url
# #             }
# #         except Exception as e:
# #             return {"error": f"Parsing failed: {str(e)}"}

import traceback
import asyncio
from curl_cffi import requests
from playwright.async_api import async_playwright
from seleniumbase import Driver
from readability import Document
from markdownify import markdownify
from bs4 import BeautifulSoup

class MarkdownExtractor:
    
    @staticmethod
    async def _fetch_with_curl(url: str) -> str:
        print(f"--> [1/3] Trying CURL_CFFI (Fast/Stealth) for: {url}")
        try:
            response = requests.get(url, impersonate="chrome", timeout=10)
            if response.status_code == 200:
                print("    [+] CURL_CFFI returned a 200 OK response.")
                return response.text
            print(f"    [-] CURL_CFFI Failed (Status: {response.status_code})")
            return ""
        except Exception as e:
            print(f"    [-] CURL_CFFI Exception: {e}")
            return ""

    @staticmethod
    async def _fetch_with_playwright(url: str) -> str:
        print(f"--> [2/3] Trying PLAYWRIGHT (Headless Browser) for: {url}")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720}
                )
                page = await context.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(2000)
                html = await page.content()
                await browser.close()
                print("    [+] PLAYWRIGHT returned page content.")
                return html
        except Exception as e:
            print(f"    [-] PLAYWRIGHT Failed/Timeout: {e}")
            return ""

    @staticmethod
    def _run_seleniumbase_sync(url: str) -> str:
        driver = None
        try:
            driver = Driver(uc=True, headless=True)
            driver.get(url)
            driver.sleep(4)
            html = driver.page_source
            driver.quit()
            return html
        except Exception as e:
            print(f"    [-] SELENIUMBASE Internal Error: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            return ""

    @staticmethod
    async def _fetch_with_seleniumbase(url: str) -> str:
        print(f"--> [3/3] Trying SELENIUMBASE (UC Mode / Max Stealth) for: {url}")
        try:
            html = await asyncio.to_thread(MarkdownExtractor._run_seleniumbase_sync, url)
            if html:
                print("    [+] SELENIUMBASE returned page content.")
            else:
                print("    [-] SELENIUMBASE returned empty HTML.")
            return html
        except Exception as e:
            print(f"    [-] SELENIUMBASE Failed: {e}")
            return ""

    @staticmethod
    def _is_bot_blocked(html: str) -> bool:
        if not html or len(html.strip()) < 500:
            return True
            
        text_content = html.lower()
        block_signals = [
            "cloudflare", 
            "captcha-delivery", 
            "checking your browser", 
            "just a moment...", 
            "enable javascript",
            "access denied",
            "security check"
        ]
        
        for signal in block_signals:
            if signal in text_content:
                return True
                
        return False

    async def extract(self, url: str) -> dict:
        print(f"\n========== STARTING EXTRACTION: {url} ==========")
        
        html = await self._fetch_with_curl(url)
        
        if self._is_bot_blocked(html):
            print("    [!] Content blocked or unrendered. Escalating to PLAYWRIGHT...")
            html = await self._fetch_with_playwright(url)
            
            if self._is_bot_blocked(html):
                print("    [!] Still hitting an anti-bot wall. Escalating to MAX STEALTH (SeleniumBase)...")
                html = await self._fetch_with_seleniumbase(url)
        
        if not html or self._is_bot_blocked(html):
            print("========== EXTRACTION FAILED (All methods blocked) ==========\n")
            return {"error": "Failed to retrieve content. Target has extreme anti-bot protection or requires login."}
            
        print("    [*] Engine Success. Parsing HTML to clean Markdown...")
        try:
            doc = Document(html)
            title = doc.title()
            summary_html = doc.summary()
            markdown = markdownify(summary_html, heading_style="ATX").strip()
            
            if not markdown or len(markdown.strip()) < 10:
                print("========== EXTRACTION FAILED (Empty Markdown) ==========\n")
                return {"error": "Content extracted was empty or completely unreadable layout."}
                
            print("========== EXTRACTION COMPLETE ==========\n")
            return {
                "title": title,
                "markdown": markdown,
                "url": url
            }
        except Exception as e:
            print("========== EXTRACTION FAILED (Parse Error) ==========\n")
            return {"error": f"Parsing failed: {str(e)}"}