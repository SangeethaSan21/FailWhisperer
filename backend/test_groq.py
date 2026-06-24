from groq import Groq
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Send a test message
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Say hello to FailWhisperer!"}
    ]
)

# Print the response
print(response.choices[0].message.content)