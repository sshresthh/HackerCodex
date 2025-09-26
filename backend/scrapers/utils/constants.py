import os
from dotenv import load_dotenv

load_dotenv()

# Page & timing
EVENTBRITE_BASE_URL = "https://www.eventbrite.com/d/australia--adelaide/all-events/?page={page}"
WAIT_TIME = 5  # JS-heavy; with WebDriverWait we still keep a small base wait

# Robust selectors for the current layout
# Each card has this attribute in your HTML
EVENT_CARD_SELECTOR = "[data-testid='search-event']"
# Anchor inside the card; aria-label holds the title
ANCHOR_SELECTOR = "a.event-card__link"
# Two lines inside the card: [0] date/time, [1] location
CLAMP_PARAGRAPH_SELECTOR = "p.event-card__clamp-line"

# Outputs (always write into backend/scrapers/data/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_CSV = os.path.join(DATA_DIR, "eventbrite.csv")
OUTPUT_JSON = os.path.join(DATA_DIR, "eventbrite.json")

FACEBOOK_OUTPUT_JSON = "backend/scrapers/data/facebook.json"

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")

# Existing constants...

SOUTH_AUSTRALIA_BASE_URL = "https://southaustralia.com/destinations/adelaide/what-s-on"


