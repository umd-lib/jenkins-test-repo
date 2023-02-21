from whpool.core.extraction import MessageFile, rewrite_attachment_path


def test_rewrite_attachment_path():
    body = '''\
<html><div dir="ltr"><img id="id-165C3ED3-A279-423B-A81D-78E9AE3DE195" src="cid:165C3ED3-A279-423B-A81D-78E9AE3DE195" alt="Image.jpeg" style="max-width: 100%;"><br>
</div>
<div><br>
</div>
</html>'''  # noqa

    message_file = MessageFile(filename="Image.jpeg", content=b'', output_subdir='attachments/',
                               content_id='165C3ED3-A279-423B-A81D-78E9AE3DE195')

    updated_body = rewrite_attachment_path(message_file, body)
    assert 'src="attachments/Image.jpeg"' in updated_body
