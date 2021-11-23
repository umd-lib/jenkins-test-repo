from whpool.extract.extract import MessageFile, create_canonical_body_html


def test_create_canonical_body_html_with_missing_body():
    message_file = MessageFile(filename="Image.jpeg", bytes=[], output_subdir='attachments/',
                               content_id='165C3ED3-A279-423B-A81D-78E9AE3DE195')

    # Message with an attachment, but no body
    processed = {'id': '0', 'files': [message_file]}

    create_canonical_body_html(processed)

    canonical_body = processed['canonical_body_html']
    empty_body = '<body><pre></pre></body>'
    assert empty_body in canonical_body
