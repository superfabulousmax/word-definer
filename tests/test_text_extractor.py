import re
import pytest
from text_extractor import get_sentence_for_word    

fullstop_sentence = "The quick brown fox jumps over the lazy dog ."
question_sentence = "The quick brown fox jumps over the lazy dog ?"
exclamation_sentence = "The quick brown fox jumps over the lazy dog !"

@pytest.mark.parametrize(
    "sentence, position, expected",
    [
        (fullstop_sentence, 3, fullstop_sentence),
        (question_sentence, 3, question_sentence),
        (exclamation_sentence, 3, exclamation_sentence),
    ]
)
def test_get_sentence_for_word(sentence, position, expected):
    words_raw = re.findall(r'\w+|[^\w\s]', sentence)
    words = [{"text": word, "x": 100, "y": 100} for word in words_raw]
    assert get_sentence_for_word(words, position) == expected