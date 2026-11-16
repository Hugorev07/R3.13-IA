#!/usr/bin/env python3
"""
Générateur de données synthétiques pour les TP de maintenance prédictive
Projet : Atelier d'usinage connecté (R3.13)
Génère la télémétrie des capteurs (1 728 relevés, 20 colonnes) et les tickets de maintenance.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42

def generer(n_par_machine: int = 288, seed: int = SEED) -> pd.DataFrame:
    """
    Génère le dataset de télémétrie de l'atelier connecté (6 machines, 5 min d'intervalle sur 24h).
    Total : 6 * 288 = 1 728 relevés, 20 colonnes.
    """
    rng = np.random.default_rng(seed)
    machines = [f"M-{i:02d}" for i in range(1, 7)]
    
    # Profils nominaux moyens par machine (temp0, vib0, courant0, cadence0)
    profils = {
        "M-01": (67.0, 1.4, 11.0, 58.0),  # Machine de référence saine
        "M-02": (70.0, 1.7, 12.2, 55.0),
        "M-03": (76.0, 2.9, 15.0, 48.0),
        "M-04": (78.0, 3.2, 15.8, 45.0),
        "M-05": (72.0, 2.1, 13.0, 52.0),
        "M-06": (82.0, 4.1, 17.5, 41.0),  # Machine dégradée / en usure avancée
    }
    
    timestamps = pd.date_range("2025-01-06 00:00:00", periods=n_par_machine, freq="5min")
    rows = []
    
    for t, ts in enumerate(timestamps):
        hour = ts.hour
        # Détermination de l'équipe (3 x 8h)
        if 6 <= hour < 14:
            equipe = "matin"
            p_charge = [0.10, 0.65, 0.25]
        elif 14 <= hour < 22:
            equipe = "après-midi"
            p_charge = [0.05, 0.35, 0.60]
        else:
            equipe = "nuit"
            p_charge = [0.65, 0.30, 0.05]
            
        for m_idx, machine in enumerate(machines):
            temp0, vib0, courant0, cadence0 = profils[machine]
            
            # Niveau de charge opérationnel
            charge = rng.choice(["faible", "moyen", "fort"], p=p_charge)
            charge_mod = {"faible": -0.8, "moyen": 0.0, "fort": 1.0}[charge]
            
            # Fenêtres d'incidents / dérives
            incident = (t % 37 in (0, 1, 2)) or (machine == "M-06" and t % 19 == 0)
            
            # Mesures de procédé avec dérive thermique diurne (+0.018*t) et bruit gaussien
            temp = temp0 + 0.018 * t + rng.normal(0, 2.0) + (8.0 if incident else 0.0) + charge_mod * 0.8
            vibration = vib0 + rng.normal(0, 0.35) + (2.5 if incident else 0.0) + (0.2 if charge == "fort" else 0.0)
            courant = courant0 + rng.normal(0, 0.9) + (3.8 if incident else 0.0) + charge_mod * 0.7
            cadence = cadence0 + rng.normal(0, 2.8) - (9.0 if incident else 0.0) + charge_mod * 1.5
            
            # Spectre vibratoire
            peak = vibration * (1.65 + rng.normal(0, 0.10))
            f1 = max(0.05, vibration * (0.42 + rng.normal(0, 0.05)))
            f2 = max(0.05, vibration * (0.31 + rng.normal(0, 0.04)))
            f3 = max(0.05, vibration * (0.18 + rng.normal(0, 0.03)))
            f4 = max(0.05, vibration * (0.09 + rng.normal(0, 0.02)))
            
            # Défaut a posteriori
            p_defaut = 0.70 if incident else (0.12 if machine == "M-06" else 0.025)
            defaut = int(rng.random() < p_defaut)
            
            # Alarmes à seuils opérationnels
            alarmes = {
                "alarme_temperature": int(temp > 83.0),
                "alarme_vibration": int(vibration > 4.2),
                "alarme_courant": int(courant > 18.5),
                "alarme_cadence": int(cadence < 38.0),
            }
            # Bruit de capteur sur les alarmes (2% d'erreurs de commutation)
            if rng.random() < 0.02:
                k = rng.choice(list(alarmes))
                alarmes[k] = 1 - alarmes[k]
                
            # Annotation experte (régime de référence)
            if incident:
                if alarmes["alarme_vibration"] == 1 or machine in ("M-04", "M-06"):
                    regime = "incident_roulement"
                else:
                    regime = "incident_thermique"
            elif machine == "M-06":
                regime = "usure_avancee"
            elif charge == "fort":
                regime = "charge_elevee"
            else:
                regime = "nominal"
                
            row = {
                "horodatage": ts.isoformat(),
                "machine_id": machine,
                "equipe": equipe,
                "niveau_charge": charge,
                "temperature": temp,
                "vibration": vibration,
                "courant": courant,
                "cadence": cadence,
                "vibration_pic": peak,
                "vib_f1": f1,
                "vib_f2": f2,
                "vib_f3": f3,
                "vib_f4": f4,
                "defaut": defaut,
                **alarmes,
                "regime_reference": regime,
                "donnees_synthetiques": True,
            }
            rows.append(row)
            
    df = pd.DataFrame(rows)
    
    # Introduction des pertes de télémétrie (3 à 5% MCAR sur les mesures de procédé)
    taux_manquants = [("temperature", 0.035), ("vibration", 0.045), ("courant", 0.025), ("cadence", 0.030)]
    for col, rate in taux_manquants:
        mask = rng.random(len(df)) < rate
        df.loc[mask, col] = np.nan
        
    return df

CAUSES_ALARMES = {
    "alarme_temperature": ("surchauffe", "Contrôle refroidissement / remplacement ventilateur"),
    "alarme_vibration": ("vibrations excessives", "Rééquilibrage / remplacement roulement"),
    "alarme_courant": ("surintensité moteur", "Vérification bobinage et alimentation"),
    "alarme_cadence": ("baisse de cadence", "Réglage mécanisme d'entraînement"),
}
TECHNICIENS = ["T-01", "T-02", "T-03", "T-04"]
PAS_MINUTES = 5
DELAI_MIN_TICKETS = 12
PERIODE_PREVENTIF = 40

def generer_interventions(df: pd.DataFrame, seed: int = SEED) -> pd.DataFrame:
    """Génère les tickets d'intervention de maintenance associés à la télémétrie."""
    rng = np.random.default_rng(seed + 1)
    df_t = df.assign(_t=pd.to_datetime(df["horodatage"]))
    alarmes = list(CAUSES_ALARMES)
    tickets = []

    def ajouter(machine, debut, type_, cause, action, priorite, duree, cout):
        tickets.append({
            "machine_id": machine,
            "date_ouverture": debut.isoformat(),
            "date_cloture": (debut + pd.Timedelta(minutes=duree)).isoformat(),
            "type_intervention": type_,
            "cause": cause,
            "action": action,
            "priorite": priorite,
            "duree_arret_min": duree,
            "cout_eur": round(float(cout), 2),
            "technicien": rng.choice(TECHNICIENS),
            "statut": "clos",
            "donnees_synthetiques": True,
        })

    for machine, g in df_t.groupby("machine_id", sort=True):
        g = g.reset_index(drop=True)
        dernier = -DELAI_MIN_TICKETS
        for i, r in g.iterrows():
            actives = [a for a in alarmes if r[a] == 1]
            if r["defaut"] != 1 or i - dernier < DELAI_MIN_TICKETS:
                continue
            if rng.random() >= (0.6 if actives else 0.2):
                continue
            dernier = i
            if actives:
                cause, action = CAUSES_ALARMES[str(rng.choice(actives))]
                priorite = "haute" if len(actives) >= 2 else "moyenne"
            else:
                cause, action, priorite = "défaut qualité sans alarme", "Inspection visuelle et réglages", "basse"
            duree = int(max(15, rng.gamma(3.0, 25 if priorite != "haute" else 45)))
            cout = 80 + duree * rng.uniform(1.5, 3.0) + (rng.uniform(50, 400) if priorite == "haute" else 0)
            ajouter(machine, r["_t"] + pd.Timedelta(minutes=PAS_MINUTES), "corrective", cause, action, priorite, duree, cout)
            
        for i in range(PERIODE_PREVENTIF, len(g), PERIODE_PREVENTIF):
            duree = int(rng.integers(20, 60))
            ajouter(machine, g.loc[i, "_t"], "preventive", "maintenance planifiée",
                    "Graissage, contrôle serrage et nettoyage", "basse", duree, 60 + duree * rng.uniform(1.0, 1.5))
                    
    out = pd.DataFrame(tickets).sort_values(["date_ouverture", "machine_id"], kind="stable").reset_index(drop=True)
    out.insert(0, "ticket_id", [f"TK-{n:04d}" for n in range(1, len(out) + 1)])
    return out

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    default_data_dir = Path(__file__).resolve().parent / "data"
    parser.add_argument("--output", type=Path, default=default_data_dir / "atelier_connecte.csv", help="Chemin CSV de télémétrie")
    parser.add_argument("--output-interventions", type=Path, default=default_data_dir / "interventions_maintenance.csv", help="Chemin CSV des tickets")
    parser.add_argument("--n-par-machine", type=int, default=288, help="Nombre de relevés par machine (288 = 24h à pas de 5 min)")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output_interventions.parent.mkdir(parents=True, exist_ok=True)
    
    df = generer(args.n_par_machine, args.seed)
    df.to_csv(args.output, index=False)
    
    interventions = generer_interventions(df, args.seed)
    interventions.to_csv(args.output_interventions, index=False)
    
    print(f"Dataset de télémétrie généré : {args.output} ({len(df)} lignes, {len(df.columns)} colonnes, seed={args.seed})")
    print(f"Tickets d'intervention générés : {args.output_interventions} ({len(interventions)} tickets)")

if __name__ == "__main__":
    main()
