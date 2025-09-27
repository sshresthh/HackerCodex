import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Save inside backend/scrapers/data/
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "ticketmaster.json")

def fetch_ticketmaster_events(debug=False):
    """Fetch Adelaide events from Ticketmaster Discovery API."""
    api_key = os.getenv("TICKETMASTER_API_KEY")
    
    if not api_key:
        print("TICKETMASTER_API_KEY not found in environment variables")
        return []
    
    print("Fetching Adelaide events from Ticketmaster Discovery API...")
    
    # Base API endpoint
    base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
    
    # Parameters for Adelaide, Australia events
    params = {
        "apikey": api_key,
        "city": "Adelaide",
        "countryCode": "AU",
        "size": 100,  # Max events per request
        "page": 0,
        "sort": "date,asc",  # Sort by date ascending
        "startDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),  # Only future events
        "endDateTime": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")  # Next year
    }
    
    all_events = []
    max_pages = 5  # Limit to avoid too many API calls
    
    try:
        for page in range(max_pages):
            params["page"] = page
            
            print(f"Fetching page {page + 1}...")
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"API error: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            
            # Check if we have events
            if "_embedded" not in data or "events" not in data["_embedded"]:
                print(f"No events found on page {page + 1}")
                break
            
            events = data["_embedded"]["events"]
            print(f"Found {len(events)} events on page {page + 1}")
            
            for event in events:
                try:
                    # Debug: Print first event structure to understand available fields
                    if debug and page == 0 and events.index(event) == 0:
                        print("\nDEBUG: First event structure:")
                        import json as json_debug
                        print(json_debug.dumps(event, indent=2)[:2000] + "...")
                        print("DEBUG: Available top-level keys:", list(event.keys()))
                        if "_embedded" in event:
                            print("DEBUG: Embedded keys:", list(event["_embedded"].keys()))
                    
                    # Extract event details
                    event_data = {
                        "title": event.get("name", ""),
                        "date": "",
                        "time": "",
                        "location": "",
                        "venue": "",
                        "description": "",
                        "organizer": "",
                        "link": event.get("url", ""),
                        "price_range": "",
                        "category": "",
                        "image": ""
                    }
                    
                    # Extract description from multiple possible fields
                    description_parts = []
                    if event.get("info"):
                        description_parts.append(event["info"])
                    if event.get("pleaseNote"):
                        description_parts.append(f"Please note: {event['pleaseNote']}")
                    if event.get("additionalInfo"):
                        description_parts.append(event["additionalInfo"])
                    event_data["description"] = " | ".join(description_parts)
                    
                    # Extract organizer/promoter information
                    organizer_parts = []
                    if "promoter" in event:
                        if isinstance(event["promoter"], dict):
                            organizer_parts.append(event["promoter"].get("name", ""))
                        elif isinstance(event["promoter"], list) and event["promoter"]:
                            organizer_parts.append(event["promoter"][0].get("name", ""))
                    
                    # Check for organizer in embedded data
                    if "_embedded" in event:
                        if "venues" in event["_embedded"] and event["_embedded"]["venues"]:
                            venue_data = event["_embedded"]["venues"][0]
                            if "boxOfficeInfo" in venue_data:
                                box_office = venue_data["boxOfficeInfo"]
                                if "openHoursDetail" in box_office:
                                    organizer_parts.append(f"Box Office: {box_office['openHoursDetail']}")
                        
                        # Look for promoter in embedded attractions
                        if "attractions" in event["_embedded"]:
                            for attraction in event["_embedded"]["attractions"]:
                                if attraction.get("name") and attraction["name"] not in event_data["title"]:
                                    organizer_parts.append(f"Featuring: {attraction['name']}")
                    
                    event_data["organizer"] = " | ".join(filter(None, organizer_parts))
                    
                    # Parse date and time
                    if "dates" in event and "start" in event["dates"]:
                        start_date = event["dates"]["start"]
                        if "localDate" in start_date:
                            event_data["date"] = start_date["localDate"]
                        if "localTime" in start_date:
                            event_data["time"] = start_date["localTime"]
                    
                    # Parse venue information
                    if "_embedded" in event and "venues" in event["_embedded"]:
                        venue = event["_embedded"]["venues"][0]
                        event_data["venue"] = venue.get("name", "")
                        
                        # Build location string
                        location_parts = []
                        if "address" in venue:
                            address = venue["address"]
                            if "line1" in address:
                                location_parts.append(address["line1"])
                        if "city" in venue:
                            location_parts.append(venue["city"]["name"])
                        if "state" in venue:
                            location_parts.append(venue["state"]["name"])
                        
                        event_data["location"] = ", ".join(location_parts)
                    
                    # Parse price range
                    if "priceRanges" in event and event["priceRanges"]:
                        price_range = event["priceRanges"][0]
                        min_price = price_range.get("min", 0)
                        max_price = price_range.get("max", 0)
                        currency = price_range.get("currency", "AUD")
                        
                        if min_price == max_price:
                            event_data["price_range"] = f"{currency} {min_price}"
                        else:
                            event_data["price_range"] = f"{currency} {min_price} - {max_price}"
                    
                    # Parse category/classification
                    if "classifications" in event and event["classifications"]:
                        classification = event["classifications"][0]
                        categories = []
                        if "segment" in classification:
                            categories.append(classification["segment"]["name"])
                        if "genre" in classification:
                            categories.append(classification["genre"]["name"])
                        event_data["category"] = " / ".join(categories)
                    
                    # Parse image
                    if "images" in event and event["images"]:
                        # Get the largest image
                        images = sorted(event["images"], key=lambda x: x.get("width", 0), reverse=True)
                        event_data["image"] = images[0]["url"]
                    
                    # Only add events with required fields
                    if event_data["title"] and event_data["link"]:
                        all_events.append(event_data)
                
                except Exception as e:
                    print(f"Error processing event: {e}")
                    continue
            
            # Check if we have more pages
            page_info = data.get("page", {})
            total_pages = page_info.get("totalPages", 1)
            
            if page + 1 >= total_pages:
                print(f"Reached last page ({total_pages} total pages)")
                break
    
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
    
    # Save results
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)
    
    print(f"Scraped {len(all_events)} events from Ticketmaster (Adelaide)")
    
    # Show sample events
    if all_events:
        print("\n Sample events:")
        for i, event in enumerate(all_events[:3]):
            print(f"  {i+1}. {event['title']}")
            print(f"     {event['date']} {event['time']}")
            print(f"     {event['venue']}")
            print(f"     {event['price_range']}")
            print(f"     {event['category']}")
            print()
    
    return all_events

if __name__ == "__main__":
    import sys
    debug_mode = "--debug" in sys.argv
    fetch_ticketmaster_events(debug=debug_mode)
