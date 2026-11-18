# Rapport qualité (livrable 9)

Rapport produit automatiquement par le notebook (étape 9), puis enregistré dans `quality/rapport_qualite.csv`. Format : **contrôle, règle, résultat, statut**. Les 6 dimensions du cours sont couvertes (complétude, unicité, validité, cohérence, intégrité, fraîcheur).

| jeu                | dimension   | controle                                    | regle                                            | resultat                                                                            | statut         |
|:-------------------|:------------|:--------------------------------------------|:-------------------------------------------------|:------------------------------------------------------------------------------------|:---------------|
| sources            | Volume      | Nombre de lignes lues                       | Identique à l'inventaire du Jour 1               | store_sales 667579, item 17820, store 12, date_dim 109573                           | OK             |
| toutes             | Validité    | Conversion des types (R1)                   | 0 valeur non convertible                         | 0 échec(s)                                                                          | OK             |
| store_sales        | Complétude  | Champs obligatoires non nuls (R2)           | date, article, magasin, ticket renseignés        | 0 valeur(s) manquante(s)                                                            | OK             |
| store_sales        | Complétude  | Champs facultatifs (R3)                     | Valeurs manquantes conservées                    | ss_customer_sk 0, ss_cdemo_sk 238, ss_hdemo_sk 295, ss_addr_sk 448, ss_promo_sk 158 | OK (documenté) |
| store_sales        | Unicité     | Doublons exacts (R4)                        | 0 doublon après nettoyage                        | 0 retiré(s)                                                                         | OK             |
| store_sales        | Unicité     | Clé ticket + article (R5)                   | Paire unique, sinon analyse (pas de suppression) | 4136 ligne(s) en plus, conservées (quantités et prix différents)                    | À surveiller   |
| store_sales        | Validité    | Quantité > 0 (R6)                           | ss_quantity > 0                                  | 0 ligne(s) en quarantaine                                                           | OK             |
| store_sales        | Validité    | Montants positifs (R7)                      | ss_sales_price ≥ 0 et ss_net_paid ≥ 0            | 0 ligne(s) en quarantaine                                                           | OK             |
| store_sales        | Cohérence   | Marge négative (R8)                         | Conservée et signalée                            | 495971 lignes (74.3 %)                                                              | À surveiller   |
| store_sales        | Cohérence   | Calcul des montants (R9)                    | ext_sales_price = quantité × prix (±0,01)        | 0 écart(s)                                                                          | OK             |
| store_sales        | Intégrité   | Clé article → item (R10)                    | Chaque clé existe dans le référentiel            | 0 orphelin(s)                                                                       | OK             |
| store_sales        | Intégrité   | Clé magasin → store (R10)                   | Chaque clé existe dans le référentiel            | 0 orphelin(s)                                                                       | OK             |
| store_sales        | Intégrité   | Clé date → date_dim (R10)                   | Chaque clé existe dans le référentiel            | 0 orphelin(s)                                                                       | OK             |
| item               | Unicité     | Clé i_item_sk                               | Unique                                           | unique                                                                              | OK             |
| item               | Complétude  | Catégorie renseignée (R12)                  | Absente → « Non renseignée »                     | 0 remplacée(s)                                                                      | OK             |
| store              | Unicité     | Clé s_store_sk                              | Unique                                           | unique                                                                              | OK             |
| date_dim           | Cohérence   | d_year et d_moy cohérents avec d_date (R13) | Même année et même mois                          | 0 incohérence(s)                                                                    | OK             |
| silver/store_sales | Volume      | Conservation des lignes                     | initial = doublons + quarantaine + Silver        | 667579 = 0 + 0 + 667579                                                             | OK             |
| jointures          | Intégrité   | store_sales -> date_dim                     | Lignes avant = après, 0 non rapprochée           | 667579 → 667579, 0 non rapprochée(s)                                                | OK             |
| jointures          | Intégrité   | store_sales -> item                         | Lignes avant = après, 0 non rapprochée           | 667579 → 667579, 0 non rapprochée(s)                                                | OK             |
| jointures          | Intégrité   | store_sales -> store                        | Lignes avant = après, 0 non rapprochée           | 667579 → 667579, 0 non rapprochée(s)                                                | OK             |
| gold               | Cohérence   | Réconciliation du CA                        | CA Gold = CA Silver                              | écart 0.00                                                                          | OK             |
| gold               | Cohérence   | Comparaison avec le Jour 1                  | CA Silver = KPI-01 du Jour 1 (si 0 rejet)        | écart 0.00                                                                          | OK             |
| gold | Fraîcheur | Date du traitement | Tracée dans chaque jeu (`_date_traitement`) | date et heure de l'exécution | OK |

## Bilan

- **Règles respectées :** 0 échec de conversion, 0 clé obligatoire manquante, 0 doublon exact, quantités et montants valides, 0 incohérence de calcul, 0 vente orpheline, dates cohérentes.
- **Anomalies restantes (« À surveiller ») :**
  1. marge négative sur 495 971 lignes (74,3 %), conservée et signalée ;
  2. 4 136 lignes avec le même ticket et le même article mais des quantités et des prix différents, conservées car il n'existe pas de numéro de ligne de ticket pour les distinguer.
- **Données mises à l'écart :** 0 ligne. Le dossier `quality/rejets_store_sales` existe, mais il est vide.
- **Limites des contrôles :** données synthétiques ; lot `data/` uniquement ; pas de contrôle de fraîcheur réel (aucune date de chargement dans les sources) ; noms de colonnes déduits du schéma de référence.
- **Contrôle indépendant :** le CA Gold (1 150 529 586,37) est identique au KPI-01 du Jour 1, calculé avec pandas.
