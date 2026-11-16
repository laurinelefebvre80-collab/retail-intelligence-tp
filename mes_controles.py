"""
TP J1 - Mes contrôles (Étapes C et D de l'UC-01)
Lancer :  py mes_controles.py C:\TP_J1\retail_project
Chaque bloc affiche un résultat à capturer (Win + Maj + S) pour le dossier preuves.
"""
import sys, duckdb
from schema_tpcxbb import SCHEMA

DOSSIER = sys.argv[1] if len(sys.argv) > 1 else r"C:\TP_J1\retail_project"
con = duckdb.connect()

def table(nom, lot="data"):
    """Crée une 'vue' SQL sur le fichier .dat : séparateur |, pas d'en-tête, noms de colonnes TPCx-BB."""
    chemin = f"{DOSSIER}/{lot}/{nom}/{nom}.dat"
    vue = nom if lot == "data" else f"refresh_{nom}"
    con.execute(f"CREATE OR REPLACE VIEW {vue} AS SELECT * FROM read_csv('{chemin}', delim='|', header=false, "
                f"quote='', escape='', names={SCHEMA[nom]}, sample_size=-1)")

def titre(t): print("\n" + "=" * 70 + "\n" + t + "\n" + "=" * 70)
def montre(sql): print(con.execute(sql).df().to_string(index=False))

for t in ["store_sales", "web_sales", "store_returns", "item", "customer", "store", "date_dim",
          "inventory", "web_clickstreams", "promotion"]:
    table(t)
table("item", "data_refresh")

titre("1. Aperçu de store_sales (5 premières lignes, quelques colonnes)")
montre("SELECT ss_sold_date_sk, ss_item_sk, ss_customer_sk, ss_store_sk, ss_ticket_number, ss_quantity, ss_sales_price, ss_net_paid FROM store_sales LIMIT 5")

titre("2. Types de colonnes détectés pour store_sales")
montre("SELECT column_name AS colonne, column_type AS type FROM (DESCRIBE store_sales)")

titre("3. Volumes : nombre de lignes par table")
montre("""SELECT 'store_sales' AS table_, count(*) AS nb_lignes FROM store_sales UNION ALL
          SELECT 'web_sales', count(*) FROM web_sales UNION ALL SELECT 'store_returns', count(*) FROM store_returns UNION ALL
          SELECT 'item', count(*) FROM item UNION ALL SELECT 'customer', count(*) FROM customer UNION ALL
          SELECT 'store', count(*) FROM store UNION ALL SELECT 'inventory', count(*) FROM inventory""")

titre("4. Unicité des clés : la clé est-elle unique ? (nb lignes = nb valeurs distinctes)")
montre("""SELECT 'item.i_item_sk' AS cle, count(*) AS nb_lignes, count(DISTINCT i_item_sk) AS nb_distincts FROM item UNION ALL
          SELECT 'customer.c_customer_sk', count(*), count(DISTINCT c_customer_sk) FROM customer UNION ALL
          SELECT 'store.s_store_sk', count(*), count(DISTINCT s_store_sk) FROM store UNION ALL
          SELECT 'store_sales (ticket+article)', count(*), count(DISTINCT (ss_ticket_number, ss_item_sk)) FROM store_sales""")

titre("5. Valeurs vides dans store_sales")
montre("""SELECT count(*) AS nb_lignes, count(*) - count(ss_customer_sk) AS client_vide, count(*) - count(ss_promo_sk) AS promo_vide,
          count(*) - count(ss_quantity) AS quantite_vide FROM store_sales""")

titre("6. Relation store_sales -> item : ventes dont l'article n'existe pas (orphelins)")
montre("SELECT count(*) AS ventes_orphelines FROM store_sales s LEFT JOIN item i ON s.ss_item_sk = i.i_item_sk WHERE i.i_item_sk IS NULL")

titre("7. Relation inventory -> item : lignes de stock orphelines")
montre("""SELECT count(*) AS lignes_orphelines, count(DISTINCT inv_item_sk) AS articles_concernes, min(inv_item_sk) AS cle_min, max(inv_item_sk) AS cle_max
          FROM inventory v LEFT JOIN item i ON v.inv_item_sk = i.i_item_sk WHERE i.i_item_sk IS NULL""")
print("-> Ces articles existent-ils dans data_refresh/item ?")
montre("SELECT min(i_item_sk) AS cle_min_refresh, max(i_item_sk) AS cle_max_refresh FROM refresh_item")

titre("8. Lignes de vente vs transactions (tickets)")
montre("""SELECT count(*) AS lignes_de_vente, count(DISTINCT ss_ticket_number) AS tickets,
          round(count(*) / count(DISTINCT ss_ticket_number), 2) AS lignes_par_ticket FROM store_sales""")

titre("9. Période couverte par les ventes")
montre("SELECT min(d_date) AS premiere_vente, max(d_date) AS derniere_vente FROM store_sales JOIN date_dim ON ss_sold_date_sk = d_date_sk")

titre("10. Clics web : anonymes et liés à une vente")
montre("""SELECT count(*) AS nb_clics, round(100.0 * (count(*) - count(wcs_user_sk)) / count(*), 2) AS pct_anonymes,
          round(100.0 * count(wcs_sales_sk) / count(*), 2) AS pct_lies_a_une_vente FROM web_clickstreams""")

titre("11. Promotions : part des ventes avec un code promo")
montre("SELECT round(100.0 * count(ss_promo_sk) / count(*), 2) AS pct_ventes_avec_promo FROM store_sales")

titre("12. Anomalie : dates de fermeture des magasins")
montre("SELECT s_store_name, s_closed_date_sk, d_date AS date_fermeture FROM store LEFT JOIN date_dim ON s_closed_date_sk = d_date_sk ORDER BY s_store_sk")

titre("13. KPI : CA net, transactions et panier moyen par canal")
montre("""SELECT 'magasin' AS canal, round(sum(ss_net_paid), 0) AS ca_net, count(DISTINCT ss_ticket_number) AS transactions,
                 round(sum(ss_net_paid) / count(DISTINCT ss_ticket_number), 2) AS panier_moyen FROM store_sales UNION ALL
          SELECT 'web', round(sum(ws_net_paid), 0), count(DISTINCT ws_order_number),
                 round(sum(ws_net_paid) / count(DISTINCT ws_order_number), 2) FROM web_sales""")
print("\nTerminé.")
