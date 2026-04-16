from fastapi import FastAPI, UploadFile, File
import base64
from services.vision_service import analyze_image

app = FastAPI()

@app.post("/analyze-image")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    encoded = base64.b64encode(contents).decode("utf-8")
    result = analyze_image(encoded)

    if result.get("success") is False:
        return {"success": False, "error": result.get("error")}

    return {"filename": file.filename, "analysis": result}