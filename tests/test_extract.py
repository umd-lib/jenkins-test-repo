import filecmp

from click.testing import CliRunner

from whpool.cli import main


def test_extracted_csv(shared_datadir):
    input_file = shared_datadir / 'extract.mbox'
    output_dir = shared_datadir / 'extract'
    runner = CliRunner()
    result = runner.invoke(main, ['extract', '-i', input_file, '-o', output_dir])

    assert result.exit_code == 0

    expect_csv = shared_datadir / 'extract_expected/whpool.csv'
    result_csv = output_dir / 'whpool.csv'
    compare = filecmp.cmp(expect_csv, result_csv, shallow=False)
    print(expect_csv.read_text())
    print(result_csv.read_text())
    assert compare is True
