"""
Module src pour les utilitaires de maintenance prédictive (R3.13)
Atelier d'usinage connecté
"""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_telemetry(filename: str = "atelier_connecte.csv") -> pd.DataFrame:
    """Charge le jeu de données de télémétrie de l'atelier connecté."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Le fichier {filepath} n'existe pas. Exécutez generateur_atelier.py d'abord.")
    df = pd.read_csv(filepath)
    df["horodatage"] = pd.to_datetime(df["horodatage"])
    return df

def load_interventions(filename: str = "interventions_maintenance.csv") -> pd.DataFrame:
    """Charge le registre des interventions de maintenance."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Le fichier {filepath} n'existe pas. Exécutez generateur_atelier.py d'abord.")
    df = pd.read_csv(filepath)
    df["date_ouverture"] = pd.to_datetime(df["date_ouverture"])
    df["date_cloture"] = pd.to_datetime(df["date_cloture"])
    return df
