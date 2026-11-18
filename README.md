# Jour 3 : UC-06 Transformation, qualité et Data Lakehouse

Retail Intelligence Platform · Laurine Lefebvre · 18/11/2026

## Résultat en bref

La chaîne **Raw → Silver → Gold** a été réalisée avec **PySpark** sur 4 sources TPCx-BB (`store_sales`, `item`, `store`, `date_dim`), pour répondre à deux questions métier du Jour 1 :

| Question | Jeu Gold | Granularité | Lignes |
|---|---|---|---|
| **Q06** : performance des magasins | `gold/ventes_magasin_mois` | 1 magasin × 1 mois | 720 |
| **Q03** : CA et volume par catégorie | `gold/ventes_categorie_annee` | 1 catégorie × 1 année | 45 |

Principaux contrôles :
- 667 579 ventes lues, typées et contrôlées, **sans perte ni duplication** ;
- jointures vérifiées : 667 579 lignes avant et après ;
- **CA net Gold = 1 150 529 586,37**, identique au KPI-01 calculé au Jour 1 avec un autre outil ;
- tous les résultats sont écrits en **Parquet**, puis relus.

Le socle obligatoire UC-06 est réalisé. Les parties UC-05 (NoSQL/HBase) et avancée n'ont **pas** été réalisées.

## Environnement (détail : `docs/environment/fiche_environnement.md`)

| Élément | Version |
|---|---|
| Plateforme | **Google Colab**, avec l'accord du formateur |
| Python | 3.13.18 |
| Spark / PySpark | 4.0.5, mode `local[*]` (une seule machine, 2 processeurs, 12,7 Go) |
| Java | OpenJDK 21.0.12.1 |

**Solution de repli (consigne §9.2, « HDFS indisponible ») :** Colab n'a pas accès au HDFS installé sur mon PC au Jour 2. Les fichiers sources sont lus depuis **Google Drive** : ce sont les mêmes fichiers `.dat` que ceux déposés dans `/retail-lake/raw/tpcxbb/initial/`. **Aucun traitement de ce dossier n'a été exécuté sur HDFS ni sur un cluster.**

## Reproduire le traitement

1. Dans Google Drive, créer le dossier `TP3_retail/data/` avec un sous-dossier par table, contenant les fichiers du kit `retail_project/data/` :
   ```
   TP3_retail/data/store_sales/store_sales.dat
   TP3_retail/data/item/item.dat
   TP3_retail/data/store/store.dat
   TP3_retail/data/date_dim/date_dim.dat
   ```
2. Ouvrir `notebooks/TP3_Retail_Intelligence.ipynb` dans Google Colab (*Fichier → Importer le notebook*).
3. Si besoin, adapter la variable `DOSSIER_DRIVE` dans la cellule « 0. Paramètres ». C'est le **seul** paramètre à modifier.
4. *Exécution → Tout exécuter*, puis autoriser l'accès à Google Drive. La durée est d'environ 3 à 5 minutes.
5. Les résultats sont recopiés sur Drive dans `TP3_retail/resultats/` (`silver/`, `gold/`, `quality/`, `outputs/`).

Le notebook installe PySpark s'il est absent, crée une seule session Spark et n'écrit **jamais** dans les fichiers sources : il travaille sur une copie.

## Contenu du dossier (livrables §10.2)

| N° | Livrable | Emplacement |
|---|---|---|
| 1 | Fiche environnement | `docs/environment/fiche_environnement.md`, `outputs/fiche_environnement.csv` |
| 2 | Inventaire technique | `docs/data-dictionary/inventaire_technique.md`, `outputs/inventaire_sources.csv` |
| 3 | Notebook d'exploration | `notebooks/TP3_Retail_Intelligence.ipynb` (étapes 2 et 3) |
| 4 | Règles de nettoyage | `docs/transformations/regles_nettoyage.md` |
| 5 | Scripts PySpark | `notebooks/TP3_Retail_Intelligence.ipynb` (étapes 5 à 8) ; description dans `docs/transformations/transformations.md` |
| 6 | Données Silver | `data/silver/` (Parquet) |
| 7 | Données Gold | `data/gold/` (Parquet) + documentation dans `docs/transformations/transformations.md` |
| 8 | Données Parquet | `docs/lakehouse/parquet_et_lakehouse.md`, `outputs/comparaison_tailles.csv` |
| 9 | Rapport qualité | `docs/quality/rapport_qualite.md`, `quality/rapport_qualite.csv` |
| 10 | README | ce fichier |
| 11 | Preuves | notebook exécuté (avec ses sorties), `outputs/journal_execution.txt`, `outputs/preuves/` |
| — | Questions de recul | `docs/questions_de_recul.md` |
| — | Tests et réconciliation | `tests/controles.md` |

## Limites

- Les données TPCx-BB sont **synthétiques** : les résultats ne décrivent pas une réalité économique.
- Seul le lot initial `data/` est traité, pas `data_refresh/`. Les ventes s'arrêtent au 13/12/2005.
- Spark tourne en mode local : le traitement distribué sur plusieurs machines n'est pas démontré.
- Les fichiers Parquet produits ne sont **pas** des tables transactionnelles Lakehouse (pas de Delta Lake, Iceberg ni Hudi).

## Préparation du Jour 4

Les deux jeux Gold, documentés et contrôlés, servent de base aux analyses et visualisations métier du Jour 4.
