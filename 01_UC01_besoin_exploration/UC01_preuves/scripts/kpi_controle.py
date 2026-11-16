"""Calcule des valeurs de contrôle des KPI sur le lot initial data/ (preuve de faisabilité).
Usage : python kpi_controle.py <dossier retail_project> <fichier sortie csv>"""
import sys, os, duckdb, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema_tpcxbb import SCHEMA
root, out = sys.argv[1], sys.argv[2]
con = duckdb.connect()
for t in ["store_sales","web_sales","store_returns","web_returns","date_dim","inventory","product_reviews","web_clickstreams"]:
    con.execute(f"CREATE VIEW {t} AS SELECT * FROM read_csv('{root}/data/{t}/{t}.dat',delim='|',header=false,quote='',escape='',names={SCHEMA[t]},sample_size=-1)")
K = [
 ("KPI-01 CA net magasin (somme ss_net_paid)", "SELECT round(sum(ss_net_paid),2) FROM store_sales"),
 ("KPI-01 CA net web (somme ws_net_paid)", "SELECT round(sum(ws_net_paid),2) FROM web_sales"),
 ("KPI-02 Quantités vendues magasin", "SELECT sum(ss_quantity) FROM store_sales"),
 ("KPI-02 Quantités vendues web", "SELECT sum(ws_quantity) FROM web_sales"),
 ("KPI-03 Transactions magasin (tickets distincts)", "SELECT count(DISTINCT ss_ticket_number) FROM store_sales"),
 ("KPI-03 Transactions web (commandes distinctes)", "SELECT count(DISTINCT ws_order_number) FROM web_sales"),
 ("KPI-04 Panier moyen magasin", "SELECT round(sum(ss_net_paid)/count(DISTINCT ss_ticket_number),2) FROM store_sales"),
 ("KPI-04 Panier moyen web", "SELECT round(sum(ws_net_paid)/count(DISTINCT ws_order_number),2) FROM web_sales"),
 ("KPI-05 Taux de remise magasin (%)", "SELECT round(100*sum(ss_ext_discount_amt)/sum(ss_ext_list_price),2) FROM store_sales"),
 ("KPI-05 Taux de remise web (%)", "SELECT round(100*sum(ws_ext_discount_amt)/sum(ws_ext_list_price),2) FROM web_sales"),
 ("KPI-06 Évolution CA total 2004 vs 2003 (%)", """WITH a AS (SELECT d_year y, sum(ss_net_paid) ca FROM store_sales JOIN date_dim ON ss_sold_date_sk=d_date_sk GROUP BY 1
      UNION ALL SELECT d_year, sum(ws_net_paid) FROM web_sales JOIN date_dim ON ws_sold_date_sk=d_date_sk GROUP BY 1),
      b AS (SELECT y, sum(ca) ca FROM a GROUP BY 1)
      SELECT round(100*((SELECT ca FROM b WHERE y=2004)/(SELECT ca FROM b WHERE y=2003)-1),2)"""),
 ("KPI-07 Part du web dans le CA total (%)", "SELECT round(100*(SELECT sum(ws_net_paid) FROM web_sales)/((SELECT sum(ws_net_paid) FROM web_sales)+(SELECT sum(ss_net_paid) FROM store_sales)),2)"),
 ("KPI-08 Taux de retour en quantité magasin (%)", "SELECT round(100*(SELECT sum(sr_return_quantity) FROM store_returns)/(SELECT sum(ss_quantity) FROM store_sales),2)"),
 ("KPI-08 Taux de retour en quantité web (%)", "SELECT round(100*(SELECT sum(wr_return_quantity) FROM web_returns)/(SELECT sum(ws_quantity) FROM web_sales),2)"),
 ("KPI-09 Montant des retours magasin (somme sr_return_amt)", "SELECT round(sum(sr_return_amt),2) FROM store_returns"),
 ("KPI-09 Montant des retours web (somme wr_return_amt)", "SELECT round(sum(wr_return_amt),2) FROM web_returns"),
 ("KPI-10 Marge nette magasin (somme ss_net_profit)", "SELECT round(sum(ss_net_profit),2) FROM store_sales"),
 ("KPI-10 Marge nette web (somme ws_net_profit)", "SELECT round(sum(ws_net_profit),2) FROM web_sales"),
 ("KPI-11 Stock moyen par article/entrepôt/relevé", "SELECT round(avg(inv_quantity_on_hand),1) FROM inventory"),
 ("KPI-12 Note moyenne des avis (1 à 5)", "SELECT round(avg(pr_review_rating),2) FROM product_reviews"),
 ("KPI-13 Part des clics associés à une vente (%)", "SELECT round(100*count(wcs_sales_sk)/count(*),2) FROM web_clickstreams"),
]
rows = [(k, con.execute(s).fetchone()[0]) for k, s in K]
pd.DataFrame(rows, columns=["indicateur", "valeur_controle_lot_data"]).to_csv(out, index=False)
for r in rows: print(r)
