class FileOutput:
    level: str
    formatter: str
    max_size: int
    backups_qty: int
    filename_template: str


class StdoutOutput:
    level: str
    formatter: str
