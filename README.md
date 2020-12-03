# Supporting scripts for the WHCA Pool Reports Collection

[whpool-extract.py](whpool-extract.py) - Extract pool reports email messages
from an mbox format file. Write them out to a directory with metadata in
a single whpool.csv and HTML body and other attachments in sub-directories.

[imapbackup.sh](imapbackup.sh) - Sync the contents of the service account
INBOX folder to local INBOX.mbox file.

[mbox_stats.py](mbox_stats.py) - Used to gather statistics of email in an
mbox format file during early investigations.
