from flask import Flask
from routes import ImageProcessor
from flask_cors import CORS

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers="*",
    supports_credentials=True,
    methods=["GET", "POST", "OPTIONS"]
)
ImageProcessor(app)

if __name__ == "__main__":
    print("Starting app...")
    app.run(host="0.0.0.0", port=8000)
