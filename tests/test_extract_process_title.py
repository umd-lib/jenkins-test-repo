import pytest

from whpool.extract.extract import process_title


@pytest.mark.parametrize(
    ('subject', 'escaped'),
    [
        ('Foo', 'Foo'),
        ('Foo | Bar', 'Foo \\| Bar'),
        ('Foo\\Bar', 'Foo\\\\Bar')
    ]
)
def test_process_title(subject, escaped):
    assert process_title(subject) == escaped
