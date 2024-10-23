import pubchempy as pcp
import image_generator as ig
from eln_packages_common.resourcemanage import Resource_Manager
import printer.generate_label
import json
import slack.slackbot as slackbot

rm = Resource_Manager()
labelgen = printer.generate_label.LabelGenerator()



# CAS numbers fall in the 'name' category on pubchem, so they are searched as names
# you could also search by the common name or any other synonym, however CAS numbers
# should return more consistent results
def get_compound(CAS) -> pcp.Compound:
    compound_list: list[pcp.Compound] = pcp.get_compounds(CAS, "name")
    if len(compound_list) > 1:
        raise ValueError(
            "Multiple compounds with this name have been found, please input a more specific name or CAS number"
        )
    elif len(compound_list) == 0:
        raise ValueError("No compound with this name has been found")
    compound: pcp.Compound = compound_list[0]
    return compound


def check_if_cas(input: str) -> bool:
    for char in input:
        if not char.isdigit() and char != "-":
            return False
    return True


def fill_in(id: int):
    body: dict = rm.get_item(id)
    metadata: dict = json.loads(body["metadata"])
    if check_if_cas(body["title"]): 
        # if the title is a CAS number, search by CAS number, and replace the title with the first synonym on PubChem
        CAS: str = body["title"]
        compound: pcp.Compound = get_compound(body["title"])
        body["title"] = compound.synonyms[0]
    elif "CAS" in metadata["extra_fields"]:
        # if the title is not a CAS but there is a CAS in the metadata, search by that CAS
        CAS = metadata["extra_fields"]["CAS"]["value"]
        compound: pcp.Compound = get_compound(CAS)
    else:
        # otherwise try to search by the non-CAS title
        compound: pcp.Compound = get_compound(body["title"])
    metadata["extra_fields"]["Full name"]["value"] = compound.iupac_name

    if "SMILES" not in metadata["extra_fields"]:
        # if there isn't a SMILES field, create one
        metadata["extra_fields"]["SMILES"] = {
            "type": "text",
            "value": "",
            "description": "From PubChem",
        }
    metadata["extra_fields"]["SMILES"]["value"] = compound.isomeric_smiles
    if "CAS" not in metadata["extra_fields"]:
        # if there isn't a CAS field, create one
        metadata["extra_fields"]["CAS"] = {
            "type": "text",
            "value": "",
            "description": "",
        }
    metadata["extra_fields"]["CAS"]["value"] = CAS
    if "Molecular Weight" not in metadata["extra_fields"]:
        # if there isn't a molecular weight field, create one #TODO: make this a number
        metadata["extra_fields"]["Molecular Weight"] = {
            "type": "text",
            "value": "",
            "description": "From PubChem (g/mol)",
        }
    metadata["extra_fields"]["Molecular Weight"]["value"] = compound.molecular_weight
    if "Pubchem Link" not in metadata["extra_fields"]:
        # if there isn't a Pubchem link field, create one
        metadata["extra_fields"]["Pubchem Link"] = {
            "type": "url",
            "value": "",
            "description": "Link to PubChem page",
        }
    metadata["extra_fields"]["Pubchem Link"]["value"] = (
        f"https://pubchem.ncbi.nlm.nih.gov/compound/{compound.cid}"
    )
    if "Hazards Link" not in metadata["extra_fields"]:
        # if there isn't a hazards link field, create one
        metadata["extra_fields"]["Hazards Link"] = {
            "type": "url",
            "value": "",
            "description": "Link to Hazards section of PubChem",
        }
    metadata["extra_fields"]["Hazards Link"]["value"] = (
        f"https://pubchem.ncbi.nlm.nih.gov/compound/{compound.cid}#section=Hazards-Identification"
    )

    body = {
        "rating": 0, # before i figured out tags I used this to mark autofilled items, no longer necessary. this will remove ratings
        "metadata": json.dumps(metadata),
    }
    rm.change_item(id, body)


def create_and_upload_labels(id: int):
    for file in rm.get_uploaded_files(id):
        if file.to_dict()["real_name"] == "label.pdf":
            print(f"Label already exists for {id}")
            # return
            rm.delete_upload(id, file.to_dict()["id"])
    labelgen.add_item(id)
    labelgen.write_labels()
    rm.upload_file(id, labelgen.path)


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


def autofill(
    start=300, end=None, force=False, info=True, label=True, image=True, size=5
):  # autofills compounds and polymers, force fills in items even if they've already been filled, the other parameters decide what information to fill
    # start: lowest bound of item id to autofill
    # end: highest bound of item id to autofill, no end by default
    # force: whether to fill in items that have already been filled in--False by default
    # info: whether to fill in the information fields--True by default
    # label: whether to generate a label pdf--True by default
    # image: whether to generate an RDKit image--True by default
    # size: number of recent entries to check. Default is 5 to prevent unnecessary traffic. Set to higher to check old entries.
    ### NOTE: if you set start to a very low number, you will likely have to set size to a higher number in order to pull enough entires to reach the start number
    ### the most recent 
    items: list[rm.itemsapi.Item] = rm.get_items(size=size)
    # the type Item is not subscriptable, but has a to_dict() method that makes it a dictionary.
    for item in items:
        type: int = int(item.to_dict()["category"])
        id = item.to_dict()["id"]
        if (end is None and id >= start) or (end is not None and id in range(start, end)):
            if label:
                create_and_upload_labels(id)
            if type == 2 or type == 3:  # limits to only polymers and compounds
                metadata = json.loads(item.to_dict()["metadata"])
                # check if CAS is there. this also indicates whether the item has been filled in already
                if "Autofilled" not in item.to_dict()["tags"] or force:
                    if info:
                        try:
                            fill_in(id)
                            rm.add_tag(id, "Autofilled")
                        except ValueError:
                            rm.add_tag(id, "Not In PubChem")
                            print(f"No compound found for item {id}")
                            slackbot.send_message(f"No compound found in PubChem for item {id}. See https://eln.ddomlab.org/database.php?mode=view&id={id}")
                    if image:
                        try:
                            smiles: str = metadata["extra_fields"]["SMILES"]["value"]
                        except KeyError:
                            print(f"No SMILES found for item {id}")
                            continue
                        check_and_fill_image(smiles, id)
                else:
                    print(f"Item {id} has already been filled in")