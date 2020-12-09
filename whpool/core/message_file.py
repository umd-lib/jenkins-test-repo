from typing import Optional, Any


class MessageFile:
    """
    Value class for holding information about files associated with a message.

    Attributes
    ----------
    filename: str
        The filename from the message
    bytes: str
         A string containing the contents of the message
    output_subdir: str
        When writing to output, the subdirectory to output to. Default
        is '', which writes to the message folder
    content_id: str
        The content id associated with the file. Defaults to '', which
        indicates no content id. Typically used for matching attachments to
        in-line image links in the message.
    """
    def __init__(self, filename: str, bytes: Optional[Any],
                 output_subdir: str = '', content_id: str = ''):
        self.filename = filename
        self.bytes = bytes
        self.output_subdir = output_subdir
        self.content_id = content_id

    def __str__(self) -> str:
        str = f"MessageFile@{id(self)}['"
        str = str + f", filename={self.filename}"
        str = str + f", output_subdir={self.output_subdir}"
        str = str + f", content_id={self.content_id}"
        str = str + "]"

        return str
