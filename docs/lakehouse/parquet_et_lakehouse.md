# Parquet et Data Lakehouse (livrable 8)

## 1. Écriture et relecture

Tous les jeux Silver et Gold sont écrits en Parquet, puis **relus** pour vérifier :
- que la lecture fonctionne ;
- que le schéma est conservé (noms et types identiques) ;
- que le nombre de lignes est conservé ;
- que les valeurs sont exploitables (sommes de CA identiques).

| Jeu | Lignes écrites | Lignes relues | Schéma |
|---|---|---|---|
| silver/store_sales | 667 579 | 667 579 | conservé |
| silver/item | 17 820 | 17 820 | conservé |
| silver/store | 12 | 12 | conservé |
| silver/date_dim | 109 573 | 109 573 | conservé |
| gold/ventes_magasin_mois | 720 | 720 | conservé (colonne de partition `annee` placée à la fin) |
| gold/ventes_categorie_annee | 45 | 45 | conservé |

## 2. Comparaison des tailles (mêmes données)

| Jeu de données | Taille |
|---|---|
| `store_sales` : source `.dat` (texte délimité) | 88,5 Mo |
| `store_sales` : Silver Parquet (4 fichiers) | ≈ 44 Mo |
| Gold magasin × mois : CSV | 111 Ko |
| Gold magasin × mois : JSON | 249 Ko |
| Gold magasin × mois : Parquet | 20 Ko |

*Valeurs exactes : `outputs/comparaison_tailles.csv`.*

**Lecture sélective :** le plan d'exécution de `select("ss_store_sk", "ss_net_paid")` sur le Parquet Silver indique `ReadSchema: struct<ss_store_sk:bigint, ss_net_paid:decimal(12,2)>`. Spark ne lit que **2 colonnes sur 26**.

## 3. Comparaison des formats

| Critère | CSV / `.dat` | JSON | Parquet |
|---|---|---|---|
| Organisation | lignes, valeurs séparées par un délimiteur | un objet clé : valeur par ligne | **par colonnes**, avec métadonnées |
| Lisibilité | lisible dans un éditeur | lisible | **binaire** |
| Types | aucun (tout est du texte) | types simples | **schéma typé** (décimal, date…) |
| Volume (observé) | moyen | le plus gros (noms de colonnes répétés) | le plus petit (compression par colonne) |
| Lecture sélective | non | non | **oui** |
| Usage adapté | échange, sources brutes (Raw) | API, données semi-structurées | **analyse**, zones Silver et Gold |
| Limite | pas de types, séparateur fragile | volumineux, lent | illisible sans outil ; **pas de transactions** |

## 4. Pourquoi ces fichiers Parquet ne sont pas un Lakehouse

Parquet décrit **comment les données sont enregistrées** dans des fichiers. Il n'apporte pas :
- de **transactions ACID** : si deux traitements écrivent en même temps, ou si une écriture plante au milieu, la table peut rester incohérente ;
- d'**historique des versions** (revenir à l'état d'hier) ;
- d'**évolution contrôlée du schéma** (ajout de colonne validé) ;
- de **gestion de la concurrence** entre lecteurs et écrivains.

Ces garanties viennent d'un **format de table** posé au-dessus de Parquet : **Delta Lake**, **Apache Iceberg** ou **Apache Hudi**. Il tient un **journal des transactions** qui liste les fichiers faisant partie de chaque version de la table.

Dans ce TP, aucun de ces formats n'est utilisé. Le mode `overwrite` remplace donc le dossier sans garde-fou. Les fichiers produits sont un **Data Lake au format Parquet**, et non un Lakehouse.

## 5. Partitionnement

`gold/ventes_magasin_mois` est partitionné par **année** (`annee=2001/`, …, `annee=2005/`). Une analyse filtrée sur une année ne lit que son dossier. Partitionner aussi par mois aurait créé 60 très petits fichiers pour 720 lignes : c'est le piège du partitionnement excessif.
