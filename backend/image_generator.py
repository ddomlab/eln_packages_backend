from rdkit import Chem
from rdkit.Chem import Draw


def generate_image(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    filename = "tmp/RDKitImage.png"
    Draw.MolToFile(mol, filename)
    return filename
