from text_extractor import extract_words_with_boxes, detect_lines, match_words_to_underlines
from dictionary import get_definition

def main():
    path = "/Users/sinead.urisohn/git/learning/word-definer/images/IMG_1798.jpg"
    words = extract_words_with_boxes(path)
    lines = detect_lines(path)
    matched = match_words_to_underlines(words, lines)
    for word, sentence in matched:   
        print(f"Word: {word}")
        print(f"Sentence: {sentence}")
        print("Definition:")
        print(get_definition(word, sentence))
        print("-" * 40)  # Separator for readability

if __name__ == "__main__":
    main()
