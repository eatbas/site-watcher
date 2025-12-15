"""
Playwright-based scraper for PTT announcements
"""
import asyncio
from typing import List, Dict
from playwright.async_api import async_playwright, Page


class PTTScraper:
    """Scraper for PTT announcement pages using Playwright"""
    
    BASE_URL = "https://www.ptt.gov.tr/duyurular"
    
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def scrape_announcements(self, page_num: int = 1, announcement_type: int = 3) -> List[Dict]:
        """
        Scrape announcements from PTT website
        
        Args:
            page_num: Page number to scrape
            announcement_type: Type of announcements (3 = İhale Duyuruları)
        
        Returns:
            List of announcement dictionaries with title, date_text, and link
        """
        url = f"{self.BASE_URL}?page={page_num}&announcementType={announcement_type}"
        announcements = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                locale="tr-TR"
            )
            page = await context.new_page()
            
            try:
                # Navigate to the page
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Handle cookie consent if present
                await self._handle_cookie_consent(page)
                
                # Wait for announcements to load
                await page.wait_for_selector('a[href*="/duyuru/"]', timeout=10000)
                
                # Extract announcements
                announcements = await self._extract_announcements(page)
                
            except Exception as e:
                print(f"Error scraping page: {e}")
                raise
            finally:
                await browser.close()
        
        return announcements

    async def _handle_cookie_consent(self, page: Page):
        """Handle the cookie consent popup if present"""
        try:
            # Look for the "Anladım" button
            consent_button = page.locator('button:has-text("Anladım")')
            if await consent_button.count() > 0:
                await consent_button.click()
                await page.wait_for_timeout(500)  # Wait for popup to close
        except Exception:
            # Cookie consent might not be present, continue
            pass

    async def _extract_announcements(self, page: Page) -> List[Dict]:
        """Extract announcement data from the page"""
        announcements = []
        
        # Find all announcement links
        announcement_links = await page.query_selector_all('a[href*="/duyuru/"]')
        
        for link_element in announcement_links:
            try:
                href = await link_element.get_attribute("href")
                
                # Skip if this is not a valid announcement link
                if not href or "/duyuru/" not in href:
                    continue
                
                # Get the parent container to extract date and title
                parent = await link_element.evaluate_handle("el => el.parentElement.parentElement")
                parent_text = await parent.evaluate("el => el.innerText")
                
                # Parse the text content
                lines = [line.strip() for line in parent_text.split('\n') if line.strip()]
                
                # Extract date parts and title
                date_text = ""
                title = ""
                
                # Look for date pattern (day, month, year on separate lines or together)
                for i, line in enumerate(lines):
                    # Check if this looks like a day number
                    if line.isdigit() and 1 <= int(line) <= 31:
                        # Next lines should be month and year
                        if i + 2 < len(lines):
                            month = lines[i + 1]
                            year = lines[i + 2] if lines[i + 2].isdigit() else ""
                            date_text = f"{line} {month} {year}".strip()
                            # Title should be after the date
                            if i + 3 < len(lines):
                                title = lines[i + 3]
                        break
                
                # Fallback: if we didn't find structured data, use the link text
                if not title:
                    title = await link_element.inner_text()
                    if title.lower() in ["daha fazla oku", "read more"]:
                        # Get text from parent
                        title = lines[0] if lines else ""
                
                # Construct full URL
                full_link = f"https://www.ptt.gov.tr{href}" if href.startswith("/") else href
                
                if title and title.lower() not in ["daha fazla oku", "read more"]:
                    announcements.append({
                        "title": title,
                        "date_text": date_text,
                        "link": full_link,
                    })
                    
            except Exception as e:
                print(f"Error extracting announcement: {e}")
                continue
        
        # Remove duplicates based on link
        seen_links = set()
        unique_announcements = []
        for ann in announcements:
            if ann["link"] not in seen_links:
                seen_links.add(ann["link"])
                unique_announcements.append(ann)
        
        return unique_announcements


def scrape_sync(page_num: int = 1, announcement_type: int = 3, headless: bool = True) -> List[Dict]:
    """Synchronous wrapper for the scraper"""
    scraper = PTTScraper(headless=headless)
    return asyncio.run(scraper.scrape_announcements(page_num, announcement_type))


if __name__ == "__main__":
    # Test the scraper
    announcements = scrape_sync(headless=False)
    print(f"Found {len(announcements)} announcements:")
    for ann in announcements:
        print(f"  - {ann['date_text']}: {ann['title']}")
        print(f"    Link: {ann['link']}")
