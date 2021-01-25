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

### Extract Usage

```
$ whpool extract --help

Usage: whpool extract [OPTIONS]

  Extract pool report emails from mbox format file and create an output
  format suitable for curatorial review.

Options:
  -i, --input FILE        Input mbox format email file.  [required]
  -o, --output DIRECTORY  Output directory which must already exist; files and
                          sub-directories will be created or overwritten as
                          necessary.  [required]

  -v, --verbose           Produce verbose logging output.
  --help                  Show this message and exit.
```

Extract processing rules are described in
[docs/ExtractProcessingRules.md][extract_rules].


### Extract Output Format

The output directory will contain:

* "whpool.csv" - a CSV file with one row of metadata from each email:
    * "id" - based on message order within the mbox
    * "Date" - email "Date" header
    * "Reporter" - email "From" header
    * "Title" - email "Subject" header
    * "Pool Report" - ("true"/"false") best guess based on heuristics, see
      [docs/ExtractProcessingRules.md][extract_rules]
    * "Publish" - always "false", will be updated by reviewer
    * "Comments" - always empty,  will be updated by reviewer

* Each output message stored is stored in a folder based on id, with the
  following:
    * "body.txt" - original text body, if provided
    * "body.html" - original HTML body, if provided, or a simple “HTML-ized”
      version of the “body.txt” file, if not. The contents of the “body.html”
      file are used in the subsequent processing.
    * "body-processed.html" - the “processed” HTML, all processing *except*
      redactions, including:
        * “Unsubscribe” signature removal
        * Updating in-message links to point to local copies of attachments
        * Updating in-message “img” tags to point to local copies of files
          downloaded from the URL
    * "body-processed-redacted.html" - the “processed” HTML with redactions
    * "attachments/" subfolder - containing any attachments or other “parts”
      included in the message
    * "external_files/" subfolder - containing files downloaded from URLs
      referenced in “img” tags. Files are given generic names (“external_img”),
      a number (starting with “0”), and an extension based on their content
      type (i.e., “.png” for PNG files, “.jpg” for JPEG files, etc.). Unknown
      content types have an “.unknown” extension.

      The files are uniquely numbered across all the messages in the mbox
      (i.e., “external_img00.png”, external_image01.jpg”, etc.). The
      “external_files/” subfolder for a message only contains the external files
      associated with that message (so a subfolder may have non-consecutive
      numbers, or not begin with “0”).

## Convert

Converts the directory structure created by [extract](#extract) to a format
suitable for use with the [Plastron] import command.

### Convert Usage

```
$ whpool convert --help

Usage: whpool convert [OPTIONS]

  Convert extracted pool reports metadata and files into an import package.

Options:
  -I, --input-dir DIRECTORY  Location of metadata and binaries to convert to
                             an import package.  [required]

  -o, --output FILENAME      Output CSV file; use "-" for STDOUT.  [required]
  -b, --base-id TEXT         String to prepend to the item id; it will be
                             followed by a "_".  [required]

  --help                     Show this message and exit.
```

Convert expects there to be a `whpool.csv` metadata file in the `input-dir`. It
reads this file, and writes an output CSV file based on the UMD standard item
metadata model.

Column mappings:

| Extracted | Converted        | Notes |
|-----------|------------------|-------|
| id        | Identifier       | prepended with the `--base-id` argument plus "_" |
| Reporter  | Creator          | |
| Title     | Title            | |
| Date      | Date             | converted to ISO 8601 format |
| --        | Object Type      | `http://vocab.lib.umd.edu/form#pool_reports` 
| --        | Rights Statement | `http://vocab.lib.umd.edu/rightsStatement#InC-NC` |

The `body-processed-redacted.html` file is further sanitized using
[HTML Sanitizer], and written to the file `body-{id}.html` in the same directory
as the `body-processed-redacted.html`.

The sanitized HTML, plus any files in the `attachments` subdirectory, are added
to the `FILES` column of the output CSV file.

# Full-Text Indexing

See [docs/FullTextIndexing.md](docs/FullTextIndexing.md)

[extract_rules]: docs/ExtractProcessingRules.md
[Plastron]: https://github.com/umd-lib/plastron
[HTML Sanitizer]: https://pypi.org/project/html-sanitizer/