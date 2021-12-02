import re

import pytest

from whpool.core.redaction import REDACT_REPLACEMENT, RedactedText


@pytest.fixture
def text():
    return RedactedText('The quick brown fox jumped over the lazy dog')


def test_redacted_text_string(text):
    text.redact('fox')

    assert str(text) == f'The quick brown {REDACT_REPLACEMENT} jumped over the lazy dog'
    assert '"fox"' in text.matches
    assert text.matches['"fox"'] == 1


def test_redacted_text_pattern(text):
    text.redact(re.compile(r'\b[a-z]{4}\b'), 'Four-letter words')

    assert str(text) == f'The quick brown fox jumped {REDACT_REPLACEMENT} the {REDACT_REPLACEMENT} dog'
    assert 'Four-letter words' in text.matches
    assert text.matches['Four-letter words'] == 2
