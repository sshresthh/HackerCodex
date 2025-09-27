## Inspiration
Our inspiration comes from a common Adelaide paradox: South Australia is officially "The Festival State," yet there's a widespread local sentiment that "there's nothing to do." We believe the problem isn't a lack of events, but a fragmentation of information. Amazing things are happening constantly, but they're scattered across countless websites, closed social media groups, and physical posters. We were inspired to merge these scattered sources into a single, comprehensive platform to prove how vibrant our city truly is.


## What it does
Mapster is a live, interactive map designed to end the "nothing to do" myth in Adelaide. It acts as a single source of truth by merging scattered event information from across the city into one simple, beautiful interface.

Our platform proves this concept by merging event information from six major sources: Eventbrite, Experience Adelaide, the Adelaide Festival Centre, South Australia Tourism, Google Events, and Ticketmaster. We collate this data, geocode each event's address, and display it all seamlessly on the map. This is combined with our vision to one day allow users to scan physical posters, truly merging Adelaide's digital and physical event landscapes.

Users can explore the city in two powerful ways: a heat map mode to instantly see which areas are buzzing with activity, or a classic pin mode to view individual events. You can also use the search bar to find something specific or browse a complete, alphabetised list of what's on. 

With Mapster, you don't just find events. You discover your city.


## How we built it
We built Mapster as a full-stack event aggregation platform, designed around a distinct data processing pipeline, a backend API, and a frontend user interface. The user-facing experience is delivered through a modern, responsive web app built with SvelteKit and TypeScript, featuring an interactive map powered by Mapbox GL JS. At its core, Mapster’s data aggregation pipeline embodies the “merger” theme: we either employ Selenium and BeautifulSoup or use APIs to scrape event data from six major digital sources, including Eventbrite and Experience Adelaide, while our most innovative feature leverages OpenAI’s GPT-4o Vision API to scan and parse text directly from uploaded event posters. All event addresses are then geocoded into precise coordinates via the OpenCage Geocoding API and stored in a unified Supabase (PostgreSQL) database. This structured dataset is served to the frontend through a Python FastAPI backend deployed on Railway, with the frontend itself deployed globally on Vercel.


## Challenges we ran into
Our primary challenge was data aggregation. Many event websites either lack a public API, have complex structures that are difficult to parse, or implement measures to block web scraping. For example, our initial plan to include Facebook Events was abandoned because scraping their platform is against their Terms of Service, which forced us to pivot and find alternative, more scraper-friendly websites. This multi-source approach also led to data inconsistency, as different sites provide different information, resulting in some forced missing values in our final dataset. On the development side, as we worked in parallel on the frontend, we also had to navigate and resolve several Git merge conflicts.


## What's next for Mapster
We are incredibly proud of our MVP and have a clear vision for Mapster's future. Our next steps would focus on community building and expansion:
- **Community Engagement & Gamification:** We plan to introduce a system for contributor achievements to reward users who help expand our event database.
- **Deeper Social Integration:** We will enhance the platform by adding more direct social media interactions with event tags, allowing users to engage more deeply with the buzz around each event.
- **Scaling and Growth:** Our ultimate goal is to scale the platform beyond Adelaide, launching Mapster in other larger cities to make it the definitive tool for urban discovery.

