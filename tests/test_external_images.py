from whpool.core.external_images import ExternalImagesFactory


def test_create_filename():
    assert 'external_img001.png' == ExternalImagesFactory.create_filename(1, 101, 'image/png')
    assert 'external_img42.jpg' == ExternalImagesFactory.create_filename(42, 100, 'image/jpeg')
    assert 'external_img10.unknown' == ExternalImagesFactory.create_filename(10, 11, 'image/unknown')
