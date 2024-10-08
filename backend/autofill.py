import pubchempy as pcp
import backend.image_generator as ig
from backend.resourcemanage import Resource_Manager
import json

rm = Resource_Manager()


# a somewhat unnecessary wrapper for pubchem.py
# CAS numbers fall in the 'name' category on pubchem, so they are searched as names
# you could also search by the common name or any other synonym, however CAS numbers
# should return more consistent results
def get_compound(CAS):
    compound_list = pcp.get_compounds(CAS, "name")
    if len(compound_list) > 1:
        raise ValueError(
            "Multiple compounds with this name have been found, please input a more specific name or CAS number"
        )
    elif len(compound_list) == 0:
        raise ValueError("No compound with this name has been found")
    compound = compound_list[0]
    return compound


def fill_in(id):
    body: dict = rm.get_item(id)
    compound = get_compound(body["title"])
    CAS = body["title"]
    metadata = json.loads(body["metadata"])
    metadata["extra_fields"]["SMILES"]["value"] = compound.isomeric_smiles
    metadata["extra_fields"]["Full name"]["value"] = compound.iupac_name
    metadata["extra_fields"]["CAS"]["value"] = CAS
    # metadata["extra_fields"]["Molecular Weight"]["value"] = compound.molecular_weight

    # TODO add hazards : this is proving to be more difficult than expected, i'll deal with this later
    # hazards are not readily accessible through pubchempy api, so i'll have to find another way to get them

    body = {
        "title": compound.synonyms[0],
        "rating": 5,
        "metadata": json.dumps(metadata),
    }
    check_and_fill_image(compound.isomeric_smiles, id)
    rm.change_item(id, body)


def check_and_fill_image(smiles, id):
    ## upload RDKit image if it isn't there
    has_image = False
    files = rm.get_uploaded_files(id)
    for file in files:
        if file.to_dict()["real_name"] == "RDKitImage.png":
            print("Image already exists")
            has_image = True
    if not has_image:
        imagepath = ig.generate_image(smiles)
        print(imagepath)
        rm.upload_file(id, imagepath)


def autofill_chemical(start, end=None, force=False):  # autofills compounds and polymers
    items = rm.get_items(
        size=100
    )  # get the most recent 100 items. ADJUST THIS IF THERE ARE MORE THAN 100 ITEMS AND YOU NEED TO FILL IN MORE (i set this to be reasonably low so if this does cause an error one day, i will be there to see it. hopefully  we shouldn't need to do operations on every chemical very often at all though)
    if end is None:
        end = len(items)
    for item in items:
        type = item.to_dict()["category"]
        if type == 2 or type == 3:  # limits to only polymers and compounds
            print("Filling in item", item.to_dict()["id"])
            metadata = json.loads(item.to_dict()["metadata"])
            CAS = metadata["extra_fields"]["CAS"]["value"]
            id = item.to_dict()["id"]
            # check if CAS is there. also a safety to prevent it going and messing up old resources, unless force is set to true
            if (
                (
                    CAS == "" or force
                )  # check if the compound has already been "filled in"
                and id in range(start, end)  # so it doesn't operate outside of range
            ):
                fill_in(id)
            else:
                print(
                    f"Item {id} is not a compound or polymer, or has already been filled in"
                )


def autofill_image_only(
    start, end=None, force=False
):  # autofills images for compounds and polymers
    items = rm.get_items(
        size=100
    )  # get the most recent 100 items. ADJUST THIS IF THERE ARE MORE THAN 100 ITEMS AND YOU NEED TO FILL IN MORE (i set this to be reasonably low so if this does cause an error one day, i will be there to see it. hopefully  we shouldn't need to do operations on every chemical very often at all though)
    if end is None:
        end = len(items)
    for item in items:
        type = item.to_dict()["category"]
        if type == 2 or type == 3:  # limits to only polymers and compounds
            print("Filling in item", item.to_dict()["id"])
            metadata = json.loads(item.to_dict()["metadata"])
            CAS = metadata["extra_fields"]["CAS"]["value"]
            id = item.to_dict()["id"]
            # check if CAS is there. also a safety to prevent it going and messing up old resources, unless force is set to true
            if (
                (
                    CAS == "" or force
                )  # check if the compound has already been "filled in"
                and id in range(start, end)  # so it doesn't operate outside of range
            ):
                check_and_fill_image(
                    json.loads(item.to_dict()["metadata"])["extra_fields"]["SMILES"][
                        "value"
                    ],
                    id,
                )
            else:
                print(
                    f"Item {id} is not a compound or polymer, or has already been filled in"
                )
