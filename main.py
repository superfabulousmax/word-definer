from flask import Flask
from routes import ImageProcessor
from flask_cors import CORS

if __name__ == "__main__":
    app = Flask(__name__)
    CORS(app)
    ImageProcessor(app)
    app.run(debug=True)  
