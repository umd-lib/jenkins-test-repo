from whpool.core.extraction import MessageFile, create_canonical_body_html


def test_create_canonical_body_html_with_missing_body():
    message_file = MessageFile(filename="Image.jpeg", content=[], output_subdir='attachments/',
                               content_id='165C3ED3-A279-423B-A81D-78E9AE3DE195')

    # Message with an attachment, but no body
    canonical_body = create_canonical_body_html(msg_id='0', files=[message_file])

    empty_body = '<body><pre></pre></body>'
    assert empty_body in canonical_body
