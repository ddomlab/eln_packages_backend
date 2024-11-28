import image_generator as ig
from eln_packages_common.resourcemanage import Resource_Manager
import eln_packages_common.fill_info
import printer.generate_label
import json
import slack.slackbot as slackbot

rm = Resource_Manager()
labelgen = printer.generate_label.LabelGenerator()



#get_compound
#check_if_cas
#fill_in
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
    # this method controls which functions are called and handles deciding which items to autofill
    
    # start: lowest bound of item id to autofill
    # end: highest bound of item id to autofill, no end by default
    # force: whether to fill in items that have already been filled in--False by default
    # info: whether to fill in the information fields--True by default
    # label: whether to generate a label pdf--True by default
    # image: whether to generate an RDKit image--True by default
    # size: number of recent entries to check. Default is 5 to prevent unnecessary traffic. Set to higher to check old entries.
    ### NOTE: if you set start to a very low number, you will likely have to set size to a higher number in order to pull enough entires to reach the start number
    ### the most recent 
    items: list = rm.get_items(size=size)
    # the type Item is not subscriptable, but has a to_dict() method that makes it a dictionary.
    for item in items:
        type: int = int(item.to_dict()["category"])
        id = item.to_dict()["id"]
        if (end is None and id >= start) or (end is not None and id in range(start, end)):
            if label:
                create_and_upload_labels(id)
            if type == 2 or type == 3:  # limits to only polymers and compounds
                metadata = json.loads(item.to_dict()["metadata"])
                # check if the item has been autofilled already, or if force is true
                if item.to_dict()["tags"] is None or "Autofilled" not in item.to_dict()["tags"] or force:
                    if info:
                        try:
                            eln_packages_common.fill_info.fill_in(id)
                            rm.add_tag(id, "Autofilled")
                        except ValueError as e:
                            if "Not In PubChem" not in item.to_dict()["tags"]:
                                rm.add_tag(id, "Not In PubChem")
                                print(str(e))
                                if "No compound" in str(e):
                                    print(f"No compound found for item {id}")
                                    slackbot.send_message(f"No single compound found in PubChem for item {id}. See https://eln.ddomlab.org/database.php?mode=view&id={id}")
                                elif "Multiple compounds" in str(e):
                                    print(f"Multiple compounds found for item {id}")
                                    slackbot.send_message(f"Multiple compounds found in PubChem for item {id}. Manual addition of chemical properties required. See https://eln.ddomlab.org/database.php?mode=view&id={id}")
                    if image:
                        try:
                            smiles: str = metadata["extra_fields"]["SMILES"]["value"]
                        except KeyError:
                            print(f"No SMILES found for item {id}")
                            continue
                        check_and_fill_image(smiles, id)
                else:
                    print(f"Item {id} has already been filled in")