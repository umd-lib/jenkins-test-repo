from whpool.extract.extract import MessageFile, process_attachments


def test_process_attachments():
    body = '''\
<html><div dir="ltr"><img id="id-165C3ED3-A279-423B-A81D-78E9AE3DE195" src="cid:165C3ED3-A279-423B-A81D-78E9AE3DE195" alt="Image.jpeg" style="max-width: 100%;"><br>
</div>
<div><br>
</div>
</html>'''  # noqa

    message_file = MessageFile(filename="Image.jpeg", bytes=[], output_subdir='attachments/',
                               content_id='165C3ED3-A279-423B-A81D-78E9AE3DE195')

    processed = {}
    processed['processed_body_html'] = body
    processed['files'] = [message_file]

    process_attachments(processed)

    updated_body = processed['processed_body_html']
    assert 'src="attachments/Image.jpeg"' in updated_body
