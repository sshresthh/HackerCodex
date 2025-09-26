from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from processor import process_image_with_openai, get_coordinates_from_location

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.post("/api/process-poster")
async def process_poster_endpoint(file: UploadFile = File(...)):
    """Process uploaded poster image and extract event data."""

    image_content = await file.read()
    event_data = process_image_with_openai(image_content)

    if not event_data:
        raise HTTPException(status_code=500, detail="Failed to process image.")

    location_text = event_data.get("Location", "")
    coordinates = get_coordinates_from_location(location_text)
    event_data.update(coordinates)

    return event_data


@app.get("/api/test")
def read_root():
    return {"message": "Hello from Mapster.city"}
