import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.constants import (
    EVENTBRITE_BASE_URL,
    EVENT_CARD_SELECTOR,
    OUTPUT_CSV,
    OUTPUT_JSON,
    WAIT_TIME,
)
from utils.helpers import export_to_csv, export_to_json, parse_event_card


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Eventbrite Adelaide events")
    parser.add_argument("--pages", type=int, default=1,
                        help="Pages to scrape (default: 1)")
    args = parser.parse_args()

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=opts)

    events, seen = [], set()
    try:
        for page in range(1, args.pages + 1):
            url = EVENTBRITE_BASE_URL.format(page=page)
            print(f"\nLoading: {url}")
            driver.get(url)

            # Wait until at least one card is present or timeout (10s)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, EVENT_CARD_SELECTOR))
                )
            except Exception:
                # Save page for inspection on failures
                with open(f"debug_page_{page}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"No cards found. Saved debug_page_{page}.html")
                continue

            cards = driver.find_elements(By.CSS_SELECTOR, EVENT_CARD_SELECTOR)
            print(f"Found {len(cards)} cards")

            for c in cards:
                data = parse_event_card(c, driver, seen)
                if data:
                    print(f"{data['Title']}")
                    events.append(data)

    finally:
        driver.quit()

    if events:
        export_to_csv(events, OUTPUT_CSV)
        export_to_json(events, OUTPUT_JSON)
        print(
            f"\nScraped {len(events)} events\n- {OUTPUT_CSV}\n- {OUTPUT_JSON}")
    else:
        print("\nNo events scraped. Check selectors or debug_page_*.html.")


if __name__ == "__main__":
    main()
