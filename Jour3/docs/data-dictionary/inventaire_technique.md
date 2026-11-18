# Inventaire technique des sources (livrable 2)

## 1. Sources utilisées

| Source | Fichier réel | Format | Taille | Lignes | Colonnes | Granularité (une ligne = …) | Clé candidate |
|---|---|---|---|---|---|---|---|
| `store_sales` | `store_sales.dat` | texte, séparateur `\|`, sans en-tête, CRLF | 88,5 Mo | 667 579 | 23 | une **ligne de ticket** (un article vendu sur un ticket) | voir § 3 |
| `item` | `item.dat` | idem | 6,5 Mo | 17 820 | 22 | une version d'un article | `i_item_sk` (unique) |
| `store` | `store.dat` | idem | 3 Ko | 12 | 29 | une version d'un magasin | `s_store_sk` (unique) |
| `date_dim` | `date_dim.dat` | idem | 14,7 Mo | 109 573 | 28 | un jour du calendrier (1900 → 2199) | `d_date_sk` (unique) |

Contrôle de structure : **toutes les lignes** de chaque fichier ont exactement le nombre de colonnes attendu (`store_sales` : 23 sur 667 579 lignes ; `item` : 22 ; `store` : 29 ; `date_dim` : 28).

**Noms des colonnes :** absents des fichiers, ils proviennent du **schéma de référence TPCx-BB** (statut : *déduit*, comme au Jour 1). **Lecture :** toutes les colonnes sont d'abord lues en texte, puis converties explicitement (voir règle R1).

**Pourquoi ces 4 sources :** elles suffisent à répondre à Q06 (ventes, magasins, dates) et à Q03 (ventes, articles, dates). Le Jour 1 a montré que leurs clés se rapprochent sans orphelin.

## 2. Schéma retenu après typage (colonnes utilisées)

| Table | Colonne | Type | Rôle |
|---|---|---|---|
| store_sales | `ss_sold_date_sk` | long | clé → `date_dim.d_date_sk` |
| store_sales | `ss_item_sk` | long | clé → `item.i_item_sk` |
| store_sales | `ss_store_sk` | long | clé → `store.s_store_sk` |
| store_sales | `ss_ticket_number` | long | numéro de ticket (transaction) |
| store_sales | `ss_quantity` | integer | quantité vendue |
| store_sales | `ss_sales_price` | decimal(12,2) | prix unitaire de vente |
| store_sales | `ss_ext_sales_price` | decimal(12,2) | montant de la ligne (quantité × prix) |
| store_sales | `ss_net_paid` | decimal(12,2) | **montant payé hors taxes**, utilisé pour le CA net (KPI-01) |
| store_sales | `ss_net_profit` | decimal(12,2) | marge de la ligne |
| store_sales | `ss_customer_sk`, `ss_cdemo_sk`, `ss_hdemo_sk`, `ss_addr_sk`, `ss_promo_sk` | long | clés facultatives (non utilisées pour les KPI) |
| item | `i_item_sk`, `i_item_id` | long, string | identifiants technique et métier |
| item | `i_category`, `i_class`, `i_brand` | string | catégorie (9 valeurs), classe, marque |
| item | `i_current_price`, `i_wholesale_cost` | decimal(12,2) | prix et coût |
| store | `s_store_sk`, `s_store_id` | long, string | identifiants |
| store | `s_store_name`, `s_city`, `s_state` | string | nom et localisation |
| date_dim | `d_date_sk` | long | clé |
| date_dim | `d_date` | date | date du jour |
| date_dim | `d_year`, `d_moy` | integer | année, mois |

Les montants sont typés en **décimal (12,2)** plutôt qu'en nombre à virgule flottante (`double`), pour éviter les erreurs d'arrondi sur les sommes de CA.

## 3. Granularité de `store_sales` : point d'attention

La clé candidate attendue était **ticket + article**. L'exploration montre que **4 038 paires** apparaissent plusieurs fois (4 136 lignes en plus), avec des **quantités et des prix différents**. Il n'y a aucun doublon exact. Le fichier ne contient pas de numéro de ligne de ticket : il n'existe donc pas de clé unique. Le grain réel est « une ligne de ticket ». (Voir règle R5.)

## 4. Profil des valeurs manquantes (`store_sales`)

| Colonne | Valeurs nulles | % |
|---|---|---|
| `ss_addr_sk` | 448 | 0,07 |
| `ss_hdemo_sk` | 295 | 0,04 |
| `ss_cdemo_sk` | 238 | 0,04 |
| `ss_promo_sk` | 158 | 0,02 |
| toutes les autres | 0 | 0 |

`item.i_rec_end_date` et `store.s_rec_end_date` sont vides à 100 % : c'est normal, la version en cours n'a pas de date de fin.

## 5. Période couverte

Ventes du **01/01/2001 au 13/12/2005**, sur 89 100 tickets distincts, avec en moyenne 7,49 lignes par ticket.
