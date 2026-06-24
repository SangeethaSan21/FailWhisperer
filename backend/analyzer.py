from groq import Groq
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_failure(error_log: str) -> dict:
    """
    Takes a Playwright error log and returns AI diagnosis.
    
    This is the core function of FailWhisperer!
    Think of it like a QA expert reading the log and 
    telling you exactly what went wrong.
    """
    
    # SYSTEM PROMPT — teaches AI to be a Playwright expert
    # This is like your test setup/configuration
    system_prompt = """
    You are FailWhisperer, an expert Playwright test failure analyst 
    with deep knowledge of:
    - Playwright error types (timeout, locator, assertion, network)
    - Common flaky test patterns
    - Root cause analysis of test failures
    - How to fix broken Playwright tests
    
    When given a Playwright error log, you must respond ONLY in this 
    exact JSON format, nothing else:
    {
        "error_type": "one of: timeout | locator | assertion | network | unknown",
        "root_cause": "plain English explanation of WHY it failed",
        "is_flaky": true or false,
        "fix": "exact code or step to fix this",
        "confidence": "high | medium | low"
    }
    """
    
    # USER PROMPT — the actual Playwright error log
    user_prompt = f"""
    Analyze this Playwright test failure and diagnose it:
    
    {error_log}
    """
    
    # Send to Groq AI and get response
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.1  # Low = more consistent, focused answers
                         # High = more creative but unpredictable
                         # For diagnosis we want low temperature!
    )
    
    # Extract the text response from AI
    # Extract AI text from response
    raw = response.choices[0].message.content

    # Strip markdown code blocks if AI added them
    # AI sometimes wraps JSON in ```json ... ```
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]  # get content between backticks
        if raw.startswith("json"):
            raw = raw[4:]          # remove the word "json"
        raw = raw.strip()

    # Parse JSON safely
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            'error_type': 'unknown',
            'root_cause': raw,
            'is_flaky': False,
            'fix': 'Check manually',
            'confidence': 'low'
        }
    
