from groq import Groq
from dotenv import load_dotenv
import os
import json
import base64

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


def analyze_failure_with_image(error_log: str, image_bytes: bytes, image_type: str) -> dict:
    """
    Analyzes Playwright failure using BOTH error log + screenshot.
    Uses vision-capable model on Groq.
    """
    # Convert image bytes to base64 string
    # This is how we send images through text-based APIs
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    system_prompt = """
    You are FailWhisperer, an expert Playwright test failure analyst.
    You will be given BOTH a Playwright error log AND a screenshot of 
    the browser at the moment of failure.
    
    Analyze both together for the most accurate diagnosis.
    Look at the screenshot for:
    - What element was visible/missing
    - Page loading state
    - Any visible error messages
    - UI state that caused the failure
    
    Respond ONLY in this exact JSON format, no markdown:
    {
        "error_type": "timeout|locator|assertion|network|unknown",
        "root_cause": "detailed explanation using both log and screenshot",
        "is_flaky": true or false,
        "fix": "specific fix based on what you see in the screenshot",
        "confidence": "high|medium|low",
        "screenshot_insight": "what you observed in the screenshot"
    }
    """

    # Vision model API call — sends both text and image
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Analyze this Playwright failure:\n\nERROR LOG:\n{error_log}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{image_type};base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        temperature=0.1
    )

    raw = response.choices[0].message.content

    # Strip markdown if needed
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            'error_type': 'unknown',
            'root_cause': raw,
            'is_flaky': False,
            'fix': 'Check manually',
            'confidence': 'low',
            'screenshot_insight': 'Could not parse response'
        }