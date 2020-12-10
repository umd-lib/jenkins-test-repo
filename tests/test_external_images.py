from whpool.core.external_images import ExternalImagesFactory


def test_create_filename():
    assert 'external_image001.png' == ExternalImagesFactory.create_filename(1, 101, 'image/png')
    assert 'external_image42.jpg' == ExternalImagesFactory.create_filename(42, 100, 'image/jpeg')
    assert 'external_image10.file' == ExternalImagesFactory.create_filename(10, 11, 'image/unknown')
