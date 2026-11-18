# Fiche environnement – Jour 3 (livrable 1)

Valeurs **observées** dans le notebook (cellule « Fiche d'environnement »), exécution du 18/11/2026.

| Élément | Valeur observée |
|---|---|
| Plateforme | Google Colab (autorisé par le formateur) |
| Python | 3.13.18 |
| Spark / PySpark | 4.0.5 |
| Java | OpenJDK 21.0.12.1 |
| Mode d'exécution | `local[*]` : Spark en local sur la machine Colab, **pas de cluster** |
| Processeurs | 2 |
| Mémoire | 12,7 Go |
| Données sources | Google Drive : `IPSSI/Cours_1_DATALAKE_DATAWAREHOUSE/TP3_retail/data/<table>/<fichier>.dat` |
| Dossier de travail | `/content/tp3` (temporaire, effacé à la fin de la session Colab) |
| Sauvegarde des résultats | Google Drive : `TP3_retail/resultats/` |
| Bibliothèques | `pyspark` (traitements), `pandas` (affichage des tableaux de synthèse) |

## Configuration de la session Spark

| Paramètre | Valeur | Raison |
|---|---|---|
| `appName` | `TP3-Retail-Intelligence` | Identifier l'application |
| `master` | `local[*]` | Utiliser tous les processeurs de la machine Colab |
| `spark.sql.ansi.enabled` | `false` | Une valeur non convertible devient `null` (elle est **comptée**) au lieu d'arrêter le traitement |
| `spark.sql.session.timeZone` | `Europe/Paris` | Fuseau horaire des dates Spark |

Une **seule** session Spark est créée et réutilisée dans tout le notebook ; elle est arrêtée à la fin (`spark.stop()`).

## Écart avec l'environnement du Jour 2 (solution de repli)

| | Jour 2 | Jour 3 |
|---|---|---|
| Stockage | HDFS 3.5.0 (WSL, mono-nœud) | Google Drive + disque local de Colab |
| Accès aux sources | `hdfs://localhost:9000/retail-lake/raw/...` | `/content/drive/MyDrive/.../TP3_retail/data/...` |

**Raison :** Colab est une machine distante, sans accès au HDFS de mon PC. **Équivalence des données :** ce sont les mêmes fichiers `.dat` du kit `retail_project`, avec les mêmes tailles en octets (`store_sales.dat` : 92 764 700 octets) et le même nombre de lignes que l'inventaire du Jour 1.

**Remarque :** les heures affichées dans le journal d'exécution et dans `_date_traitement` sont celles de la machine Colab, en **UTC** (1 h de moins que l'heure de Paris).
