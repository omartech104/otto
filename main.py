import os
from dotenv import load_dotenv
from groq import Groq
from rich.console import Console

# 1. Load env and setup Rich
load_dotenv()
console = Console()

# 2. Initialize Groq Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

# 3. Define the "Neural Logic"
def otto_brain(user_input):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Otto, a Linux CLI task assistant. "
                    "Output ONLY valid JSON. Fields: action, task, priority, tags."
                )
            },
            {
                "role": "user",
                "content": user_input,
            }
        ],
        model="llama-3.3-70b-versatile", # Or llama3-8b-8192 for even more speed
        response_format={"type": "json_object"} # Forces JSON output
    )
    
    return chat_completion.choices[0].message.content

# 4. Test it
response = otto_brain("Add a high priority task to fix the CSS for the navbar with #frontend tag")
console.print_json(response)