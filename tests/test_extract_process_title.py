import pytest

from whpool.extract.extract import scrub_title


@pytest.mark.parametrize(
    ('subject', 'escaped'),
    [
        ('Foo', 'Foo'),
        ('Foo | Bar', 'Foo \\| Bar'),
        ('Foo\\Bar', 'Foo\\\\Bar')
    ]
)
def test_process_title(subject, escaped):
    assert scrub_title(subject) == escaped
