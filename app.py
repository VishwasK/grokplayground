import os
from flask import Flask, request, render_template_string
from xai_sdk import Client
from xai_sdk.chat import user, system
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize client
client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    timeout=3600,
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Grok 4 Fast Chat</title>
    <style>
        body { 
            font-family: 'Salesforce Sans', Arial, sans-serif; 
            background: #f3f2ef; 
            color: #181818; 
            margin: 0; 
            padding: 20px; 
            line-height: 1.5; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        h1 { 
            color: #1589f0; 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            font-weight: bold; 
            color: #333; 
            margin-bottom: 5px; 
        }
        textarea, input[type="text"] { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #d8dde6; 
            border-radius: 4px; 
            box-sizing: border-box; 
        }
        input[type="file"] { 
            width: 100%; 
            padding: 5px; 
        }
        .btn { 
            background: #1589f0; 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 4px; 
            cursor: pointer; 
            font-size: 16px; 
            font-weight: bold; 
        }
        .btn:hover { 
            background: #1067c0; 
        }
        .response { 
            background: #faffbd; 
            padding: 15px; 
            border-radius: 4px; 
            margin-top: 20px; 
            border-left: 4px solid #1589f0; 
        }
        .error { 
            color: #c23934; 
            background: #ef6966; 
            padding: 10px; 
            border-radius: 4px; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Chat with Grok 4 Fast</h1>
        <form method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="prompt">Prompt:</label>
                <textarea name="prompt" rows="4" placeholder="Enter your prompt here..." required>{{ prompt if prompt else '' }}</textarea>
            </div>
            <div class="form-group">
                <label for="file">Upload Text File for Context (.txt only):</label>
                <input type="file" name="file" accept=".txt">
            </div>
            <button type="submit" class="btn">Send to Grok 4 Fast</button>
        </form>
        {% if response %}
        <div class="response">
            <h3>Grok 4 Fast Response:</h3>
            <p>{{ response }}</p>
        </div>
        {% endif %}
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    response = None
    error = None
    prompt = request.form.get("prompt", "") if request.method == "POST" else ""
    
    if request.method == "POST":
        if not prompt:
            error = "Please enter a prompt."
        else:
            try:
                file_content = ""
                uploaded_file = request.files.get("file")
                if uploaded_file and uploaded_file.filename:
                    filename = uploaded_file.filename.lower()
                    if not filename.endswith('.txt'):
                        error = "Unsupported file type. Only .txt files are supported."
                        return render_template_string(HTML_TEMPLATE, prompt=prompt, error=error)
                    file_content = uploaded_file.read().decode('utf-8')

                # Build chat with Grok-4-fast-reasoning (text-only, fast)
                chat = client.chat.create(model="grok-4-fast-reasoning")
                chat.append(system("You are Grok, a highly intelligent, helpful AI assistant."))
                
                full_prompt = prompt
                if file_content:
                    full_prompt = f"Context from file: {file_content}\n\n{full_prompt}"
                
                chat.append(user(full_prompt))
                response = chat.sample().content
            except Exception as e:
                error = f"Chat error: {str(e)}"
    
    return render_template_string(HTML_TEMPLATE, response=response, error=error, prompt=prompt)

if __name__ == "__main__":
    app.run(debug=True)
