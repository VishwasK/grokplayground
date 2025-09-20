import os
from flask import Flask, request, render_template_string
from xai_sdk import Client
from xai_sdk.chat import user, system
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Grok 4 client (uses env var for API key)
client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    timeout=3600,  # Recommended for Grok 4's reasoning
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Grok 4 Chat</title></head>
<body>
    <h1>Chat with Grok 4</h1>
    <form method="post">
        <textarea name="prompt" rows="4" cols="50" placeholder="Enter your prompt here..."></textarea><br>
        <input type="submit" value="Send to Grok 4">
    </form>
    {% if response %}
    <h2>Response:</h2>
    <p>{{ response }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    response = None
    if request.method == "POST":
        prompt = request.form["prompt"]
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok, a highly intelligent, helpful AI assistant."))
        chat.append(user(prompt))
        response = chat.sample().content
    return render_template_string(HTML_TEMPLATE, response=response)

if __name__ == "__main__":
    app.run(debug=True)
