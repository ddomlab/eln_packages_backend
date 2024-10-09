from rdkit import Chem
from rdkit.Chem import Draw
from pathlib import Path

current_dir = Path(__file__).parent


def generate_image(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    filename = str(current_dir.parent / "RDKitImage.png")
    Draw.MolToFile(mol, filename)
    return filename
