# J1 — Retail Intelligence Platform

**TP Jour 1 · UC-01 et UC-02** · Mastère Développement, Data & IA — IPSSI
Auteure : Laurine Lefebvre · Rendu du 16/11/2026

Analyses exécutées par l'auteure sur poste Windows (Python 3.14, DuckDB 2.0) le 16/11/2026. Captures d'écran dans `01_UC01_besoin_exploration/UC01_preuves/captures/`.

## Contenu du rendu

```
J1_Retail_Intelligence/
├── README.md
├── 01_UC01_besoin_exploration/
│   ├── UC01_cadrage_metier.pdf              (1) fiche de cadrage + identification du kit
│   ├── UC01_questions_decisionnelles.pdf    (2) 8 profils (dont Administration), 18 questions + schéma fonctionnel
│   ├── UC01_dictionnaire_KPI.xlsx           (3) 17 KPI : définition, formule, unité, périmètre, sources, limites
│   ├── UC01_inventaire_sources.xlsx         (4) 36 fichiers, 344 colonnes (522 profils avec le refresh), clés, relations, contrôles
│   ├── UC01_qualification_donnees.pdf       (5) formats, granularité, clés, 41 relations testées, confrontation au référentiel formateur
│   ├── UC01_limites_et_hypotheses.pdf       (6) 12 limites, 7 hypothèses, questions de recul
│   └── UC01_preuves/                        captures, scripts, résultats (CSV + Excel), arborescence, aperçus, journal
└── 02_UC02_architecture/
    ├── UC02_comparaison_architectures.pdf   (7) DW / Data Lake / Lakehouse + choix + questions de recul
    ├── UC02_architecture_cible.pdf          (8) architecture logique, zones Bronze/Silver/Gold
    ├── UC02_schema_flux.pdf                 (9) 7 flux décrits (source → consommateur)
    ├── UC02_positionnement_composants.pdf   (10) matrice des composants et de leur statut
    ├── UC02_gouvernance.pdf                 (11) traçabilité, qualité, accès, protection, coûts
    ├── UC02_local_vers_azure.pdf            (12) local Ubuntu vs cible ADLS Gen2
    └── UC02_preuves/                        schéma d'architecture refait sous draw.io (.drawio + .png), sources Graphviz
```

Les parties complémentaire (UC-C1, UC-C2) et avancée (UC-A1) n'ont pas été réalisées.

## Ce qui a été réellement fait / ce qui est une conception

| Élément | Nature |
|---|---|
| Inventaire, profilage des colonnes, contrôles de clés, de relations et de règles métier, valeurs de contrôle des KPI | **Réalisé** : scripts Python exécutés sur les données fournies (résultats dans `UC01_preuves/`) |
| Architecture, flux, zones, gouvernance, cible Azure | **Conception logique** : aucun composant (HDFS, NiFi, Spark, Azure) n'a été déployé au Jour 1 |

## Reproduire l'exploration

Prérequis : Python ≥ 3.12.

```bash
py -m pip install duckdb pandas openpyxl
py 01_UC01_besoin_exploration/UC01_preuves/scripts/explore.py <chemin>/retail_project resultats
py 01_UC01_besoin_exploration/UC01_preuves/scripts/kpi_controle.py <chemin>/retail_project resultats/kpi_valeurs_controle.csv
```

Durée : environ 5 minutes (le fichier `inventory.dat` compte 23 millions de lignes).

## Données

- Kit : `retail_project.zip`, fourni par le formateur. Données synthétiques TPCx-BB, version non communiquée.
- Les fichiers `.dat` **n'ont pas d'en-tête**. Les noms de colonnes viennent du schéma TPCx-BB de référence (`scripts/schema_tpcxbb.py`), et le nombre de colonnes a été vérifié pour chaque fichier.
- Les données ne sont pas incluses dans ce rendu (1 Go).

## Statuts utilisés

**Vérifié** (observé) · **Déduit** (analyse justifiée) · **Hypothèse** (à confirmer) · **Non disponible** (absent) · **À valider** (décision du formateur).
