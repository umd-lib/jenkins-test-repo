from whpool.commands.convert import get_item_row


def test_get_item_row():
    row = {
        'id': '0',
        'Date': 'Wed, 7 Jul 2021 15:23:51 -0400',
        'Reporter': 'Michael Shear',
        'Title': 'Travel pool report  # 11 — conversation with mayor lightfoot',
        'PoolReport': 'true',
        'Publish': 'true',
        'Comments': ''
    }
    files = ['a.html', 'b.jpg']
    item_row = get_item_row('foo_0', row, files)
    assert item_row['Identifier'] == 'foo_0'
    assert item_row['Date'] == '2021-07-07T15:23:51-04:00'
    assert item_row['Creator'] == 'Michael Shear'
    assert item_row['Title'] == 'Travel pool report  # 11 — conversation with mayor lightfoot'
    assert item_row['Object Type'] == 'http://purl.org/dcmitype/Text'
    assert item_row['Format'] == 'http://vocab.lib.umd.edu/form#pool_reports'
    assert item_row['Rights Statement'] == 'http://vocab.lib.umd.edu/rightsStatement#InC-NC'
    assert item_row['FILES'] == 'a.html;b.jpg'
