import pytesseract
from PIL import Image
import cv2 
import numpy as np


def extract_words_with_boxes_from_image(image: Image) -> list[dict]:
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    words = []
    word_list = data['text']
    for i in range(len(word_list)):
        confidence = data['conf'][i]
        confidence_threshold = 30
        if confidence > confidence_threshold and word_list[i].strip() != '':
            word_info = {
                'text': data['text'][i],
                'x': data['left'][i],
                'y': data['top'][i],
                'w': data['width'][i],
                'h': data['height'][i]
            }
            words.append(word_info)
        else:
            print(f"Skipping word: {word_list[i]} with confidence {confidence}")
    return words

def detect_lines_from_image(image: Image) -> list[tuple[int, int, int, int]]:
    # Convert PIL Image to NumPy array if needed
    if not isinstance(image, np.ndarray):
        image = np.array(image)
        # If the image is RGBA, convert to RGB first
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Detect lines using Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                            minLineLength=30, maxLineGap=5)
    
    underlines = []
    if lines is not None:
        for line in lines:
            _, y1, _, y2 = line[0]
            if abs(y1 - y2) < 5:  # near-horizontal
                underlines.append(line[0])
    return underlines

def match_words_to_underlines(words: list[dict], lines: list[tuple[int, int, int, int]], vertical_gap: int = 30) -> list[tuple[str, str]]:
    matched = []
    for i, word in enumerate(words):
        word_left = word['x']
        word_right = word['x'] + word['w']
        word_bottom = word['y'] + word['h']

        for (x1, y1, x2, _) in lines:
            # Check if the line is just below the word
            if 0 < (y1 - word_bottom) < vertical_gap:
                # Check for horizontal overlap
                line_left = min(x1, x2)
                line_right = max(x1, x2)
                if word_right > line_left and word_left < line_right:
                    sentence = get_sentence_for_word(words, i)
                    matched.append((word['text'], sentence))
                    break
    return matched

def get_sentence_for_word(words: list[dict], position: int) -> str:
    # Go backward to find the start of the sentence
    start = position
    while start > 0:
        if words[start - 1]['text'].endswith('.'):
            break
        start -= 1

    # Go forward to find the end of the sentence
    end = position
    while end < len(words) - 1:
        if words[end]['text'].endswith('.'):
            break
        end += 1

    # Collect the sentence words
    sentence_words = [ word['text'] for word in words[start:end + 1] ]
    sentence = ' '.join(sentence_words)
    return sentence

def match_lines_to_words(
    words: list[dict],
    lines: list[dict],
    x_tolerance: int = 5,  # pixels to allow around the midpoint
    max_vertical_distance: int = 50
) -> list[tuple[str, str]]:
    """
    For each line, find the word whose bounding box contains the line's midpoint (with tolerance).
    Prefer the word closest vertically above or intersecting the line.
    Returns a list of (word, sentence) tuples, one for each line.
    """
    matched = []
    for line in lines:
        print(line)
        x1 = line['x1']
        y1 = line['y1']
        x2 = line['x2']
        y2 = line['y2'] if 'y2' in line else y1
        mid_x = (x1 + x2) / 2
        line_y = min(y1, y2)  # use the higher y (closer to the word)
        best_word = None
        min_vertical_gap = float('inf')
        for i, word in enumerate(words):
            word_left = word['x']
            word_right = word['x'] + word['w']
            word_top = word['y']
            word_bottom = word['y'] + word['h']
            # Check if the midpoint (with tolerance) is within the word's bounding box
            if (word_left - x_tolerance) <= mid_x <= (word_right + x_tolerance):
                # Prefer intersection, otherwise closest above
                if word_top <= line_y <= word_bottom:
                    vertical_gap = 0
                elif line_y > word_bottom:
                    vertical_gap = line_y - word_bottom
                else:
                    continue  # line is above the word, skip
                if vertical_gap < min_vertical_gap and vertical_gap <= max_vertical_distance:

                    best_word = (word['text'], get_sentence_for_word(words, i))
                    min_vertical_gap = vertical_gap
        if best_word:
            matched.append(best_word)
    return matched