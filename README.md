# Atelier d'usinage connecté - Maintenance Prédictive (R3.13)

Ce dépôt héberge l'ensemble des travaux pratiques de la ressource **R3.13 : Maintenance Prédictive & Data Science appliquée à l'industrie**.

L'objectif global est de développer et valider une chaîne complète d'analyse de données, de segmentation non supervisée, de détection d'anomalies et de prédiction de défaillances sur un atelier d'usinage composé de 6 machines interconnectées (`M-01` à `M-06`).

---

## Architecture du Dépôt

```text
.
├── data/
│   ├── atelier_connecte.csv          # Relevés capteurs (1 728 relevés, 20 variables, pas de 5 min)
│   └── interventions_maintenance.csv # Registre synthétique des tickets d'intervention
├── notebooks/
│   └── TP1_preparation_telemetrie.ipynb # TP 1 : Préparation et exploration de la télémétrie
├── src/
│   ├── __init__.py
│   └── data_loader.py                # Fonctions utilitaires réutilisables (chargement des données)
├── generateur_atelier.py             # Script de génération synthétique des données
├── requirements.txt                  # Dépendances Python du projet
├── .gitignore
└── README.md                         # Documentation du projet
```

---

## Installation et Environnement

### 1. Cloner le dépôt
```bash
git clone <URL_DU_DEPOT>
cd <NOM_DU_DEPOT>
```

### 2. Créer et activer un environnement virtuel
```bash
# Sous Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Sous Linux / macOS (bash)
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. (Optionnel) Régénérer les jeux de données
Si les fichiers de données ne sont pas présents dans `data/`, exécutez le script générateur :
```bash
python generateur_atelier.py
```

---

## Sommaire des Séances de TP

| Séance | Sujet du TP | Statut | Fichier associé |
| :--- | :--- | :---: | :--- |
| **TP 1** | **Préparation et exploration de la télémétrie capteurs** |  **Terminé** | `notebooks/TP1_preparation_telemetrie.ipynb` |
| **TP 2** | Segmentation non supervisée des régimes de fonctionnement (K-Means, DBSCAN) | ⏳ *À venir* | `notebooks/TP2_segmentation_regimes.ipynb` |
| **TP 3** | Détection d'anomalies statistiques et résidus thermomécaniques | ⏳ *À venir* | `notebooks/TP3_detection_anomalies.ipynb` |
| **TP 4** | Modélisation supervisée du risque de panne et classification prédictive | ⏳ *À venir* | `notebooks/TP4_classification_defauts.ipynb` |
| **TP 5** | Estimation de la durée de vie résiduelle (RUL - Remaining Useful Life) | ⏳ *À venir* | `notebooks/TP5_estimation_rul.ipynb` |
| **TP 6** | Fusion de données : croisement télémétrie et tickets d'intervention GMAO | ⏳ *À venir* | `notebooks/TP6_fusion_gmao.ipynb` |
| **TP 7** | Déploiement d'un tableau de bord de maintenance prédictive | ⏳ *À venir* | `notebooks/TP7_dashboard_monitoring.ipynb` |

---

## Détail du TP 1 : Préparation & Exploration de la télémétrie

Le **TP 1** pose les fondations rigoureuses de la démarche de Data Science industrielle :
1. **Premier regard & Classification des variables :** Dictionnaire de données, exclusion motivée des variables de fuite (target leakage, variables d'évaluation expert, constantes, horodatage).
2. **Audit des valeurs manquantes :** Quantification des pertes de paquets de télémétrie (3 à 5% MCAR) et analyse d'homogénéité inter-machines.
3. **Exploration des distributions & Hypothèses métier :** Visualisations (histogrammes, boxplots) et formulation de deux hypothèses majeures de maintenance (dérive thermique et état critique de `M-06`).
4. **Découpage chronologique strict :** Séparation Train (70%) / Test (30%) sans fuite du futur (*data leakage* évité).
5. **Imputation robuste :** Justification théorique et démonstration chiffrée de la médiane face aux valeurs aberrantes (outliers capteurs).
6. **Encodage propre :** Encodage ordinal strict (`niveau_charge`) et One-Hot Encoding (`machine_id`, `equipe`) fitté exclusivement sur le train.
7. **Standardisation & Détection de dérive :** Mise à l'échelle via `StandardScaler` fitté sur le train ; mise en évidence de la dérive thermique diurne.
8. **Analyse de l'espace des distances :** Comparaison des distances Euclidienne, Manhattan et Cosinus ; démonstration mathématique de l'effet d'échelle écrasant les signaux vibratoires sans standardisation.
9. **Synthèse & Variables retenues :** Cartographie finale des features prêtes pour le TP 2.
