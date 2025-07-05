from flask import Flask, jsonify, request
from parse import parse_pdf, parse_pdf_binary
import base64

app = Flask(__name__)

# Accept filename && binary data

# have user request with their computer's absolute dir path?
@app.route("/parse/dir", methods=["POST"])
def parse_dir():
    req = request.get_json()
    if not req or "input_dir" not in req or "output_dir" not in req:
        return jsonify({"error": "Invalid request"}), 400
    input_dir = req["input_dir"]
    output_dir = req["output_dir"]
    res = parse_pdf(input_dir, output_dir)
    return jsonify(res), 200

@app.route("/parse/binary", methods=["POST"])
def parse_binary():
    req = request.get_json()
    if not req or "filename" not in req or "bytes" not in req or "output_dir" not in req:
        return jsonify({"error": "Invalid request"}), 400
    filename = req["filename"]
    try:
        bytes = base64.b64decode(req["bytes"])
    except Exception as e:
        return jsonify({"error": f"Invalid bytes: {str(e)}"}), 400
    
    output_dir = req["output_dir"]
    res = parse_pdf_binary(filename, bytes, output_dir)
    return jsonify(res), 200

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Hello, World!"}), 200

if __name__ == "__main__":
    # can only be 127.0.0.1:5000 not localhost:5000
    app.run(port=5000)
