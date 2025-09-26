import requests
from bs4 import BeautifulSoup
import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "experienceadelaide.json")


def scrape_experienceadelaide():
    base_url = "https://www.experienceadelaide.com.au"
    list_url = f"{base_url}/visit/whats-on/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                      "Version/16.4 Safari/605.1.15"
    }

    # Step 1: Fetch listing page
    resp = requests.get(list_url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    events = []

    # Step 2: Loop over event cards
    for card in soup.select("div.event-card a"):  # updated selector
        link = card.get("href")
        if not link.startswith("http"):
            link = base_url + link

        title = card.get_text(strip=True)

        # Step 3: Visit each event detail page
        try:
            detail_resp = requests.get(link, headers=headers)
            detail_resp.raise_for_status()
            detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

            date = detail_soup.select_one("p.event-datetime")
            date = date.get_text(strip=True) if date else None

            description = detail_soup.select_one(".card-body")
            description = description.get_text(strip=True) if description else None

            location = None
            for p in detail_soup.select("p"):
                if "Adelaide" in p.get_text():
                    location = p.get_text(strip=True)
                    break

            events.append({
                "title": title,
                "date": date,
                "location": location,
                "description": description,
                "link": link
            })

        except Exception as e:
            print(f"⚠️ Failed to scrape {link}: {e}")

    # Step 4: Save JSON
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"🎉 Scraped {len(events)} events from ExperienceAdelaide")
    return events


if __name__ == "__main__":
    scrape_experienceadelaide()
