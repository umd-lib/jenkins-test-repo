# Scripts for the WHCA Pool Reports Collection

## Development Environment

See [docs/DevelopmentEnvironment.md](docs/DevelopmentEnvironment.md).

## whpool Commands

### Sort

Sorts messages by yyyy-mm to mailbox folders, creating mailbox folders in
  yyyy-mm format if it does not exist.

#### Sort Usage

```
$ whpool sort --help

Usage: whpool sort [OPTIONS]

  Sorts messages by yyyy-mm to mailbox folders, creating mailbox folders in
  yyyy-mm format if it does not exist.

Options:
  -v, --verbose INTEGER  Set verbosity logging output level.
                         0 = Warning
                         1 = Info (default)
                         2 = Debug
  --help                 Show this message and exit.
```

Performs the following:

- Creates mailbox folders in yyyy-mm format if it does not exist
- Moves emails to the appropriate mailbox folder according to date
- Runs once a day in order to keep imap credentials alive.

Note: Remove messages from the Inbox is normally done while accessing the Inbox
using uid('STORE', uid, '+FLAGS', '\\Deleted').
However, this does not work with Gmail when using UIDs.
Using Gmail imap extensions, '+X-GM-LABELS', '\\Trash', deletes messages from all folders
because it uses labels and folders interchangably.
Thus, removing the inbox label while accessing the yyyy-mm folder is the solution.

### mbox_download

Fetches messages in mbox format from previous month's mailbox folder.

#### mbox_download Usage

```
$ whpool mbox_download --help

Usage: whpool mbox_download [OPTIONS]

  Fetch messages in mbox format from mailbox folders.

Options:
  -v, --verbose INTEGER  Set verbosity logging output level.
                         0 = Warning
                         1 = Info (default)
                         2 = Debug
  --help                 Show this message and exit.
```

Performs the following:

- Checks that there are no previous month’s messages in the inbox
- Check if mbox file already exists for one month prior. If it exists, then end.
- Fetches messages from the previous month’s mailbox folder
- Saves messages to an mbox file
- Compares the mbox file messages to the mailbox folder messages
- Needs to run at least once a month

### Extract

Extract pool reports email messages from an mbox format file. Write them out to
a directory with metadata in a single whpool.csv and HTML body and other
attachments in sub-directories.

#### Extract Usage

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

#### Extract Output Format

The output directory will contain:

- "whpool.csv" - a CSV file with one row of metadata from each email:
  - "id" - based on message order within the mbox
  - "Date" - email "Date" header
  - "Reporter" - email "From" header
  - "Title" - email "Subject" header
  - "Pool Report" - ("true"/"false") best guess based on heuristics, see
    [docs/ExtractProcessingRules.md][extract_rules]
  - "Publish" - always "false", will be updated by reviewer
  - "Comments" - always empty,  will be updated by reviewer
- Each output message stored is stored in a folder based on id, with the
following:
  - "body.txt" - original text body, if provided
  - "body.html" - original HTML body, if provided, or a simple “HTML-ized”
    version of the “body.txt” file, if not. The contents of the “body.html”
    file are used in the subsequent processing.
  - "body-processed.html" - the “processed” HTML, all processing *except*
    redactions, including:
    - “Unsubscribe” signature removal
    - Updating in-message links to point to local copies of attachments
    - Updating in-message “img” tags to point to local copies of files
      downloaded from the URL
  - "body-processed-redacted.html" - the “processed” HTML with redactions
  - "attachments/" subfolder - containing any attachments or other “parts”
    included in the message
  - "external_files/" subfolder - containing files downloaded from URLs
    referenced in “img” tags. Files are given generic names (“external_img”),
    a number (starting with “0”), and an extension based on their content
    type (i.e., “.png” for PNG files, “.jpg” for JPEG files, etc.). Unknown
    content types have an “.unknown” extension.
    The files are uniquely numbered across all the messages in the mbox
    (i.e., “external_img00.png”, external_image01.jpg”, etc.). The
    “external_files/” subfolder for a message only contains the external files
    associated with that message (so a subfolder may have non-consecutive
    numbers, or not begin with “0”).

### Redact

Redacts the text of the "body-processed.html" created by [extract](#extract).

#### Redact Usage

```
$ whpool redact --help

Usage: whpool redact [OPTIONS] [DIRECTORIES]...

  Redact strings or patterns in extracted message bodies in the given
  directories.

Options:
  --strings-from-file FILENAME   File containing exact strings to redact, one
                                 per line.
  --patterns-from-file FILENAME  YAML file containing a map of labels to
                                 regular expressions to redact.
  -n, --dry-run                  Display the redacted text, but do not write
                                 the output file.
  --help                         Show this message and exit.
```

#### Built-in Patterns

Defined in [whpool.core.redaction.REDACT_PATTERNS](whpool/core/redaction.py):

* Email address
* North American phone number

#### Strings File Format

The strings file contains exact strings that should be redacted. They are
case-sensitive. Blank lines, or lines whose first non-whitespace character is
a `#` are ignored.

For example, given this strings file:

```
# strings file (this line is ignored)
Foo

# bar
BAZ
```

the two strings that would be redacted are `Foo` and `BAZ`. `bar` is ignored
because it is commented out with a `#`, as is the first line of the file.

#### Patterns File Format

The patterns file is a YAML-formatted file containing regular expressions for
finding text that should be redacted. The file contains a mapping of explanatory
labels to regular expressions. The regular expressions are
[compiled](https://docs.python.org/3.9/library/re.html#regular-expression-objects)
to Python `Pattern` objects using the `re.VERBOSE` flag, so you can use YAML
block scalars to spread out complicated expressions over multiple lines. For
example:

```yaml
North American phone number: |-
  (\+\d{1,2}([ -]|%20)?)? # optional country code with separator
  \(?\d{3}\)?             # area code
  ([. -]|%20)             # separator
  \d{3}                   # exchange
  ([. -]|%20)             # separator
  \d{4}                   # local
```

(Note: This pattern is included in the [built-in patterns](#built-in-patterns),
so there is no need to specify it in an external patterns file. It is simply
presented here as an example of how such a pattern would be formatted.)

### Convert

Converts the directory structure created by [extract](#extract) and the body 
text as processed by [redact](#redact) to a format suitable for use with the
[Plastron] import command.

#### Convert Usage

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

## Full-Text Indexing

See [docs/FullTextIndexing.md](docs/FullTextIndexing.md)

[extract_rules]: docs/ExtractProcessingRules.md
[Plastron]: https://github.com/umd-lib/plastron
[HTML Sanitizer]: https://pypi.org/project/html-sanitizer/

## Depreciated Scripts

[imapbackup.sh](imapbackup.sh) - Sync the contents of the service account
INBOX folder to local INBOX.mbox file.

[mbox_stats.py](mbox_stats.py) - Used to gather statistics of email in an
mbox format file during early investigations.
