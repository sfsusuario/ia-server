# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

OLLAMA_BASE_URL = "http://localhost:11434"

# --- API Endpoints ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/v1/models', methods=['GET'])
def list_models():
    """List local models from Ollama."""
    try:
        response = requests.get("{}/api/tags".format(OLLAMA_BASE_URL))
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/models/pull', methods=['POST'])
def pull_model():
    """Download/Pull a new model with streaming progress."""
    data = request.get_json()
    model_name = data.get('name')
    if not model_name:
        return jsonify({"error": "Model name is required"}), 400
    
    try:
        def generate():
            # Request stream from Ollama
            response = requests.post(
                "{}/api/pull".format(OLLAMA_BASE_URL),
                json={"name": model_name, "stream": True},
                stream=True
            )
            for line in response.iter_lines():
                if line:
                    # Forward each progress update to the client
                    yield line + b'\n'
                    
        return app.response_class(generate(), mimetype='application/x-ndjson')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/models/delete', methods=['POST'])
def delete_model():
    """Remove a local model."""
    data = request.get_json()
    model_name = data.get('name')
    try:
        response = requests.delete(
            "{}/api/delete".format(OLLAMA_BASE_URL),
            json={"name": model_name}
        )
        if response.status_code == 200:
            return jsonify({"status": "success"})
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- OpenAI Compatibility for Claude Code ---

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI-compatible endpoint."""
    data = request.get_json()
    
    # Map OpenAI format to Ollama format
    ollama_data = {
        "model": data.get("model", "llama3"),
        "messages": data.get("messages", []),
        "stream": data.get("stream", False)
    }
    
    try:
        response = requests.post(
            "{}/api/chat".format(OLLAMA_BASE_URL),
            json=ollama_data,
            stream=ollama_data["stream"]
        )
        
        if ollama_data["stream"]:
            # Basic streaming proxy (simplified for 2.7)
            def generate():
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        # Minimal OpenAI-like chunk format
                        yield "data: {}\n\n".format(json.dumps({
                            "choices": [{"delta": {"content": chunk.get("message", {}).get("content", "")}}]
                        }))
                yield "data: [DONE]\n\n"
            return app.response_class(generate(), mimetype='text/event-stream')
        else:
            result = response.json()
            # Log for debugging
            print("Ollama Response:", json.dumps(result))
            
            if 'error' in result:
                return jsonify({"error": result['error']}), 500

            # Wrap in OpenAI format (handling both 'message' and 'response' fields)
            bot_message = result.get("message")
            if not bot_message and result.get("response"):
                bot_message = {"role": "assistant", "content": result.get("response")}

            openai_response = {
                "id": "chatcmpl-unique",
                "object": "chat.completion",
                "created": 1234567,
                "model": result.get("model"),
                "choices": [{
                    "message": bot_message,
                    "finish_reason": "stop"
                }]
            }
            return jsonify(openai_response)
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Default Flask port 5000
    print("IA Server running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
