from flask import Flask, request, jsonify, send_from_directory
import os
from model import analyze_video

print("🚀 Flask starting...")

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return send_from_directory("static", "login.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if email == "test@gmail.com" and password == "1234":
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["video"]
    shot = request.form.get("shot")

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    result = analyze_video(filepath)
    result["shot"] = shot

    return jsonify(result)

@app.route("/history")
def history():
    return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)