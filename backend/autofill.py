import pubchempy as pcp
import backend.image_generator as ig
from common.resourcemanage import Resource_Manager
import backend.printer.generate_label as labelgen
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


def check_if_cas(input: str) -> bool:
    for char in input:
        if not char.isdigit() and char != "-":
            return False
    return True


def fill_in(id: int):
    body: dict = rm.get_item(id)
    compound = get_compound(body["title"])
    if check_if_cas(body["title"]):
        CAS = body["title"]
        body["title"] = compound.synonyms[0]
    elif "CAS" in json.loads(body["metadata"])["extra_fields"]:
        CAS = json.loads(body["metadata"])["extra_fields"]["CAS"]["value"]
    metadata = json.loads(body["metadata"])
    metadata["extra_fields"]["Full name"]["value"] = compound.iupac_name

    if "SMILES" not in metadata["extra_fields"]:
        metadata["extra_fields"]["SMILES"] = {
            "type": "text",
            "value": "",
            "description": "From PubChem",
        }
    metadata["extra_fields"]["SMILES"]["value"] = compound.isomeric_smiles
    if "CAS" not in metadata["extra_fields"]:
        metadata["extra_fields"]["CAS"] = {
            "type": "text",
            "value": "",
            "description": "",
        }
    metadata["extra_fields"]["CAS"]["value"] = CAS
    if "Molecular Weight" not in metadata["extra_fields"]:
        metadata["extra_fields"]["Molecular Weight"] = {
            "type": "text",
            "value": "",
            "description": "From PubChem (g/mol)",
        }
    metadata["extra_fields"]["Molecular Weight"]["value"] = compound.molecular_weight
    if "Pubchem Link" not in metadata["extra_fields"]:
        metadata["extra_fields"]["Pubchem Link"] = {
            "type": "url",
            "value": "",
            "description": "Link to PubChem page",
        }
    metadata["extra_fields"]["Pubchem Link"]["value"] = (
        f"https://pubchem.ncbi.nlm.nih.gov/compound/{compound.cid}"
    )
    if "Hazards Link" not in metadata["extra_fields"]:
        metadata["extra_fields"]["Hazards Link"] = {
            "type": "url",
            "value": "",
            "description": "Link to Hazards section of PubChem",
        }
    metadata["extra_fields"]["Hazards Link"]["value"] = (
        f"https://pubchem.ncbi.nlm.nih.gov/compound/{compound.cid}#section=Hazards-Identification"
    )

    # TODO add hazards : this is proving to be more difficult than expected, i'll deal with this later
    # hazards are not readily accessible through pubchempy api, so i'll have to find another way to get them

    body = {
        "rating": 5,
        "metadata": json.dumps(metadata),
    }
    rm.change_item(id, body)


def create_and_upload_labels(id: int):
    filenames: list[str] = []
    for file in rm.get_uploaded_files(id):
        filenames.append(file.to_dict()["real_name"])
    if "label.pdf" not in filenames:
        labelgen.add_item(id)
        labelgen.write_labels()
        rm.upload_file(id, labelgen.path)


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


def autofill(
    start=300, end=None, force=False, info=True, label=False, image=False, max=15
):  # autofills compounds and polymers, force fills in items even if they've already been filled, the other parameters decide what information to fill
    # ADJUST max AS NEEDED. set to a small number to limit the scope of damage if something goes wrong, but for huge batch operations, set to a larger number
    items = rm.get_items(size=max)
    if end is None:
        end = start + max
    for item in items:
        type: int = item.to_dict()["category"]
        smiles: str = json.loads(item.to_dict()["metadata"])["extra_fields"]["SMILES"][
            "value"
        ]

        if type == 2 or type == 3:  # limits to only polymers and compounds
            print("Filling in item", item.to_dict()["id"])
            metadata = json.loads(item.to_dict()["metadata"])
            CAS = metadata["extra_fields"]["CAS"]["value"]
            id = item.to_dict()["id"]
            # check if CAS is there. also a safety to prevent it going and messing up old resources, unless force is set to true
            if (CAS == "" or force) and id in range(start, end):
                if info:
                    fill_in(id)
                if label:
                    create_and_upload_labels(id)
                if image:
                    check_and_fill_image(smiles, id)
            else:
                print(
                    f"Item {id} is not a compound or polymer, or has already been filled in"
                )
