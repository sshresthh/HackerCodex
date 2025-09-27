import time
import json
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
import os


def parse_event_card(card: WebElement, driver: WebDriver, seen_titles: set[str]):
    """
    Parse one Eventbrite card with deep scrape for Location, Date/Time, Organizer.
    """
    try:
        # --- Title + URL from card ---
        anchor = card.find_element(By.TAG_NAME, "a")
        url = anchor.get_attribute("href")
        title = anchor.get_attribute("aria-label") or anchor.text.strip()

        if not title or title in seen_titles:
            return None
        seen_titles.add(title)

        # --- Open detail page ---
        driver.execute_script("window.open(arguments[0]);", url)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)  # wait for detail page to load

        # --- Location ---
        try:
            location = driver.find_element(By.CSS_SELECTOR, "div[data-testid='location']").text.strip()
        except:
            location = "Unknown"

        # --- Date & Time ---
        try:
            date_time = driver.find_element(By.CSS_SELECTOR, "div[data-testid='dateAndTime']").text.strip()
        except:
            date_time = "TBD"

        # --- Organizer ---
        try:
            organizer = driver.find_element(
                By.CSS_SELECTOR,
                "div[data-testid='organizerBrief'] strong.organizer-info__name-link"
            ).text.strip()
        except:
            organizer = "Unknown"

        # TODO: Category can be added later if needed
        category = ""

        # Close tab and return to listing
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        return {
            "Title": title,
            "URL": url,
            "Date & Time": date_time,
            "Location": location,
            "Category": category,
            "Organizer": organizer,
            "Source": "Eventbrite",
        }

    except Exception as e:
        print(f"⚠️ Failed to parse a card: {e}")
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return None


def export_to_csv(events: list[dict[str, str]], filename: str) -> None:
    """Save scraped events to CSV (without pandas)."""
    if not events:
        print("⚠️ No events to save to CSV.")
        return
    fieldnames = sorted({k for e in events for k in e.keys()})
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in events:
            writer.writerow(e)
    print(f"💾 Saved {len(events)} events to {filename}")


def export_to_json(events: list[dict[str, str]], filename: str) -> None:
    """Save scraped events to JSON (without pandas)."""
    if not events:
        print("⚠️ No events to save to JSON.")
        return
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=4, ensure_ascii=False)
    print(f"💾 Saved {len(events)} events to {filename}")

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
