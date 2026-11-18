# Questions de recul – Jour 3 (§11)

**1. Pourquoi est-il nécessaire de vérifier les schémas avant de commencer les transformations ?**
Parce qu'un calcul sur une colonne mal typée donne un résultat faux, ou n'est même pas possible. Une somme sur un montant lu comme du texte échoue, et un identifiant lu comme un nombre décimal ne se joint plus correctement. Dans ce TP, les fichiers n'ont pas d'en-tête : les noms de colonnes viennent du schéma de référence. On a donc vérifié que **chaque ligne contient exactement le nombre de colonnes attendu**, puis converti chaque colonne **explicitement**, en comptant les échecs de conversion (0).

**2. Quelle différence existe entre une donnée brute, une donnée Silver et une donnée Gold ?**
- La donnée **brute** est le fichier reçu, conservé tel quel : `store_sales.dat`, texte sans en-tête.
- La donnée **Silver** est la même donnée rendue **fiable** : colonnes nommées et typées, contrôles appliqués, anomalies isolées, provenance ajoutée. Le niveau de détail ne change pas (une ligne par ligne de ticket).
- La donnée **Gold** est **préparée pour un usage précis** : agrégée selon une granularité choisie (magasin × mois), avec des indicateurs calculés (CA, panier moyen), une finalité et des limites documentées.

**3. Pourquoi faut-il connaître la granularité d'une table avant de réaliser une agrégation ?**
Pour savoir **ce que l'on compte**. Dans `store_sales`, une ligne est un **article sur un ticket**, pas une transaction : il y a en moyenne 7,49 lignes par ticket. Compter les lignes pour obtenir des « ventes » surestimerait les transactions de 7,5 fois, et le panier moyen serait faux. On compte donc les tickets distincts. De même, sans connaître le grain, on prendrait les 4 136 lignes ticket + article répétées pour des doublons, alors que ce sont des lignes différentes.

**4. Quels risques présente une jointure réalisée sur une clé supposée ?**
- Si la clé n'est **pas unique** dans la table jointe, chaque vente est **dupliquée** autant de fois qu'il y a de correspondances : le CA est gonflé.
- Si la clé ne correspond pas, ou si les types diffèrent, des ventes **disparaissent** (jointure interne) ou restent **vides** (jointure gauche).
- Deux colonnes qui portent le même nom ne prouvent pas une relation.

Ici, on a vérifié l'unicité des clés des référentiels, puis compté les lignes avant et après chaque jointure (667 579 → 667 579) et les lignes non rapprochées (0).

**5. Pourquoi ne faut-il pas supprimer automatiquement les valeurs atypiques ?**
Parce qu'une valeur atypique n'est **pas forcément une erreur**. La marge négative sur 74,3 % des lignes peut correspondre à des ventes à perte ou à des remises. Les supprimer ferait disparaître les trois quarts des ventes et fausserait complètement le CA. On les **conserve**, on les **signale** et on documente la limite. Les cas douteux sont mis en **quarantaine**, pas supprimés, pour pouvoir être analysés.

**6. Quels contrôles permettent de vérifier la cohérence d'un jeu de données transformé ?**
- **Volumes :** lignes lues = doublons retirés + quarantaine + Silver.
- **Jointures :** même nombre de lignes avant et après, 0 ligne non rapprochée.
- **Réconciliation :** le CA de Gold est égal à celui de Silver ; le nombre de tickets est égal au nombre de tickets distincts.
- **Contrôle indépendant :** le CA est égal au KPI-01 du Jour 1, calculé avec un autre outil.
- **Cohérence interne :** quantité × prix = montant.
- **Relecture :** le Parquet relu a le même schéma et le même nombre de lignes.

**7. Pourquoi Parquet est-il adapté aux usages analytiques ?**
Parquet range les données **par colonne**, **compressées** et **typées**. Une analyse n'utilise souvent que quelques colonnes : Spark ne lit que celles-là (2 sur 26 dans notre test). Les fichiers sont plus petits (`store_sales` : 88,5 Mo → environ 44 Mo), et les types sont conservés, donc il n'y a pas besoin de re-convertir à chaque lecture.

**8. Pourquoi Parquet seul ne fournit-il pas les garanties d'une table transactionnelle Lakehouse ?**
Parquet ne fait qu'**enregistrer des fichiers**. Il ne gère ni les **transactions** (une écriture interrompue peut laisser une table à moitié écrite), ni l'**historique des versions**, ni l'**évolution contrôlée du schéma**, ni les **écritures simultanées**. Ces garanties viennent d'un **format de table** (Delta Lake, Iceberg, Hudi) qui ajoute un journal des transactions au-dessus des fichiers Parquet. Un Lakehouse n'est donc pas un Data Lake dans lequel on dépose des fichiers Parquet.

**9. Dans quels cas une base NoSQL pourrait-elle compléter une architecture Data Lake ?**
Quand il faut des **accès rapides par clé**, en temps réel, que le Data Lake (conçu pour des analyses sur de gros volumes) ne fournit pas. Pour Retail Intelligence, par exemple :
- un **historique d'événements par client** (base orientée colonnes comme HBase, avec une Row Key client + date) pour afficher son parcours instantanément ;
- un **profil client** ou une **fiche produit** consultés par une application (base documents) ;
- des **recommandations** « clients qui ont acheté ceci » (base graphe).

Le Data Lake reste la source de référence et le lieu des analyses ; la base NoSQL sert une application précise.

**10. Quelles limites des données TPCx-BB doivent être prises en compte lors de l'interprétation des résultats ?**
- Les données sont **synthétiques**, générées pour un test de performance : elles ne décrivent pas une réalité commerciale. Par exemple, les 12 magasins ont des CA très proches et 74 % des lignes sont à marge négative.
- La **période est partielle** : ventes du 01/01/2001 au 13/12/2005, donc 2005 est incomplète. Seul le lot `data/` a été traité.
- La **répartition par catégorie reflète la taille du catalogue** : Music représente 46 % des articles et 45 % du CA.
- Il manque des informations pour certaines analyses : pas de numéro de ligne de ticket, pas de groupe témoin pour les promotions (Jour 1), retours non déduits du CA.

Conclusion : les résultats valident la **chaîne technique**, mais ne doivent pas être présentés comme des constats commerciaux réels.
