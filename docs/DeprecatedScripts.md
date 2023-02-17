# Deprecated Scripts

## Capture Workflow

### Google Services Account

Email arrives continuously to a Google Service Account Inbox.

### Thunderbird

Once a month use Thunderbird with IMAP against service account to organize email:

* Create new folder for previous month in the form YYYY-MM
* Search for all email in Inbox before the first day of current month and move them into YYYY-MM folder

### imapbackup.sh

Use imapbackup.sh to export the contents of YYYY-MM folder to local YYYY-MM.mbox files

```bash
$ IMAPBACKUP_PASSWORD=[PASSWORD] ./imapbackup.sh YYYY-MM
```

### Optional: run stats on YYYY-MM.mbox

```bash
$ python mbox_stats.py [INFILE] [OUTFILE]
```
