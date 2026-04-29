from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
import base64
from services.vision_service import analyze_image
from services.auth_service import (
    exchange_code_for_token,
    get_github_login_url,
    verify_state,
    verify_token,
)

app = FastAPI()

security = HTTPBearer()


@app.post("/analyze-image")
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):

    try:
        await verify_token(credentials.credentials)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    contents = await file.read()
    print(
        f"Filename: {file.filename}, Content-type: {file.content_type}, Size: {len(contents)} bytes"
    )
    encoded = base64.b64encode(contents).decode("utf-8")
    result = analyze_image(encoded)

    if result.get("success") is False:
        raise HTTPException(status_code=400, detail=result.get("error"))

    return {"filename": file.filename, "analysis": result}


@app.get("/callback")
async def github_callback(code: str, state: str):

    if not verify_state(state):
        raise HTTPException(status_code=400, detail="Invalid state")

    token = await exchange_code_for_token(code)

    if not token:
        raise HTTPException(status_code=400, detail="Failed to get token")

    return {"access_token": token}


@app.get("/login")
async def login():
    url = get_github_login_url()
    return RedirectResponse(url, status_code=302)
