from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analyzer import analyze_failure, analyze_failure_with_image
from database import save_analysis, get_history

app = FastAPI(
    title="FailWhisperer API",
    description="AI-powered Playwright test failure analyst",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class AnalyzeRequest(BaseModel):
    error_log: str
    test_name: str = ""

@app.get("/")
def home():
    return {"status": "FailWhisperer is running! 🎭"}

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    if not request.error_log.strip():
        raise HTTPException(status_code=400, detail="Error log cannot be empty!")

    result = analyze_failure(request.error_log)
    result["test_name"] = request.test_name

    # Save to database
    record_id = save_analysis({
        **result,
        "error_log": request.error_log,
        "has_screenshot": False
    })
    result["id"] = record_id
    return result

@app.post("/analyze-with-image")
async def analyze_with_image(
    error_log: str = Form(...),
    test_name: str = Form(""),
    screenshot: UploadFile = File(...)
):
    if not error_log.strip():
        raise HTTPException(status_code=400, detail="Error log cannot be empty!")

    image_bytes = await screenshot.read()
    image_type = screenshot.content_type or "image/png"

    result = analyze_failure_with_image(error_log, image_bytes, image_type)
    result["test_name"] = test_name

    # Save to database
    record_id = save_analysis({
        **result,
        "error_log": error_log,
        "has_screenshot": True
    })
    result["id"] = record_id
    return result

@app.get("/history")
def history():
    return get_history(20)

@app.post("/upload-log")
async def upload_log(
    log_file: UploadFile = File(...),
    test_name: str = Form("")
):
    content = await log_file.read()
    error_log = content.decode("utf-8")

    if not error_log.strip():
        raise HTTPException(status_code=400, detail="Log file is empty!")

    return {
        "error_log": error_log,
        "filename": log_file.filename
    }