# Scripts for the WHCA Pool Reports Collection

## Development Environment

See [docs/DevelopmentEnvironment.md](docs/DevelopmentEnvironment.md).

## Scripts

[imapbackup.sh](imapbackup.sh) - Sync the contents of the service account
INBOX folder to local INBOX.mbox file.

[mbox_stats.py](mbox_stats.py) - Used to gather statistics of email in an
mbox format file during early investigations.

# whpool commands

## Extract

Extract pool reports email messages from an mbox format file. Write them out to
a directory with metadata in a single whpool.csv and HTML body and other
attachments in sub-directories.

```
> whpool extract --help
usage: whpool extract [-h] -i INPUT -o OUTPUT [-v {0,1,2}]

Extracts files from mbox

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input mbox format email file
  -o OUTPUT, --output OUTPUT
                        Output directory which must already exist; files andsub-directories will be created or overwritten as necessary.
  -v {0,1,2}, --verbosity {0,1,2}
                        verbosity of logging output; default is 1
```

Extract processing rules are described in
[docs/ExtractProcessingRules.md](docs/ExtractProcessingRules.md).