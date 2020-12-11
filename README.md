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
> whpool extract --help
usage: whpool extract [-h] -i INPUT -o OUTPUT [-v {0,1,2}]

Extracts files from mbox

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input mbox format email file
  -o OUTPUT, --output OUTPUT
                        Output directory which must already exist; files and sub-directories will be created or overwritten as necessary.
  -v {0,1,2}, --verbosity {0,1,2}
                        verbosity of logging output; default is 1
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

----
[extract_rules]: docs/ExtractProcessingRules.md