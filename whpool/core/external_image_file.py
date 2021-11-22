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
    bytes: bytes
         A byte string containing the contents of the message
    """
    def __init__(self, src: str, filename: str, bytes: bytes):
        self.src = src
        self.filename = filename
        self.bytes = bytes

    def __str__(self) -> str:
        str = f"ExternalImageFile@{id(self)}['"
        str = str + f", src={self.src},"
        str = str + f", filename={self.filename},"
        str = str + f", len(bytes)={len(self.bytes)},"
        str = str + "]"

        return str
