from fastapi import FastAPI, UploadFile, File, HTTPException
import base64
from services.vision_service import analyze_image

app = FastAPI()


@app.post("/analyze-image")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    print(
        f"Filename: {file.filename}, Content-type: {file.content_type}, Size: {len(contents)} bytes"
    )
    encoded = base64.b64encode(contents).decode("utf-8")
    result = analyze_image(encoded)

    if result.get("success") is False:
        raise HTTPException(status_code=400, detail=result.get("error"))

    return {"filename": file.filename, "analysis": result}
