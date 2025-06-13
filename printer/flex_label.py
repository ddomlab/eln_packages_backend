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
    def add_item(self, caption: str = "", codecontent:str | None = None, longcaption: str | None = None, icon: str | None = None):
        """Adds a label to the list to be printed
        :param caption: The caption for the label
        :param codecontent: The content for the QR code, if None, no QR code is generated
        :param longcaption: A longer caption for the label, if None, no long caption is displayed
        :param icon: An icon to be displayed on the label, if None, no icon is displayed
        """
        if codecontent is not None and icon is not None:
            raise ValueError("Cannot have both codecontent and icon at the same time")
        self.records.append(
            dict(
                caption=caption,
                qr_text=codecontent,
                longcaption=longcaption,
                icon=icon
            )
        )

    # generates pdf for all labels in records
    def write_labels(self):
        self.label_writer.write_labels(self.records, target=self.path)
        self.records = []
