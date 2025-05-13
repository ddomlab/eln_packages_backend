import image_generator as ig
from resourcemanage import Resource_Manager
import fill_info
import printer.generate_label
import json
import slack.slackbot as slackbot

rm = Resource_Manager()
labelgen = printer.generate_label.LabelGenerator()
def create_and_upload_labels(id: int):
    for file in rm.get_uploaded_files(id):
        if file.to_dict()["real_name"] == "label.pdf":
            print(f"Label already exists for {id}")
            return
            # rm.delete_upload(id, file.to_dict()["id"])
    labelgen.add_item(id)
    labelgen.write_labels()
    rm.upload_file(id, str(labelgen.path))


def check_and_fill_image(smiles, id):
    ## upload RDKit image if it isn't there
    files = rm.get_uploaded_files(id)
    for file in files:
        if file.to_dict()["real_name"] == "RDKitImage.png":
            print("Image already exists")
            rm.delete_upload(
                id, file.to_dict()["id"]
            )  # delete the old image, turn off usually
            # return # if the image already exists, don't upload it again
    if smiles != "":
        imagepath = ig.generate_image(smiles)
        print(imagepath)
        rm.upload_file(id, imagepath)


def autofill(start=300, end=None, force=False, info=True, label=True, image=True, size=5):  
    """
    This method controls which functions are called and handles deciding which items to autofill.
    See: https://ddomlab.slite.com/api/s/057qvutxPk1Tx-/ELN-Backend-Scripts
    https://raw.githubusercontent.com/ddomlab/eln_packages_backend/ed42074a949a341adab23ae2ca0a90ec573144fc/Screenshot%202025-05-05%20at%2010-56-14%20%F0%9F%94%99%20ELN%20Backend%20Scripts.png    The start and end parameters can be used to edit a certain range of items.
    This is not necessary in typical use, when the method is run automatically on 
    the 5 most recently created items, and only if their ID is greater than 300, 
    but the functionality is there if needed--for example:
    manually running autofill on a range of items that were created
    before the autofill was implemented.

        :param int start: lowest bound of item id to autofill
        :param int end: highest bound of item id to autofill, no end by default
        :param bool force: whether to fill in items that have already been filled in--False by default
        :param bool info: whether to fill in the information fields--True by default
        :param bool label: whether to generate a label pdf--True by default
        :param bool image: whether to generate an RDKit image--True by default
        :param int size: number of recent entries to check. Default is 5 to prevent unnecessary traffic. Set to higher to check old entries.
    
    ## NOTE: 
    if you want to edit a range of old Resources, and you set `start` to a very low number,
    you will likely have to set `size` to a higher number in order to pull enough entires to reach the start number
    the most recent 
    """
    items: list[dict] = rm.get_items(size=size)
    for item in items:
        if item['category'] is None:  # skip items that don't have a category
            continue
        type: int = int(item["category"])
        id = item["id"]
        if (end is None and id >= start) or (end is not None and id in range(start, end)):
            if label:
                create_and_upload_labels(id)
            if type == 2 or type == 3:  # limits to only polymers and compounds
                metadata = json.loads(item["metadata"])
                # check if the item has been autofilled already, or if force is true
                if item["tags"] is None or "Autofilled" not in item["tags"] or force:
                    if info:
                        try:
                            fill_info.fill_in(id)
                            rm.add_tag(id, "Autofilled")
                        except ValueError as e:
                            if "Null molecule" in str(e):
                                slackbot.send_message(f"Invalid SMILES provided in SMILES field for item {id}. See https://eln.ddomlab.org/database.php?mode=view&id={id}")
                            if item["tags"] is None or "Not In PubChem" not in item["tags"]:
                                rm.add_tag(id, "Not In PubChem")
                                print(str(e))
                                if "No compound" in str(e):
                                    print(f"No compound found for item {id}")
                                    slackbot.send_message(f"No compound found in PubChem for item {id}. See https://eln.ddomlab.org/database.php?mode=view&id={id}")
                                elif "Multiple compounds" in str(e):
                                    print(f"Multiple compounds found for item {id}")
                                    slackbot.send_message(f"Multiple compounds found in PubChem for item {id}. Manual addition of chemical properties required. See https://eln.ddomlab.org/database.php?mode=view&id={id}")
                    if image:
                        try:
                            smiles: str = metadata["extra_fields"]["SMILES"]["value"]
                            check_and_fill_image(smiles, id)
                        except KeyError:
                            print(f"No SMILES found for item {id}")
                            continue
                        except ValueError:
                            if item["tags"] is None or "Invalid SMILES" not in item["tags"]:
                                rm.add_tag(id, "Invalid SMILES")
                                slackbot.send_message(f"Invalid SMILES found for item {id}, cannot generate image.")
                            continue
                else:
                    print(f"Item {id} has already been filled in")