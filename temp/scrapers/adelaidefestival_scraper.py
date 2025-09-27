import os
import json
import requests
from bs4 import BeautifulSoup
import time

DATA_PATH = os.path.join(os.path.dirname(
    __file__), "data", "adelaidefestival.json")
BASE_URL = "https://www.adelaidefestivalcentre.com.au"


def scrape_adelaidefestival():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                      "Version/16.4 Safari/605.1.15"
    }

    events = []
    page_url = f"{BASE_URL}/whats-on"

    while page_url:
        print(f"Fetching {page_url}")
        resp = requests.get(page_url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract event cards
        for card in soup.select("a.card__link"):
            link = card.get("href")
            if not link:
                continue
            if not link.startswith("http"):
                link = BASE_URL + link

            # Visit detail page for full info
            try:
                detail_resp = requests.get(link, headers=headers)
                detail_resp.raise_for_status()
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

                title_el = detail_soup.select_one("h1")
                title = title_el.get_text(strip=True) if title_el else None

                date_el = detail_soup.select_one(".event-date, time, .date")
                date = date_el.get_text(strip=True) if date_el else None

                desc_el = detail_soup.select_one(".event-description, .rte, p")
                description = desc_el.get_text(
                    " ", strip=True) if desc_el else None

                address = None
                addr_el = detail_soup.find("address") or detail_soup.select_one(
                    ".event-location, .venue, .location")
                if addr_el:
                    address = addr_el.get_text(" ", strip=True)

                events.append({
                    "title": title,
                    "date": date,
                    "description": description,
                    "address": address,
                    "link": link
                })

                print(f"{title} ({date})")

                time.sleep(0.5)  # politeness delay to reduce load

            except Exception as e:
                print(f"Failed to scrape {link}: {e}")

        # Pagination
        next_btn = soup.select_one("nav[aria-label=Pagination] a[rel=next]")
        if next_btn:
            page_url = BASE_URL + next_btn["href"]
        else:
            page_url = None

    # Save JSON
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"Scraped {len(events)} events from Adelaide Festival Centre")
    return events


if __name__ == "__main__":
    scrape_adelaidefestival()
