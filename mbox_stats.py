#!/usr/bin/env python3

import sys
import mailbox
from email.header import make_header, decode_header
import json

INFILE = sys.argv[1]
OUTFILE = sys.argv[2]

# Read the mbox file
box = mailbox.mbox(INFILE)

# Collect data for output as JSON
stats = {'messages': 0,
         'attachment_types': {},
         'headers': set(),
        }
messages = []

# Iterate over each message
for n, obj in box.iteritems():

    stats['messages'] += 1

    message = {'n': n,
              'headers': {},
              'body': {}
             }

    # Iterate over each message header
    for header, value in obj.items():
        value = make_header(decode_header(value))

        stats['headers'].add(str(header))
        message['headers'][header] = str(value)

        if header in ['From', 'Subject', 'Date']:
            print(header, value)

    # Get the list of attachments
    parts = obj.get_payload() if obj.is_multipart else [obj.get_payload()]

    # Iterate over each attachment
    for part in parts:
        if isinstance(part, str):
            content_type = 'string'
        else:
            content_type = part.get_content_type()

        if content_type not in stats['attachment_types']:
            stats['attachment_types'][content_type] = 1
        else:
            stats['attachment_types'][content_type] += 1

        if content_type in ('text/plain', 'text/html'):
            bytes = part.get_payload(decode=True)
            charset = part.get_content_charset()
            if charset is None:
                charset = 'UTF-8'
            string = bytes.decode(charset)
            message['body'][content_type] = string
        elif content_type == 'string':
            message['body'][content_type] = part

    messages.append(message)

stats['headers'] = list(stats['headers'])

# Output as JSON
with open(OUTFILE, mode='w') as outfile:
    json.dump({'stats': stats, 'messages': messages}, outfile, indent=4)
