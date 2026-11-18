# Légendes des preuves UC-03

Chaque capture porte un titre et une phrase qui dit **ce qu'elle démontre**. Les numéros sont ceux de la séance du 17/11 : vérifie qu'ils correspondent bien à tes fichiers et renomme chaque capture avec le nom proposé.

## environnement/

| Nom de fichier proposé | Ce que la capture montre | Ce qu'elle démontre |
|---|---|---|
| `01_wsl_ubuntu.png` | `wsl -l -v` / `lsb_release -a` | Ubuntu 24.04.3 sous WSL 2 |
| `02-05_java.png` | `java -version`, versions 17 et 21 installées | Java 17 pour Hadoop, Java 21 pour NiFi |
| `06_hadoop_version.png` | `hadoop version` | Hadoop 3.5.0 installé |
| `07a_configuration.png` | `core-site.xml` et `hdfs-site.xml` | HDFS sur `localhost:9000`, réplication 1, dossiers de données |
| `07_format_namenode.png` | « successfully formatted » | Initialisation unique du NameNode |
| `08_jps.png` | `jps` | NameNode, DataNode et SecondaryNameNode actifs |

## hdfs/

| Nom de fichier proposé | Ce que la capture montre | Ce qu'elle démontre |
|---|---|---|
| `09_dfsadmin_report.png` | `hdfs dfsadmin -report` | 1 DataNode en service, capacité disponible, HDFS opérationnel |
| `10_interface_9870.png` | Interface web du NameNode | Service HDFS joignable, état « active » |
| `13_store_sales_local.png` | Taille, lignes, `head` du fichier local | Fichier source inspecté avant le dépôt |
| `14_put_store_sales.png` | `hdfs dfs -put` + `hdfs dfs -ls -h` | Dépôt d'un fichier dans HDFS, présence, taille, permissions |
| `15_md5_lecture.png` | `md5sum` local et `hdfs dfs -cat … | md5sum` | **Lecture depuis HDFS** et intégrité : empreintes identiques |
| `16_count_du.png` | `hdfs dfs -count` / `du -s -h` | 977,0 Mo + 9,1 Mo déposés, conformes au cours et au Jour 1 |
| `17_23_domaines.png` | `hdfs dfs -ls …/initial` | Les 23 domaines présents |
| `17b_apres_redemarrage.png` | Même liste après le redémarrage de WSL | Persistance des données dans HDFS |

Fichier joint : `commandes_hdfs.txt`, la sortie brute de toutes les commandes.

## data_lake/

| Nom de fichier proposé | Ce que la capture montre | Ce qu'elle démontre |
|---|---|---|
| `11_mkdir_arborescence.png` | `hdfs dfs -mkdir -p` des zones | Création des répertoires raw, bronze, silver, gold, quality et logs |
| `12_ls_R_retail_lake.png` | `hdfs dfs -ls -R /retail-lake` | Arborescence du Data Lake effectivement créée |

Le schéma de l'arborescence figure dans `UC03_Hadoop_HDFS.pdf`, partie 4.
