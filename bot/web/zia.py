import os, json, datetime, hashlib
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import uvicorn
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

# --- Configs ---
PUBLIC_WEB_CONFIG_PATH = os.path.join(ROOT_DIR, "config", "web.json")
PRIVATE_WEB_CONFIG_PATH = os.path.join(ROOT_DIR, "secrets", "config", "web.json")
ROUTE_PATH = os.path.join(ROOT_DIR, "secrets", "config", "route.json")
PERSONA_PATH = os.path.join(ROOT_DIR, "config", "persona.json")

with open(PUBLIC_WEB_CONFIG_PATH, "r") as f:
    public_web_config = json.load(f)
with open(PRIVATE_WEB_CONFIG_PATH, "r") as f:
    private_web_config = json.load(f)
with open(ROUTE_PATH, "r") as f:
    route_config = json.load(f)
try:
    with open(PERSONA_PATH, "r") as f:
        persona_config = json.load(f)
except Exception:
    persona_config = {
        "default": {
            "role": "system",
            "content": "You are ZIA, a friendly indie dev lounge AI."
        }
    }

TEMPLATE_NAME = public_web_config.get("template", "web_01")
TEMPLATE_DIR = os.path.join(ROOT_DIR, "bot", "web", "templates", TEMPLATE_NAME)

HOST_MODE = private_web_config.get("host", "localhost")
PORT = private_web_config.get("port", 5000)
if HOST_MODE == "localhost":
    HOST = "127.0.0.1"
elif HOST_MODE in ["lan", "domain"]:
    HOST = "0.0.0.0"
else:
    HOST = "127.0.0.1"

ENDPOINTS = route_config.get("endpoints", [])
MODEL = route_config.get("model", "qwen3-v1-4b")
MAX_TOKENS = route_config.get("tokens", {}).get("max_tokens", 100)

# --- Auth setup ---
SECRET_KEY = "super-secret-key"  # replace with secure value in secrets
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- FastAPI app ---
app = FastAPI()
app.mount("/static", StaticFiles(directory=TEMPLATE_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# --- Simple user store ---
USER_DB_PATH = os.path.join(ROOT_DIR, "secrets", "db", "users.json")
os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
if not os.path.exists(USER_DB_PATH):
    with open(USER_DB_PATH, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# --- Memory functions ---
def memory_path(user_id, chat_id):
    return os.path.join(ROOT_DIR, "secrets", "db", f"user_{user_id}_chat_{chat_id}.json")

def load_memory(user_id, chat_id, limit=20):
    path = memory_path(user_id, chat_id)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        history = json.load(f)
    return history[-limit:]

def save_memory(user_id, chat_id, role, content):
    path = memory_path(user_id, chat_id)
    history = []
    if os.path.exists(path):
        with open(path, "r") as f:
            history = json.load(f)
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.datetime.now().isoformat()
    })
    with open(path, "w") as f:
        json.dump(history, f, indent=2)

# --- AI call ---
def call_ai(user_message, user_id, chat_id):
    persona = persona_config.get("default")
    memory = load_memory(user_id, chat_id)
    messages = [persona] + memory + [{"role": "user", "content": user_message}]

    for endpoint in ENDPOINTS:
        try:
            response = requests.post(
                endpoint,
                json={
                    "model": MODEL,
                    "messages": messages,
                    "max_tokens": MAX_TOKENS
                },
                timeout=10
            )
            if response.status_code != 200:
                continue
            reply = response.json()["choices"][0]["message"]["content"]
            save_memory(user_id, chat_id, "user", user_message)
            save_memory(user_id, chat_id, "assistant", reply)
            return reply
        except Exception as e:
            print(f"⚠️ Failed on {endpoint}: {e}")
            continue
    return "⚠️ All endpoints failed, please try again later."

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    users = load_users()
    if username in users:
        raise HTTPException(status_code=400, detail="User already exists")
    users[username] = {"password": hash_password(password)}
    save_users(users)
    return {"msg": "User registered successfully"}

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    users = load_users()
    if username not in users or users[username]["password"] != hash_password(password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token_data = {"sub": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/chat/{chat_id}")
async def chat(chat_id: int, request: Request, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    data = await request.json()
    user_message = data.get("message", "")

    # Persona + memory
    persona = persona_config.get("default")
    memory = load_memory(username, chat_id)
    messages = [persona] + memory + [{"role": "user", "content": user_message}]

    reply = None
    for endpoint in ENDPOINTS:
        try:
            # First attempt with model
            payload = {
                "model": MODEL,
                "messages": messages,
                "max_tokens": MAX_TOKENS
            }
            response = requests.post(endpoint, json=payload, timeout=10)

            # Retry without model if failed
            if response.status_code != 200:
                payload.pop("model", None)
                response = requests.post(endpoint, json=payload, timeout=10)

            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]
                break
        except Exception as e:
            print(f"⚠️ Failed on {endpoint}: {e}")
            continue

    if not reply:
        reply = "⚠️ All endpoints failed, please try again later."

    # Save memory
    save_memory(username, chat_id, "user", user_message)
    save_memory(username, chat_id, "assistant", reply)

    history = load_memory(username, chat_id)
    return {"reply": reply, "history": history}


if __name__ == "__main__":
    print(f"✅ Web chat running on {HOST}:{PORT}, template={TEMPLATE_NAME}")
    uvicorn.run(app, host=HOST, port=PORT)