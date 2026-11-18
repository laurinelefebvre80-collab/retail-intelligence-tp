# Règles de nettoyage (livrable 4)

Principe : chaque règle est **explicite, mesurable et justifiée**. Aucune ligne n'est supprimée en silence : une ligne écartée part en **quarantaine** (`quality/rejets_store_sales`), avec son motif. Les sources ne sont jamais modifiées.

| N° | Anomalie | Règle | Action | Justification | Lignes concernées |
|---|---|---|---|---|---|
| R1 | Type incorrect | Conversion explicite : clés → long, quantités → integer, montants → decimal(12,2), dates → date | Comptage des valeurs non convertibles | L'inférence automatique ne valide pas un schéma | **0** échec (4 tables) |
| R2 | Champ obligatoire manquant | Date, article, magasin et ticket renseignés | Quarantaine (`cle_obligatoire_absente`) | Une vente sans ces clés ne peut être rattachée à rien | **0** |
| R3 | Champ facultatif manquant (client, adresse, démographie, promotion) | Valeur conservée (`null`) | Aucune | Absence légitime possible ; champs non utilisés pour les KPI | 158 à 448 par colonne (< 0,1 %) |
| R4 | Doublon exact | Une seule ligne conservée | `dropDuplicates()` | Une même ligne de ticket ne peut être comptée deux fois | **0** |
| R5 | Ticket + article répété | Analyse ; **pas de suppression automatique** | Lignes conservées, statut « À surveiller » | Quantités et prix différents : ce ne sont pas des copies ; pas de numéro de ligne pour les distinguer | **4 136** lignes (4 038 paires) |
| R6 | Quantité invalide | `ss_quantity` > 0 | Quarantaine (`quantite_invalide`) | Une vente porte au moins un article ; les retours sont dans `store_returns` | **0** (min 1, max 100) |
| R7 | Montant négatif | `ss_sales_price` ≥ 0 et `ss_net_paid` ≥ 0 | Quarantaine pour investigation (`montant_negatif`) | Un montant négatif peut être une correction : on l'isole sans le supprimer | **0** |
| R8 | Valeur atypique : marge négative | `ss_net_profit` < 0 | **Conservée** et signalée | Cas métier possible (vente à perte, remise) ; donnée synthétique : ne pas interpréter comme une réalité économique | **495 971** (74,3 %) |
| R9 | Incohérence de calcul | `ss_ext_sales_price` = `ss_quantity` × `ss_sales_price` (± 0,01) | Contrôle | Cohérence interne des montants | **0** écart |
| R10 | Clé sans correspondance (intégrité) | Article dans `item`, magasin dans `store`, date dans `date_dim` | Quarantaine (`article_inconnu`, `magasin_inconnu`, `date_inconnue`) | Une vente orpheline fausserait les agrégats | **0** |
| R11 | Texte mal formaté | Espaces superflus retirés (`trim`) dans `item` et `store` | Nettoyage | Harmonisation des libellés | colonnes texte de `item` et `store` |
| R12 | Catégorie absente (`item`) | Remplacée par « Non renseignée » | Remplacement documenté | Garder ces articles dans l'analyse par catégorie sans inventer de catégorie | **0** |
| R13 | Date incohérente (`date_dim`) | `d_year` et `d_moy` identiques à l'année et au mois de `d_date` | Contrôle | Regroupements par mois et par année corrects | **0** |

## Bilan des volumes (`store_sales`)

| Étape | Lignes |
|---|---|
| Lignes lues | 667 579 |
| Doublons exacts retirés (R4) | 0 |
| Lignes en quarantaine (R2, R6, R7, R10) | 0 |
| **Lignes en Silver** | **667 579** |
| Contrôle : lues = doublons + quarantaine + Silver | ✅ |

## Ce qui n'a volontairement pas été fait

- Les valeurs manquantes **n'ont pas été remplacées par zéro** : un zéro aurait un sens (« aucune promotion ») différent de « inconnu ».
- Les marges négatives et les paires ticket + article répétées **n'ont pas été supprimées** : rien ne prouve qu'il s'agit d'erreurs.
- Aucune colonne n'a été renommée : les noms TPCx-BB sont conservés, pour garder le lien avec la source.
