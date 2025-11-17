import asyncio
import subprocess
import sys
import socket
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Map app names to ports and file paths
apps = {
    "University": {"file": "University.py", "port": 8501},
    "Movies": {"file": "Movies.py", "port": 8502},
}

# Keep track of running Streamlit processes
processes = {}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/start-app")
async def start_streamlit(request: Request, selection: str = Form(...)):
    global processes
    
    app_info = apps.get(selection)

    if not app_info:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "message": "Invalid selection!"}
        )

    # Start Streamlit app if not already running
    if selection not in processes or processes[selection].poll() is not None:
        # Launch Streamlit in a subprocess
        processes[selection] = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", app_info["file"], "--server.port", str(app_info["port"])],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # Redirect browser to Streamlit app
    #return RedirectResponse(url=f"http://127.0.0.1:{app_info['port']}", status_code=302)
    message = f"✅Program running ...... wait for it to appear in the next window ⏳"
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "apps": apps, "message": message}
    )