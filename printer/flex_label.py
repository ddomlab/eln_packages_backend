from blabel import LabelWriter
from pathlib import Path

current_dir = Path(__file__).parent


class LabelGenerator:
    def __init__(self):
        self.label_writer = LabelWriter(
            str(current_dir / "Flex_Label.html"),
            default_stylesheets=(str(current_dir / "flex_style.css"),),
        )
        self.path=str(current_dir / "labels.pdf")

        self.records = []
    def add_item(self, caption: str = "", codecontent:str | None = None, longcaption: str | None = None):
        self.records.append(
            dict(
                caption=caption,
                qr_text=codecontent,
                longcaption=longcaption
            )
        )

    # generates pdf for all labels in records
    def write_labels(self):
        self.label_writer.write_labels(self.records, target=self.path)
        self.records = []
