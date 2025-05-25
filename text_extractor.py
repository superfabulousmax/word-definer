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
        confidence_threshold = 60
        if confidence > confidence_threshold and word_list[i].strip() != '':
            word_info = {
                'text': data['text'][i],
                'x': data['left'][i],
                'y': data['top'][i],
                'w': data['width'][i],
                'h': data['height'][i]
            }
            words.append(word_info)
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

# def match_words_to_given_lines(words: list[dict], lines: list[dict], max_vertical_distance: int = 50) -> list[tuple[str, str]]:
#     """
#     Match words to user-provided line coordinates (from the frontend).
#     Each line should be a dict with keys: x1, y1, x2, y2.
#     The line can be just under the word or a bit further below (up to max_vertical_distance).
#     The line must be under the midpoint of the word for a robust match.
#     """
#     matched = []
#     for i, word in enumerate(words):
#         word_left = word['x']
#         word_right = word['x'] + word['w']
#         word_bottom = word['y'] + word['h']
#         word_mid_x = word_left + word['w'] / 2

#         for line in lines:
#             x1, y1, x2 = line['x1'], line['y1'], line['x2']
#             # Allow the line to be just under or a bit further below the word
#             vertical_offset = y1 - word_bottom
#             if -5 < vertical_offset < max_vertical_distance:
#                 line_left = min(x1, x2)
#                 line_right = max(x1, x2)
#                 # Require the midpoint of the word to be within the line segment
#                 if line_left <= word_mid_x <= line_right:
#                     sentence = get_sentence_for_word(words, i)
#                     matched.append((word['text'], sentence))
#                     break

#                 # Additional check to ensure at least 30% of the line is under the word
#                 overlap_left = max(word_left, line_left)
#                 overlap_right = min(word_right, line_right)
#                 overlap = max(0, overlap_right - overlap_left)
#                 line_length = abs(x2 - x1)
#                 if line_length > 0 and (overlap / line_length) > 0.3:
#                     # At least 30% of the line is under the word
#                     sentence = get_sentence_for_word(words, i)
#                     matched.append((word['text'], sentence))
#                     break
#     return matched

def match_lines_to_words(
    words: list[dict],
    lines: list[dict],
    max_vertical_distance: int = 50,
    intersection_threshold: float = 0.5,  # fraction of word width for intersection
    below_threshold: int = 0  # minimum vertical gap for below match
) -> list[tuple[str, str]]:
    """
    For each line, find the word above it (or intersected by it) whose bounding box contains the line's midpoint.
    intersection_threshold: how much of the word's width (centered) to allow for intersection (0.5 = middle 50%)
    below_threshold: minimum vertical gap (in pixels) for below match (default 0)
    Returns a list of (word, sentence) tuples.
    """
    matched = []
    for line in lines:
        x1, y1, x2 = line['x1'], line['y1'], line['x2']
        mid_x = (x1 + x2) / 2
        best_word = None
        min_vertical_gap = float('inf')
        for i, word in enumerate(words):
            word_left = word['x']
            word_right = word['x'] + word['w']
            word_top = word['y']
            word_bottom = word['y'] + word['h']
            word_width = word['w']
            # Define central region for intersection
            center_frac = (1 - intersection_threshold) / 2
            central_left = word_left + center_frac * word_width
            central_right = word_right - center_frac * word_width
            # Check if the midpoint of the line is within the word's horizontal bounds (central region)
            if central_left <= mid_x <= central_right:
                vertical_gap = y1 - word_bottom
                # If the line is below the word
                if below_threshold < vertical_gap < max_vertical_distance and vertical_gap < min_vertical_gap:
                    best_word = (word['text'], get_sentence_for_word(words, i))
                    min_vertical_gap = vertical_gap
                # Or if the line intersects the word's bounding box
                elif word_top <= y1 <= word_bottom:
                    best_word = (word['text'], get_sentence_for_word(words, i))
                    min_vertical_gap = 0  # Prefer intersection
        if best_word:
            matched.append(best_word)
    return matched