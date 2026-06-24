from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analyzer import analyze_failure

# Create FastAPI app
# Think of this like initializing your Playwright browser instance
app = FastAPI(
    title="FailWhisperer API",
    description="AI-powered Playwright test failure analyst",
    version="1.0.0"
)

# CORS — allows React frontend to talk to this backend
# Without this, browser will block the connection
# Analogy: Like allowing cross-origin requests in your API tests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Data Models ──
# Pydantic models = what data we expect to receive
# Like defining your request body schema in Postman

class AnalyzeRequest(BaseModel):
    """What the frontend sends us"""
    error_log: str          # The Playwright error log text
    test_name: str = ""     # Optional test name

class AnalyzeResponse(BaseModel):
    """What we send back"""
    error_type: str
    root_cause: str
    is_flaky: bool
    fix: str
    confidence: str
    test_name: str

# ── Routes / Endpoints ──

@app.get("/")
def home():
    """Health check — is server running?"""
    return {"status": "FailWhisperer is running! 🎭"}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Main endpoint — receives Playwright error log,
    returns AI diagnosis.
    
    This is what you'll call from:
    - Postman (today for testing)
    - React frontend (Day 3+)
    """
    
    # Validate input
    if not request.error_log.strip():
        raise HTTPException(
            status_code=400,
            detail="Error log cannot be empty!"
        )
    
    # Call AI analyzer
    result = analyze_failure(request.error_log)
    
    # Add test name to result
    result["test_name"] = request.test_name
    
    return result