# Légendes des preuves UC-04

Chaque capture porte un titre et une phrase qui dit **ce qu'elle démontre**. Vérifie les numéros, puis renomme tes captures avec les noms proposés.

⚠️ Aucune capture ne doit montrer les identifiants NiFi : floute-les ou retire la capture.

## configuration/

| Nom de fichier proposé | Ce que la capture montre | Ce qu'elle démontre |
|---|---|---|
| `18_nifi_status_up.png` | `nifi.sh status` → UP | Service NiFi 2.12.0 démarré |
| `19_interface_nifi.png` | Canevas NiFi dans le navigateur | Interface accessible sur `https://localhost:8443/nifi` |
| `20_puthdfs_disponible.png` | Recherche « PutHDFS » : 1 of 304 | Composants Hadoop ajoutés et reconnus |
| `21_getfile_proprietes.png` | Propriétés de GetFile | Dossier source `/data/nifi/input`, Keep Source File = false |
| `22_puthdfs_proprietes.png` | Propriétés de PutHDFS | Configuration Hadoop, destination `/retail-lake/raw/nifi`, Conflict Resolution = fail |
| `23_flux_complet.png` | GetFile → PutHDFS → LogAttribute | Schéma du flux et relations success / failure |
| `flux_nifi_getfile_puthdfs.json` | Export *Download Flow Definition* | Configuration complète, réimportable, sans secret |

## execution/

| Nom de fichier proposé | Ce que la capture montre | Ce qu'elle démontre |
|---|---|---|
| `24_flux_demarre.png` | Processeurs en vert (Running) | Démarrage du flux |
| `25_compteurs_files.png` | Compteurs In/Out, files d'attente | Traitement effectif du FlowFile |
| `26_store_dat_hdfs.png` | `hdfs dfs -ls -h /retail-lake/raw/nifi` + `ls /data/nifi/input` vide | **Fichier présent dans HDFS** (3,3 K, 15:25) ; source prise en charge |

## provenance/

| Nom de fichier proposé | Ce que la capture montre | Ce qu'elle démontre |
|---|---|---|
| `28_provenance_details.png` | *Data Provenance* : SEND puis DROP par PutHDFS, uuid `b594c312…` | Le fichier `store.dat` a bien été envoyé vers HDFS à 15:25:20, puis le parcours s'est terminé normalement (success) |

## erreurs/

| Nom de fichier proposé | Ce que la capture montre | Ce qu'elle démontre |
|---|---|---|
| `29_erreur_dossier_inexistant.png` | GetFile avec un triangle jaune : « Directory does not exist » | Test d'erreur contrôlé : un dossier source erroné est détecté par NiFi. Correction : retour à `/data/nifi/input` |

Diagnostic et correction : voir `UC04_ingestion_NiFi.pdf`, partie « Erreurs et corrections ».
