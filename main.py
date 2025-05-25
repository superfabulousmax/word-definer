from text_extractor import extract_words_with_boxes, detect_lines, match_words_to_underlines
def main():
    path = "/Users/sinead.urisohn/git/learning/word-definer/images/IMG_1798.jpg"
    words = extract_words_with_boxes(path)
    lines = detect_lines(path)
    matched = match_words_to_underlines(words, lines)
    print(matched)

if __name__ == "__main__":
    main()
