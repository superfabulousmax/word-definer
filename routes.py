from flask import Flask, request
import base64
from io import BytesIO
from PIL import Image
from text_extractor import extract_words_with_boxes_from_image, detect_lines_from_image, match_words_to_underlines, match_words_to_given_lines
from dictionary import get_definition

class ImageProcessor:
    def __init__(self, app: Flask):
        @app.route('/process-image', methods=['POST'])
        def process_image():
            print("Processing image")
            data = request.get_json()
            image_data = data['image']
            lines_data = data.get('lines')
            
            # Remove the data URL prefix and decode
            _, encoded = image_data.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            image = Image.open(BytesIO(img_bytes)).convert("RGB").copy()
            words = extract_words_with_boxes_from_image(image)
            if lines_data:
                matched = match_words_to_given_lines(words, lines_data)
            else:
                lines = detect_lines_from_image(image)
                matched = match_words_to_underlines(words, lines)
            result = []
            for word, sentence in matched:   
                result.append({
                    "Word": word,
                    "Sentence": sentence,
                    "Definition": get_definition(word, sentence)
                })
            print(result)
            return {"results": result}

