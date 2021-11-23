class ExternalImageFile:
    """
    Value class for holding information about external images associated with
    messages.

    Attributes
    ----------
    src:
        The value from the "img" tag "src" field
    filename:
        A string containing the filename to use in storing the file
    content: bytes
         A byte string containing the contents of the message
    """
    def __init__(self, src: str, filename: str, content: bytes):
        self.src = src
        self.filename = filename
        self.content = content

    def __str__(self) -> str:
        return (
            f"ExternalImageFile@{id(self)}['"
            f", src={self.src},"
            f", filename={self.filename},"
            f", len(bytes)={len(self.content)},"
            "]"
        )
