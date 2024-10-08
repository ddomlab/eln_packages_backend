from blabel import LabelWriter
from backend.resourcemanage import Resource_Manager
import json


class LabelGenerator:
    def __init__(self):
        self.label_writer = LabelWriter(
            "printer/label.html", default_stylesheets=("printer/style.css",)
        )  # TODO: platform agnostic paths
        self.records = []
        self.rm = Resource_Manager()
        self.path = self.rm.printer_path

    def add_item(self, id: int):
        item: dict = self.rm.get_item(id)
        ## adds records to list to be printed
        self.records.append(
            dict(
                id_num=id,
                name=item["title"],
                qr_json=json.dumps({"id": id}),
            )
        )

    # generates pdf for all labels in records
    def write_labels(self):
        self.label_writer.write_labels(self.records, target=self.path)
        self.records = []
