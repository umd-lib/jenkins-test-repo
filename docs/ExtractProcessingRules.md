# Extract Processing Rules

## Introduction

The following attempts to capture in plain language the "gist" of the extract
processing rules for stakeholders.

## PoolReport

The "PoolReport" status defaults to "true".

The "PoolReport" status is set to false if any of the following occur in
either the "Subject" or "Body" of the mail message:

Word/Phrase      | Case ignored? | Note
---------------- | ------------- | ----
Dear Colleagues  | No            | First letter of either word may be uncapitialized
Hello Colleagues | No            | First letter of either word may be uncapitialized
Colleagues       | No            |
OFF RECORD       | Yes           |
off the record   | Yes           |
FPPO             | No            |
non-reportable   | Yes           |
reportable       | Yes           |
