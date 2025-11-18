import subprocess
import threading
import time
import requests
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import socket


app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Map apps to internal ports
apps = {
    "University": {"file": "University.py", "port": 8501, "name": "University App"},
    "Movies": {"file": "Movies.py", "port": 8502, "name": "Movies App"},
}

processes = {}

# Async wait for Streamlit port
async def is_streamlit_ready(port):
    try:
        # run requests.get in separate thread to avoid blocking
        r = await asyncio.to_thread(requests.get, f"http://localhost:{port}", {"timeout": 1})
        return r.status_code == 200
    except:
        return False

async def wait_for_streamlit(port, timeout=15):
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < timeout:
        if await is_streamlit_ready(port):
            return True
        await asyncio.sleep(0.5)
    return False


# Start Streamlit apps in background threads
def start_streamlit(app_file, port):
    subprocess.Popen(
        ["python", "-m", "streamlit", "run", app_file, "--server.port", str(port), "--server.headless", "true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

for app_name, info in apps.items():
    threading.Thread(target=start_streamlit, args=(info["file"], info["port"]), daemon=True).start()

# Check if Streamlit is ready
def is_ready(port):
    try:
        requests.get(f"http://localhost:{port}", timeout=1)
        return True
    except:
        return False

# Home page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "apps": apps, "message": None})

@app.get("/streamlit")
# Proxy endpoint
@app.get("/streamlit")
async def streamlit_proxy(app: str = Query(...)):
    if app not in apps:
        return HTMLResponse("<h3>Invalid Streamlit app</h3>")

    port = apps[app]["port"]

    ready = await wait_for_streamlit(port)
    if not ready:
        # Show loading page if Streamlit not ready
        html = f"""
        <html>
        <body style="text-align:center; margin-top:100px;">
            <h2>Starting {apps[app]['name']}... Please wait ⏳</h2>
            <p>This page will refresh automatically until the app is ready.</p>
            <script>
                setTimeout(() => location.reload(), 1000);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(html)

    # Streamlit ready → proxy content
    r = await asyncio.to_thread(requests.get, f"http://localhost:{port}")
    return Response(content=r.content, media_type=r.headers.get("content-type"))
