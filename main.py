from fastapi import FastAPI, UploadFile, File, HTTPException, Cookie, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import base64
from services.vision_service import analyze_image
from services.auth_service import (
    exchange_code_for_token,
    get_github_login_url,
    verify_state,
    verify_token,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://frontend:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze-image")
async def analyze_image_endpoint(
    file: UploadFile = File(...), access_token: str = Cookie(None)
):

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        await verify_token(access_token)
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

    redirect = RedirectResponse(url="http://localhost:5173/analyze")
    redirect.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="strict",
    )

    return redirect


@app.get("/login")
async def login():
    url = get_github_login_url()
    return RedirectResponse(url, status_code=302)


@app.get("/me")
async def me(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        user = await verify_token(access_token)
        return {"username": user.get("login")}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"success": True}
