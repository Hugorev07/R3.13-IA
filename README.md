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
│   ├── TP2_segmentation_kmeans.ipynb    # TP 2 : Segmentation non supervisee par K-means
│   ├── TP3_cah_dbscan.ipynb             # TP 3 : Familles de machines, CAH et DBSCAN
│   └── TP4_evaluation_stabilite.ipynb   # TP 4 : Evaluation, profilage et stabilite des clusters
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
| **TP 3** | **Familles de machines et partitionnement avance (CAH & DBSCAN)** | **Termine** | `notebooks/TP3_cah_dbscan.ipynb` |
| **TP 4** | **Evaluation, profilage et stabilite des clusters** | **Termine** | `notebooks/TP4_evaluation_stabilite.ipynb` |
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

### TP 3 : Familles de machines et partitionnement avance (CAH & DBSCAN)
- Familles de machines par CAH (Ward) : Hierarchie sur profils moyens standardises, dendrogramme et partition en 3 familles distinctes ({M-01, M-02, M-05} faible sollicitation, {M-03, M-04} charge elevee, {M-06} etat critique/usure severe).
- Comparaison des criteres de liaison : Mise en evidence de l'effet de chaine du saut minimum (single) sur signaux continus face a l'equilibre de la variance minimale de Ward.
- Lecture du dendrogramme : Comparaison de la coupure mathematique a 2 groupes vs le besoin operationnel de maintenance justifiant 4 regimes.
- Parametrage k-distance pour DBSCAN : Determination empirique de epsilon via le coude de la 5-distance (0.50 a 0.60) et etude de sensibilite de epsilon sur les effectifs.
- Analyse metier du bruit DBSCAN : Preuve de la concentration majeure des anomalies dans le bruit (taux de defauts de 42.0 % dans le bruit vs 7.9 % hors bruit, sur-representation de M-06 et des incidents roulement).
- Benchmark sur formes synthetiques : Mise a l'epreuve des 4 methodes (K-means, CAH Ward, CAH Single, DBSCAN) sur geometries complexes non convexes (blobs, lunes, cercles concentriques).
- Recommandations operationnelles : Synthese concise a destination des equipes de maintenance integrant les roles complementaires de la CAH et de DBSCAN.

### TP 4 : Evaluation, profilage et stabilite des clusters
- Metriques internes (k = 2 a 8) : Confrontation de la Silhouette, de Davies-Bouldin et de Calinski-Harabasz preferant unanimement k = 2.
- Metriques externes vs reference expert : Pic d'ARI (0.275) et d'AMI (0.385) a k = 4, et analyse du biais de sur-decoupage de la purete qui augmente artificiellement avec k.
- Tests de stabilite : Evaluation de la sensibilite aux graines initiales (n_init = 1 vs 20) et robustesse au re-echantillonnage a 80 % (ARI moyen de 0.995 pour k = 4).
- Stabilite temporelle : Decoupage chronologique 50/50 revelant une derive thermique lente et la concentration des pannes en deuxieme moitie de journee (ARI = 0.784).
- Fiches descriptives des 4 segments : Caracterisation physique complete, indicateurs distinctifs en ecart relatif par rapport a l'atelier, limites d'interpretation et recommandations testables de maintenance.
- Note de decision : Arbitrage justifie pour k = 4 comme compromis optimal entre stabilite statistique et actionnabilite terrain.
