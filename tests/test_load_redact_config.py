import io
from re import Pattern

from whpool.commands.redact import load_redact_patterns, load_redact_strings


def test_load_redact_strings():
    strings_file = io.StringIO(
        '# sample strings file\n'
        'foo\n'
        '\n'
        '# bar\n'
        'baz\n'
    )
    strings = load_redact_strings(strings_file)
    assert len(strings) == 2
    assert 'foo' in strings
    assert 'baz' in strings
    assert 'bar' not in strings


def test_load_redact_patterns():
    patterns_file = io.StringIO(
        'Email address: |-\n'
        '    [a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+\n'
    )
    patterns = load_redact_patterns(patterns_file)
    assert len(patterns) == 1
    assert 'Email address' in patterns
    assert isinstance(patterns['Email address'], Pattern)
