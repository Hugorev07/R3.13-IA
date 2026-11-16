# Atelier d'usinage connecte - Maintenance Predictive (R3.13)

Ce depot heberge l'ensemble des travaux pratiques de la ressource **R3.13 : Maintenance Predictive & Data Science appliquee a l'industrie**.

L'objectif global est de developper et valider une chaine complete d'analyse de donnees, de segmentation non supervisee, de detection d'anomalies et de prediction de defaillances sur un atelier d'usinage compose de 6 machines interconnectees (`M-01` a `M-06`).

---

## Architecture du Depot

```text
.
├── data/
│   ├── atelier_connecte.csv          # Releves capteurs (1 728 releves, 20 variables, pas de 5 min)
│   └── interventions_maintenance.csv # Registre synthetique des tickets d'intervention
├── notebooks/
│   ├── TP1_preparation_telemetrie.ipynb # TP 1 : Preparation et exploration de la telemetrie
│   └── TP2_segmentation_kmeans.ipynb    # TP 2 : Segmentation non supervisee par K-means
├── src/
│   ├── __init__.py
│   └── data_loader.py                # Fonctions utilitaires reutilisables (chargement des donnees)
├── generateur_atelier.py             # Script de generation synthetique des donnees
├── requirements.txt                  # Dependances Python du projet
├── .gitignore
└── README.md                         # Documentation du projet
```

---

## Installation et Environnement

### 1. Cloner le depot
```bash
git clone <URL_DU_DEPOT>
cd <NOM_DU_DEPOT>
```

### 2. Creer et activer un environnement virtuel
```bash
# Sous Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Sous Linux / macOS (bash)
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dependances
```bash
pip install -r requirements.txt
```

### 4. (Optionnel) Regenerer les jeux de donnees
Si les fichiers de donnees ne sont pas presents dans `data/`, executez le script generateur :
```bash
python generateur_atelier.py
```

---

## Sommaire des Seances de TP

| Seance | Sujet du TP | Statut | Fichier associe |
| :--- | :--- | :---: | :--- |
| **TP 1** | **Preparation et exploration de la telemetrie capteurs** | **Termine** | `notebooks/TP1_preparation_telemetrie.ipynb` |
| **TP 2** | **Segmentation non supervisee des regimes de fonctionnement (K-means)** | **Termine** | `notebooks/TP2_segmentation_kmeans.ipynb` |
| **TP 3** | Detection d'anomalies statistiques et residus thermomecaniques | A venir | `notebooks/TP3_detection_anomalies.ipynb` |
| **TP 4** | Modelisation supervisee du risque de panne et classification predictive | A venir | `notebooks/TP4_classification_defauts.ipynb` |
| **TP 5** | Estimation de la duree de vie residuelle (RUL - Remaining Useful Life) | A venir | `notebooks/TP5_estimation_rul.ipynb` |
| **TP 6** | Fusion de donnees : croisement telemetrie et tickets d'intervention GMAO | A venir | `notebooks/TP6_fusion_gmao.ipynb` |
| **TP 7** | Deploiement d'un tableau de bord de maintenance predictive | A venir | `notebooks/TP7_dashboard_monitoring.ipynb` |

---

## Detail des Travaux Pratiques Realises

### TP 1 : Preparation & Exploration de la telemetrie
- Premier regard & classification des variables : Dictionnaire de donnees et exclusion motivee des variables de fuite (defaut, alarmes, constantes, horodatage).
- Audit des valeurs manquantes : Quantification des pertes de paquets (3 a 5 % MCAR) et analyse de repartition inter-machines.
- Exploration des distributions & hypotheses metier : Visualisations et formulation des deux hypotheses de maintenance (derive thermique diurne et etat critique de M-06).
- Decoupage chronologique sans fuite : Separation Train (70 %) / Test (30 %) basee sur le quantile temporel.
- Imputation robuste : Demonstration chiffree de la mediane face aux valeurs aberrantes capteurs.
- Encodage rigoureux : OrdinalEncoder pour le niveau de charge et OneHotEncoder sans ordre artificiel pour les machines et equipes.
- Standardisation & detection de derive : Mise a l'echelle sans fuite revelant la derive thermique au test.
- Analyse de l'espace des distances : Demonstration de l'effet d'echelle ecrasant les signaux vibratoires sans standardisation.

### TP 2 : Segmentation non supervisee par K-means
- K-means maison en pur NumPy : Implementation vectorisee de l'affectation et de la mise a jour avec n_init relances ; accord parfait avec scikit-learn (ARI = 1.000, inertie = 1522.98).
- Choix de k : Analyse croisee de l'inertie (methode du coude) et du coefficient de silhouette moyen (pic a k=2, compromis metier justifie a k=4).
- Profilage metier ordonne : Tri strict des 4 clusters par temperature mediane croissante (0 a 3), calcul des medianes physiques dans leurs unites d'origine, taux de defauts a posteriori et croisement avec les machines (M-01 a M-06).
- Nommage prudent et actions de maintenance : Formalisation des 4 regimes (ralenti, nominal stabilise, forte charge, regime severe/incident) et precaunisations operationnelles de maintenance.
- Effet de l'echelle : Entrainement sur donnees brutes non standardisees (ARI ~ 0.44), demontrant que la temperature et la cadence masquent le signal vibratoire critique en l'absence de centrage-reduction.
