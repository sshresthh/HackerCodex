# HackerCodex Event Scrapers

This module contains scrapers for pulling event data from different Adelaide event sources.  
Each scraper saves results as JSON (and CSV for Eventbrite) under `backend/scrapers/data/`.

---

## 📂 Available Scrapers

- `eventbrite_scraper.py` → Eventbrite events (saves `eventbrite.json` + `eventbrite.csv`)
- `experienceadelaide_scraper.py` → Events from [Experience Adelaide](https://www.experienceadelaide.com.au/visit/whats-on/)
- `adelaidefestival_scraper.py` → Events from [Adelaide Festival Centre](https://www.adelaidefestivalcentre.com.au/whats-on)
- `southaustralia_scraper.py` → Events from [South Australia Tourism](https://southaustralia.com/events)
- `google_events_scraper.py` → Google Events (via [SerpAPI](https://serpapi.com/google-events))

---

## ⚙️ Setup

1. Create and activate virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

## 📂 Install dependencies:
pip install -r requirements.txt

## (Optional) Create .env in project root for SerpAPI:
SERPAPI_KEY=your_api_key_here

## Each scraper is run from inside the backend/scrapers directory:
cd backend/scrapers
python eventbrite_scraper.py
python experienceadelaide_scraper.py
python adelaidefestival_scraper.py
python southaustralia_scraper.py
python google_events_scraper.py

## Outputs
Scraped data will be saved into:
backend/scrapers/data/eventbrite.json
backend/scrapers/data/eventbrite.csv
backend/scrapers/data/experienceadelaide.json
backend/scrapers/data/adelaidefestival.json
backend/scrapers/data/southaustralia.json
backend/scrapers/data/google_events.json