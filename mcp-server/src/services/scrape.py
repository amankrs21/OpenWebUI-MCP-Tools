from __future__ import annotations


import httpx
from selectolax.parser import HTMLParser
from typing import Any, Dict, List, Optional


class ScrapeService:
    async def quick_scrape(
        self, url: str, css: Optional[str] = None, xpath: Optional[str] = None
    ) -> Dict[str, Any] | List[str]:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with httpx.AsyncClient(http2=True, timeout=15.0) as client:
            resp = await client.get(url, headers=headers, follow_redirects=True)

            if resp.status_code >= 400:
                return {"error": resp.status_code, "url": url}

            tree = HTMLParser(resp.text)

            if css:
                return [node.text(strip=True) for node in tree.css(css)]
            if xpath:
                return [node.text(strip=True) for node in tree.xpath(xpath)]

            title_node = tree.css_first("title")
            return {"title": title_node.text(strip=True) if title_node else None}

    async def robust_scrape(
        self, url: str, wait_for: Optional[str] = None, timeout: int = 45000
    ) -> Dict[str, Any]:
        try:
            from playwright.async_api import async_playwright, BrowserContext
        except Exception as exc:
            return {
                "error": "Playwright not installed. Install playwright to use robust_scrape.",
                "details": str(exc),
                "url": url,
                "success": False,
            }

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context: BrowserContext = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                ),
                locale="en-US",
                timezone_id="Asia/Kolkata",
                java_script_enabled=True,
                bypass_csp=True,
            )

            page = await context.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                if wait_for:
                    await page.wait_for_selector(wait_for, timeout=15000)

                content = await page.content()
                title = await page.title()
                return {
                    "url": page.url,
                    "title": title,
                    "html": content[:200000],
                    "success": True,
                }
            except Exception as exc:
                return {"error": str(exc), "url": url, "success": False}
            finally:
                await context.close()
                await browser.close()

    def impersonate_scrape(self, url: str) -> Dict[str, Any]:
        try:
            from curl_cffi import requests as curl_requests
            from parsel import Selector
        except Exception as exc:
            return {
                "error": "curl_cffi/parsel not installed. Install them to use impersonate_scrape.",
                "details": str(exc),
                "url": url,
            }

        session = curl_requests.Session(impersonate="chrome131")
        resp = session.get(url, timeout=12)
        if resp.status_code != 200:
            return {"error": resp.status_code, "url": url}

        sel = Selector(resp.text)
        return {
            "title": sel.xpath("//title/text()").get(),
            "h1": sel.xpath("//h1//text()").getall(),
            "price": sel.css(".price::text").get(),
            "raw": resp.text[:5000],
        }
