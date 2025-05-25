import pytesseract
from PIL import Image

def extract_text(image_path):
    image = Image.open(image_path)
    text_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    return text_data