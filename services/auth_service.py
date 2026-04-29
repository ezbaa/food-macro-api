import os
import httpx
import secrets

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "").split(",")

valid_states = set()


def get_github_login_url() -> str:
    state = secrets.token_urlsafe(16)
    valid_states.add(state)
    return (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri=http://localhost:8080/callback"
        f"&scope=read:user"
        f"&state={state}"
    )


def verify_state(state: str):
    if state in valid_states:
        valid_states.discard(state)
        return True
    return False


async def exchange_code_for_token(code: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
    data = response.json()
    return data.get("access_token")


async def get_github_user(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user", headers={"Authorization": f"Bearer {token}"}
        )
    data = response.json()
    return data


async def verify_token(token: str):
    user = await get_github_user(token)
    username = user.get("login")
    if username not in ALLOWED_USERS:
        raise Exception(f"User {username} not allowed")
    return user
