from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

from poster_processor import process_image_with_openai, get_coordinates_from_location

app = FastAPI()


# middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process-poster")
async def process_poster_endpoint(file: UploadFile = File(...)):
    """
    This is the main API endpoint for your feature. It orchestrates the entire AI pipeline.
    """ 

    #read uploaded image file into memory
    image_content = await file.read()
    event_data = process_image_with_openai(image_content)
    
    if not event_data:
        raise HTTPException(status_code=500, detail="Failed to process image with AI.")

    # get location string
    location_text = event_data.get("Location", "")
    coordinates = get_coordinates_from_location(location_text)
    # merging coordinates into event data
    event_data.update(coordinates)
    
    # final JSON data
    return event_data


# test
@app.get("/api/test")
def read_root():
    return {"message": "Hello from Sam's AI Pipeline! 👋"}