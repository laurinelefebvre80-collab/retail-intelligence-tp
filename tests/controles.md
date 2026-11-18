# Tests et contrôles automatiques

Les tests sont intégrés au notebook : ils s'exécutent à chaque lancement. Résultats de l'exécution du 18/11/2026.

| # | Test | Étape du notebook | Méthode | Attendu | Résultat |
|---|---|---|---|---|---|
| T1 | Lecture et écriture Spark | 1 | petit DataFrame écrit en Parquet puis relu | 2 lignes | ✅ 2 lignes |
| T2 | Structure des fichiers | 2 | nombre de champs par ligne (`split` sur `\|`) | 1 seule valeur par fichier | ✅ 23 / 22 / 29 / 28 |
| T3 | Volumes lus | 2 | `count()` comparé à l'inventaire du Jour 1 | 667 579 / 17 820 / 12 / 109 573 | ✅ identiques |
| T4 | Typage | 5.1 | valeur non nulle avant et nulle après conversion | 0 échec | ✅ 0 |
| T5 | Unicité des clés des référentiels | 5.3 | `assert count() == distinct().count()` (arrêt si faux) | uniques | ✅ |
| T6 | Conservation des lignes | 5.3 | lues = doublons + quarantaine + Silver | égalité | ✅ 667 579 = 0 + 0 + 667 579 |
| T7 | Écriture Silver | 5.5 | relecture Parquet : lignes et schéma | identiques | ✅ |
| T8 | Jointures N:1 | 6 | lignes avant = après ; lignes non rapprochées | égalité ; 0 | ✅ |
| T9 | Réconciliation du CA | 7 | CA Gold = CA Silver | écart 0 | ✅ 0,00 |
| T10 | Contrôle indépendant | 7 | CA Silver = KPI-01 du Jour 1 (pandas) | écart 0 | ✅ 0,00 |
| T11 | Tickets | 7 | somme des tickets Gold = tickets distincts | égalité | ✅ 89 100 |
| T12 | Relecture Gold | 8 | lecture Parquet et schéma | lisible | ✅ 720 et 45 lignes |
| T13 | Lecture sélective | 8 | plan d'exécution (`explain`) | 2 colonnes lues | ✅ `ReadSchema` à 2 colonnes |

Synthèse détaillée : `quality/rapport_qualite.csv` et `docs/quality/rapport_qualite.md`.
