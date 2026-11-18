# Preuves – Jour 3 (livrable 11)

**Preuve principale :** le notebook `notebooks/TP3_Retail_Intelligence.ipynb`, **exécuté** et enregistré avec toutes ses sorties. Chaque contrôle y affiche son résultat.

Autres preuves fournies :

| Fichier | Ce qu'il démontre |
|---|---|
| `outputs/journal_execution.txt` | Horodatage de chaque étape (copie, Silver, Gold, rapport qualité) |
| `outputs/fiche_environnement.csv` | Versions réellement utilisées (Python, Spark, Java) |
| `outputs/inventaire_sources.csv` | Sources, tailles, lignes et colonnes observées |
| `outputs/comparaison_tailles.csv` | Tailles .dat / CSV / JSON / Parquet |
| `quality/rapport_qualite.csv` | Tous les contrôles avec leur statut |

## Captures conseillées (à déposer dans ce dossier)

| Nom proposé | Ce que la capture montre | Ce qu'elle démontre |
|---|---|---|
| `01_drive_sources.png` | Le dossier `TP3_retail/data` sur Google Drive | Emplacement des sources (solution de repli) |
| `02_fiche_environnement.png` | Tableau de la fiche d'environnement dans Colab | Environnement réellement utilisé |
| `03_inventaire.png` | Tableau d'inventaire des 4 sources | Lignes et colonnes conformes |
| `04_controle_volumes.png` | Sortie de l'étape 5.3 (lignes initiales, quarantaine, Silver) | Aucune perte de ligne |
| `05_jointures.png` | Tableau des jointures (avant = après) | Jointures sans duplication |
| `06_reconciliation.png` | Tableau de réconciliation du CA | CA Gold = Silver = Jour 1 |
| `07_comparaison_formats.png` | Tableau des tailles + plan `ReadSchema` | Intérêt de Parquet |
| `08_drive_resultats.png` | Le dossier `TP3_retail/resultats` sur Drive | Silver, Gold et quality bien écrits |
