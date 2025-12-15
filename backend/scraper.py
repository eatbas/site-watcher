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
                
                # Wait for page content to load - use a more general selector
                await page.wait_for_timeout(2000)  # Give JS time to render
                
                # Try multiple selectors for announcements
                selectors_to_try = [
                    'a[aria-label^="Daha Fazla Oku"]',
                    'a[href*="/duyuru/"]',
                    'a:has-text("Daha Fazla Oku")',
                ]
                
                found = False
                for selector in selectors_to_try:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        found = True
                        break
                    except Exception:
                        continue
                
                if not found:
                    # Try to extract from page anyway
                    print("Warning: No standard selectors found, attempting extraction anyway")
                
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
            # Look for the "Anladım" button with multiple strategies
            consent_selectors = [
                'button:has-text("Anladım")',
                'button.cookie-consent-button',
                '[data-testid="cookie-accept"]',
            ]
            
            for selector in consent_selectors:
                try:
                    consent_button = page.locator(selector)
                    if await consent_button.count() > 0:
                        await consent_button.first.click()
                        await page.wait_for_timeout(1000)  # Wait for popup to close
                        return
                except Exception:
                    continue
        except Exception:
            # Cookie consent might not be present, continue
            pass

    async def _extract_announcements(self, page: Page) -> List[Dict]:
        """Extract announcement data from the page"""
        announcements = []
        
        # Try multiple selector strategies
        link_elements = []
        
        # Strategy 1: aria-label based selector
        try:
            link_elements = await page.query_selector_all('a[aria-label^="Daha Fazla Oku"]')
        except Exception:
            pass
        
        # Strategy 2: href based selector
        if not link_elements:
            try:
                link_elements = await page.query_selector_all('a[href*="/duyuru/"]')
            except Exception:
                pass
        
        # Strategy 3: text based selector
        if not link_elements:
            try:
                link_elements = await page.query_selector_all('a:has-text("Daha Fazla Oku")')
            except Exception:
                pass
        
        print(f"Found {len(link_elements)} announcement links")
        
        for link_element in link_elements:
            try:
                href = await link_element.get_attribute("href")
                aria_label = await link_element.get_attribute("aria-label")
                
                # Skip if this is not a valid announcement link
                if not href:
                    continue
                
                # Extract title from aria-label if available
                title = ""
                if aria_label and aria_label.startswith("Daha Fazla Oku - "):
                    title = aria_label.replace("Daha Fazla Oku - ", "").strip()
                
                # Get date from parent container
                date_text = ""
                try:
                    # Navigate up to find the container with date info
                    parent = await link_element.evaluate_handle("el => el.closest('div') || el.parentElement.parentElement")
                    parent_text = await parent.evaluate("el => el.innerText")
                    
                    # Parse the text content
                    lines = [line.strip() for line in parent_text.split('\n') if line.strip()]
                    
                    # Look for date pattern (day, month, year)
                    for i, line in enumerate(lines):
                        # Check if this looks like a day number
                        if line.isdigit() and 1 <= int(line) <= 31:
                            # Next lines should be month and year
                            if i + 2 < len(lines):
                                month = lines[i + 1]
                                year = lines[i + 2] if lines[i + 2].isdigit() else ""
                                date_text = f"{line} {month} {year}".strip()
                            break
                    
                    # If no title from aria-label, try to extract from parent text
                    if not title:
                        for line in lines:
                            if line and line not in ["İlan Tarihi", "Daha Fazla Oku"] and not line.isdigit():
                                # Skip Turkish month names
                                if line not in ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
                                               "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]:
                                    title = line
                                    break
                                    
                except Exception as e:
                    print(f"Error getting parent info: {e}")
                
                # Fallback title
                if not title:
                    title = await link_element.inner_text()
                    if title.lower() in ["daha fazla oku", "read more"]:
                        title = href.split("/")[-1].replace("-", " ").title() if href else "Unknown"
                
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
        
        print(f"Extracted {len(unique_announcements)} unique announcements")
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
