# Transformations PySpark : Silver et Gold (livrables 5, 6 et 7)

Le code se trouve dans `notebooks/TP3_Retail_Intelligence.ipynb`. Ce document décrit ce qu'il fait.

## 1. Chaîne de traitement

```
Google Drive (fichiers .dat, lecture seule)
      │  copie
      ▼
raw/          4 fichiers .dat, identiques aux sources
      │  lecture en texte + noms de colonnes TPCx-BB
      │  R1 typage explicite · R2 à R13 contrôles · quarantaine
      ▼
silver/       store_sales · item · store · date_dim        (Parquet)
quality/      rejets_store_sales (quarantaine) · rapport_qualite.csv
      │  jointures vérifiées (N:1) · agrégations
      ▼
gold/         ventes_magasin_mois (partitionné par année) · ventes_categorie_annee   (Parquet)
```

## 2. Zone Silver

**Convention de nommage :** `silver/<table source>`. Les noms de colonnes TPCx-BB sont conservés.

Colonnes de **provenance** ajoutées à chaque jeu Silver :

| Colonne | Contenu |
|---|---|
| `_source_fichier` | Fichier d'origine (ex. `store_sales.dat`) |
| `_date_traitement` | Date et heure de l'exécution |
| `_version_regles` | Version des règles de nettoyage (`v1`) |

| Jeu | Lignes | Fichiers Parquet | Contrôle après écriture |
|---|---|---|---|
| `silver/store_sales` | 667 579 | 4 | lignes écrites = lignes relues, schéma conservé |
| `silver/item` | 17 820 | 1 | idem |
| `silver/store` | 12 | 1 | idem |
| `silver/date_dim` | 109 573 | 1 | idem |

**Nombre de fichiers :** sans précaution, Spark écrivait `silver/store_sales` en **200 fichiers** d'environ 300 Ko, à cause du nombre de partitions par défaut après une opération de regroupement. `coalesce(4)` regroupe le résultat en 4 fichiers d'environ 11 Mo. On évite ainsi le problème des « trop nombreux petits fichiers », et la compression est meilleure : 44 Mo au lieu de 59 Mo.

## 3. Jointures vérifiées

| Jointure | Clé | Cardinalité | Lignes avant | Lignes après | Non rapprochées |
|---|---|---|---|---|---|
| ventes → date_dim | `ss_sold_date_sk = d_date_sk` | N:1 | 667 579 | 667 579 | 0 |
| ventes → item | `ss_item_sk = i_item_sk` | N:1 | 667 579 | 667 579 | 0 |
| ventes → store | `ss_store_sk = s_store_sk` | N:1 | 667 579 | 667 579 | 0 |

Avant de joindre, on a vérifié que les clés `i_item_sk`, `s_store_sk` et `d_date_sk` sont **uniques** dans leur référentiel. Le nombre de lignes reste donc identique : aucune vente n'est dupliquée.

## 4. Zone Gold

KPI repris du dictionnaire du Jour 1 :
- **KPI-01 CA net** = somme de `ss_net_paid` ;
- **KPI-02 Quantités** = somme de `ss_quantity` ;
- **KPI-03 Transactions** = nombre de tickets distincts ;
- **KPI-04 Panier moyen** = CA net ÷ nombre de tickets.

### `gold/ventes_magasin_mois` (question Q06)

| Élément | Description |
|---|---|
| Finalité | Comparer la performance des magasins et suivre leur évolution mensuelle |
| Sources | `silver/store_sales`, `silver/store`, `silver/date_dim` |
| Granularité | 1 ligne = 1 magasin × 1 mois (12 magasins × 60 mois = **720 lignes**) |
| Colonnes | `s_store_sk`, `s_store_id`, `s_store_name`, `s_city`, `s_state`, `annee`, `mois`, `ca_net`, `quantite_vendue`, `nb_tickets`, `nb_lignes_vente`, `panier_moyen`, `_sources`, `_date_traitement` |
| Partitionnement | par `annee` (5 dossiers) ; pas par mois, ce qui donnerait trop de petits fichiers pour 720 lignes |
| Règles | ventes Silver uniquement ; CA = `ss_net_paid` ; tickets comptés avec `countDistinct` |
| Limites | ventes magasin seulement (pas le web) ; retours non déduits ; 2005 incomplète (ventes jusqu'au 13/12) ; données synthétiques |

**Résultat :** les 12 magasins ont des CA très proches, de 94,0 M (Sherwood) à 99,0 M (Buffalo) sur la période, soit environ 5 % d'écart. Le panier moyen se situe entre 12 700 et 13 000, et le CA annuel est stable (environ 231 à 234 M).

### `gold/ventes_categorie_annee` (question Q03)

| Élément | Description |
|---|---|
| Finalité | Identifier les catégories qui génèrent le plus de CA et de volume |
| Sources | `silver/store_sales`, `silver/item`, `silver/date_dim` |
| Granularité | 1 ligne = 1 catégorie × 1 année (9 × 5 = **45 lignes**) |
| Colonnes | `i_category`, `annee`, `ca_net`, `quantite_vendue`, `nb_lignes_vente`, `part_ca_annee_pct`, `_sources`, `_date_traitement` |
| Règles | part du CA calculée avec une fenêtre par année (la somme des parts de chaque année = 100 %) |
| Limites | catégorie de l'article telle qu'enregistrée dans `item` ; ventes magasin seulement ; données synthétiques |

**Résultat :** **Music** (45 % du CA) et **Books** (27 %) dominent. Ce sont aussi les catégories qui ont le plus d'articles au catalogue (8 143 et 5 335 sur 17 820) : leur poids reflète surtout la taille de l'offre.

## 5. Réconciliation

| Contrôle | Valeur |
|---|---|
| CA net Silver | 1 150 529 586,37 |
| CA net Gold magasin × mois | 1 150 529 586,37 |
| CA net Gold catégorie × année | 1 150 529 586,37 |
| KPI-01 calculé au Jour 1 (pandas) | 1 150 529 586,37 |
| Tickets (somme Gold) / tickets distincts Silver | 89 100 / 89 100 |
