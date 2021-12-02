import logging
import re
from collections import Counter
from typing import Optional, Pattern, Union

logger = logging.getLogger(__name__)

# Redaction replacement string: Left three-quarters block (U+258A)
REDACT_REPLACEMENT = '\u258A' * 10

# built-in redaction patterns
REDACT_PATTERNS = {
    'Email address': re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    'North American phone number': re.compile(r'''
    (\+\d{1,2}([ -]|%20)?)? # optional country code with separator
    \(?\d{3}\)?             # area code
    ([. -]|%20)             # separator
    \d{3}                   # exchange
    ([. -]|%20)             # separator
    \d{4}                   # local
    ''', re.VERBOSE)
}


class RedactedText:
    def __init__(self, text: str):
        self._text = text
        self._redacted_text = text
        self._matches: Counter[str] = Counter()

    def __str__(self) -> str:
        return self._redacted_text

    @property
    def matches(self) -> Counter[str]:
        return self._matches

    def redact(self, pattern: Union[str, Pattern[str]], label: Optional[str] = None) -> str:
        if label is None:
            label = f'"{pattern}"'
        if isinstance(pattern, str):
            pattern = re.compile(re.escape(pattern))
        self._redacted_text, count = pattern.subn(REDACT_REPLACEMENT, self._redacted_text)
        if count > 0:
            self._matches[label] += count
        return self._redacted_text
