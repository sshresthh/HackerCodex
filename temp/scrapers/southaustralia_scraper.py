import requests
from bs4 import BeautifulSoup
import json
import os

# File where scraped events will be saved
DATA_PATH = os.path.join(os.path.dirname(
    __file__), "data", "southaustralia.json")

URL = "https://southaustralia.com/destinations/adelaide/what-s-on"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def scrape_southaustralia(limit: int = 50):
    """
    Scrape events from SouthAustralia.com (What's On Adelaide).
    Saves results into data/southaustralia.json
    """
    resp = requests.get(URL, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    events = []
    for card in soup.select("div.product-card__content")[:limit]:
        title = card.select_one("h4.product-card__title")
        title = title.get_text(strip=True) if title else None

        location = card.select_one("span.product-card__location")
        location = location.get_text(strip=True) if location else None

        price = card.select_one("span.product-card__price")
        price = price.get_text(strip=True) if price else None

        footer = card.select_one(
            "footer.product-card__footer div.product-card__info")
        date_info = footer.get_text(" ", strip=True) if footer else None

        features = [li.get_text(strip=True)
                    for li in card.select("ul.product-card__features li")]

        # --- Extract event detail link ---
        link_tag = card.find_parent("a")
        link = link_tag.get("href") if link_tag else None
        if link and not link.startswith("http"):
            link = "https://southaustralia.com" + link

        # --- Go into detail page to fetch full address ---
        full_address = None
        if link:
            try:
                detail_resp = requests.get(link, headers=HEADERS)
                detail_resp.raise_for_status()
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

                addr_tag = detail_soup.select_one("#contactAddress span")
                if addr_tag:
                    full_address = addr_tag.get_text(strip=True)

            except Exception as e:
                print(f"Failed to fetch detail page {link}: {e}")

        events.append({
            "title": title,
            "location": location,
            "price": price,
            "dates": date_info,
            "features": features,
            "full_address": full_address,
            "link": link,
        })

    # Save to JSON file
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"Scraped {len(events)} events from SouthAustralia.com")
    return events


if __name__ == "__main__":
    scrape_southaustralia()
