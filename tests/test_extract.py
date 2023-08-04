import filecmp

from click.testing import CliRunner

from whpool.cli import main


def test_extracted_csv(datadir):
    input_file = ('tests/data/extract.mbox')
    output_dir = (datadir / 'tests' / 'extract')
    runner = CliRunner()
    result = runner.invoke(main, ['extract', '-i', input_file, '-o', output_dir])

    assert result.exit_code == 0

    expect_csv = ('tests/data/extract_expected/whpool.csv')
    result_csv = (output_dir / 'whpool.csv')
    compare = filecmp.cmp(expect_csv, result_csv, shallow=False)
    assert compare is True
