"""
TP J1 - Retail Intelligence - UC-01 : exploration et qualification des données TPCx-BB.

Usage :   pip install duckdb pandas openpyxl
          python explore.py <dossier retail_project> <dossier de sortie>

Produit (dans le dossier de sortie) :
  - inventaire_fichiers.csv  : 1 ligne par fichier (chemin, taille, lignes, colonnes, format...)
  - profil_colonnes.csv      : 1 ligne par colonne (type observé, nulls, distincts, min, max)
  - controles_cles.csv       : unicité des clés candidates
  - controles_relations.csv  : jointures testées (orphelins = valeurs sans correspondance)
  - controles_metier.csv     : contrôles de cohérence (plages de dates, montants négatifs...)
"""
import os, sys, time
import duckdb, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema_tpcxbb import SCHEMA, DOMAINE, TYPE_TABLE

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "retail_project")
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else "resultats_exploration")
os.makedirs(OUT, exist_ok=True)
con = duckdb.connect()
con.execute("SET threads TO 2")

def human(n):
    for u in ["o", "Ko", "Mo", "Go"]:
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} To"

def line_ending(path):
    with open(path, "rb") as f:
        chunk = f.read(65536)
    return "CRLF (Windows)" if b"\r\n" in chunk else "LF (Unix)"

def encoding(path):
    with open(path, "rb") as f:
        data = f.read(5_000_000)
    try:
        data.decode("ascii"); return "ASCII"
    except UnicodeDecodeError:
        try: data.decode("utf-8"); return "UTF-8 (caractères non ASCII présents)"
        except UnicodeDecodeError: return "Non UTF-8"

def view_name(lot, table): return f"{lot}__{table}"

inventaire, profil = [], []
for lot in ["data", "data_refresh"]:
    base = os.path.join(ROOT, lot)
    if not os.path.isdir(base): continue
    for table in sorted(os.listdir(base)):
        for fname in sorted(os.listdir(os.path.join(base, table))):
            path = os.path.join(base, table, fname)
            rel = os.path.relpath(path, os.path.dirname(ROOT))
            size = os.path.getsize(path)
            if fname.endswith(".csv"):
                with open(path, encoding="utf-8", errors="replace") as f:
                    nlines = sum(1 for _ in f)
                inventaire.append(dict(lot=lot, table=table, fichier=fname, chemin=rel, format="CSV (fichier d'audit, en-tête + texte libre)",
                    separateur=",", en_tete="Oui", encodage=encoding(path), fin_de_ligne=line_ending(path),
                    taille_octets=size, taille=human(size), nb_lignes=nlines, nb_colonnes="variable",
                    domaine="Audit de génération (métadonnées)", type_table="Métadonnées", source="TPCx-BB (kit fourni)"))
                continue
            cols = SCHEMA[table]
            t0 = time.time()
            cols_sql = "{" + ", ".join(f"'{c}': 'VARCHAR'" for c in cols) + "}"
            # 1) lecture brute en texte pour mesurer les vides
            con.execute(f"""CREATE OR REPLACE TABLE raw AS SELECT * FROM read_csv('{path}', delim='|', header=false,
                           quote='', escape='', columns={cols_sql}, null_padding=false)""")
            n = con.execute("SELECT count(*) FROM raw").fetchone()[0]
            # 2) lecture avec détection automatique des types (= ce que verrait un outil)
            con.execute(f"""CREATE OR REPLACE VIEW {view_name(lot, table)} AS SELECT * FROM read_csv('{path}', delim='|', header=false,
                           quote='', escape='', names={cols}, sample_size=-1)""")
            types = dict(con.execute(f"DESCRIBE {view_name(lot, table)}").fetchall() and
                         [(r[0], r[1]) for r in con.execute(f"DESCRIBE {view_name(lot, table)}").fetchall()])
            for c in cols:
                q = f"""SELECT count(*) FILTER (WHERE "{c}" IS NULL OR trim("{c}")=''),
                               approx_count_distinct("{c}"),
                               min(TRY_CAST("{c}" AS DOUBLE)), max(TRY_CAST("{c}" AS DOUBLE)),
                               min("{c}"), max("{c}"),
                               any_value("{c}") FILTER (WHERE "{c}" IS NOT NULL AND trim("{c}")<>'')
                        FROM raw"""
                nul, dist, mn, mx, smin, smax, ex = con.execute(q).fetchone()
                t = types.get(c, "?")
                numeric = t in ("BIGINT", "INTEGER", "DOUBLE", "SMALLINT", "TINYINT") or t.startswith("DECIMAL")
                ex = (ex[:60] + "…") if ex and len(ex) > 60 else ex
                profil.append(dict(lot=lot, table=table, colonne=c, position=cols.index(c) + 1, type_observe=t,
                    nb_lignes=n, nb_vides=nul, pct_vides=round(100 * nul / n, 2) if n else None,
                    nb_distincts_approx=dist, min=(mn if numeric else (smin[:30] if smin else None)),
                    max=(mx if numeric else (smax[:30] if smax else None)), exemple=ex))
            inventaire.append(dict(lot=lot, table=table, fichier=fname, chemin=rel, format="Texte délimité .dat (sans en-tête)",
                separateur="|", en_tete="Non", encodage=encoding(path), fin_de_ligne=line_ending(path),
                taille_octets=size, taille=human(size), nb_lignes=n, nb_colonnes=len(cols),
                domaine=DOMAINE.get(table, "?"), type_table=TYPE_TABLE.get(table, "Dimension / référentiel"),
                source="TPCx-BB (kit fourni)"))
            print(f"{lot}/{table}: {n:,} lignes, {len(cols)} col. ({time.time()-t0:.1f}s)", flush=True)

pd.DataFrame(inventaire).to_csv(f"{OUT}/inventaire_fichiers.csv", index=False)
pd.DataFrame(profil).to_csv(f"{OUT}/profil_colonnes.csv", index=False)

# ---------- Contrôles de clés (unicité) ----------
V = lambda t, lot="data": view_name(lot, t)
cles = [("customer", "c_customer_sk"), ("customer_address", "ca_address_sk"), ("customer_demographics", "cd_demo_sk"),
        ("household_demographics", "hd_demo_sk"), ("income_band", "ib_income_band_sk"), ("date_dim", "d_date_sk"),
        ("time_dim", "t_time_sk"), ("item", "i_item_sk"), ("item", "i_item_id"), ("store", "s_store_sk"),
        ("warehouse", "w_warehouse_sk"), ("promotion", "p_promo_sk"), ("reason", "r_reason_sk"), ("ship_mode", "sm_ship_mode_sk"),
        ("web_page", "wp_web_page_sk"), ("web_site", "web_site_sk"), ("product_reviews", "pr_review_sk"),
        ("item_marketprices", "imp_sk"),
        ("store_sales", "ss_ticket_number, ss_item_sk"), ("web_sales", "ws_order_number, ws_item_sk"),
        ("store_returns", "sr_ticket_number, sr_item_sk"), ("web_returns", "wr_order_number, wr_item_sk"),
        ("inventory", "inv_date_sk, inv_item_sk, inv_warehouse_sk")]
rows = []
for t, k in cles:
    n, d, nulls = con.execute(f"""SELECT count(*), count(DISTINCT ({k})),
            count(*) FILTER (WHERE {' OR '.join(c.strip()+' IS NULL' for c in k.split(','))}) FROM {V(t)}""").fetchone()
    rows.append(dict(table=t, cle_candidate=k, nb_lignes=n, nb_valeurs_distinctes=d, nb_cles_nulles=nulls,
                     doublons=n - d, unique="Oui" if n == d and nulls == 0 else "Non"))
pd.DataFrame(rows).to_csv(f"{OUT}/controles_cles.csv", index=False)

# ---------- Contrôles de relations (intégrité référentielle) ----------
rels = [
 ("store_sales", "ss_sold_date_sk", "date_dim", "d_date_sk"), ("store_sales", "ss_sold_time_sk", "time_dim", "t_time_sk"),
 ("store_sales", "ss_item_sk", "item", "i_item_sk"), ("store_sales", "ss_customer_sk", "customer", "c_customer_sk"),
 ("store_sales", "ss_store_sk", "store", "s_store_sk"), ("store_sales", "ss_promo_sk", "promotion", "p_promo_sk"),
 ("store_sales", "ss_cdemo_sk", "customer_demographics", "cd_demo_sk"), ("store_sales", "ss_hdemo_sk", "household_demographics", "hd_demo_sk"),
 ("store_sales", "ss_addr_sk", "customer_address", "ca_address_sk"),
 ("web_sales", "ws_sold_date_sk", "date_dim", "d_date_sk"), ("web_sales", "ws_item_sk", "item", "i_item_sk"),
 ("web_sales", "ws_bill_customer_sk", "customer", "c_customer_sk"), ("web_sales", "ws_ship_customer_sk", "customer", "c_customer_sk"),
 ("web_sales", "ws_web_site_sk", "web_site", "web_site_sk"), ("web_sales", "ws_web_page_sk", "web_page", "wp_web_page_sk"),
 ("web_sales", "ws_warehouse_sk", "warehouse", "w_warehouse_sk"), ("web_sales", "ws_ship_mode_sk", "ship_mode", "sm_ship_mode_sk"),
 ("web_sales", "ws_promo_sk", "promotion", "p_promo_sk"),
 ("store_returns", "sr_item_sk", "item", "i_item_sk"), ("store_returns", "sr_store_sk", "store", "s_store_sk"),
 ("store_returns", "sr_reason_sk", "reason", "r_reason_sk"), ("store_returns", "sr_returned_date_sk", "date_dim", "d_date_sk"),
 ("store_returns", "sr_customer_sk", "customer", "c_customer_sk"),
 ("web_returns", "wr_item_sk", "item", "i_item_sk"), ("web_returns", "wr_reason_sk", "reason", "r_reason_sk"),
 ("web_returns", "wr_returned_date_sk", "date_dim", "d_date_sk"),
 ("inventory", "inv_item_sk", "item", "i_item_sk"), ("inventory", "inv_warehouse_sk", "warehouse", "w_warehouse_sk"),
 ("inventory", "inv_date_sk", "date_dim", "d_date_sk"),
 ("web_clickstreams", "wcs_item_sk", "item", "i_item_sk"), ("web_clickstreams", "wcs_user_sk", "customer", "c_customer_sk"),
 ("web_clickstreams", "wcs_web_page_sk", "web_page", "wp_web_page_sk"), ("web_clickstreams", "wcs_click_date_sk", "date_dim", "d_date_sk"),
 ("product_reviews", "pr_item_sk", "item", "i_item_sk"), ("product_reviews", "pr_user_sk", "customer", "c_customer_sk"),
 ("customer", "c_current_addr_sk", "customer_address", "ca_address_sk"), ("customer", "c_current_cdemo_sk", "customer_demographics", "cd_demo_sk"),
 ("customer", "c_current_hdemo_sk", "household_demographics", "hd_demo_sk"),
 ("household_demographics", "hd_income_band_sk", "income_band", "ib_income_band_sk"),
 ("item_marketprices", "imp_item_sk", "item", "i_item_sk"), ("promotion", "p_item_sk", "item", "i_item_sk"),
]
rows = []
for ft, fk, dt, pk in rels:
    tf, td = con.execute(f"SELECT typeof(any_value({fk})) FROM {V(ft)}").fetchone()[0], con.execute(f"SELECT typeof(any_value({pk})) FROM {V(dt)}").fetchone()[0]
    n, nn, orph, dorph = con.execute(f"""SELECT count(*), count(f.{fk}),
          count(*) FILTER (WHERE f.{fk} IS NOT NULL AND d.{pk} IS NULL),
          count(DISTINCT f.{fk}) FILTER (WHERE f.{fk} IS NOT NULL AND d.{pk} IS NULL)
        FROM {V(ft)} f LEFT JOIN (SELECT DISTINCT {pk} FROM {V(dt)}) d ON f.{fk} = d.{pk}""").fetchone()
    rows.append(dict(table_source=ft, colonne=fk, table_cible=dt, cle_cible=pk, type_source=tf, type_cible=td,
        nb_lignes=n, nb_vides=n - nn, pct_vides=round(100 * (n - nn) / n, 2), nb_orphelins=orph,
        pct_orphelins=round(100 * orph / nn, 2) if nn else None, nb_valeurs_orphelines_distinctes=dorph,
        cardinalite="N:1 (plusieurs lignes " + ft + " -> 1 ligne " + dt + ")"))
pd.DataFrame(rows).to_csv(f"{OUT}/controles_relations.csv", index=False)

# ---------- Contrôles métier ----------
def q1(sql): return con.execute(sql).fetchone()
rows = []
def add(ctrl, res, comm=""): rows.append(dict(controle=ctrl, resultat=res, commentaire=comm))
for t, dcol in [("store_sales", "ss_sold_date_sk"), ("web_sales", "ws_sold_date_sk"), ("store_returns", "sr_returned_date_sk"),
                ("web_returns", "wr_returned_date_sk"), ("inventory", "inv_date_sk"), ("web_clickstreams", "wcs_click_date_sk")]:
    for lot in ["data", "data_refresh"]:
        try:
            mn, mx, nd = q1(f"SELECT min(d.d_date), max(d.d_date), count(DISTINCT f.{dcol}) FROM {V(t, lot)} f JOIN {V('date_dim')} d ON f.{dcol}=d.d_date_sk")
            add(f"Période couverte {lot}/{t}", f"{mn} -> {mx}", f"{nd} dates distinctes")
        except Exception as e:
            pass
mn, mx = q1(f"SELECT min(d_date), max(d_date) FROM {V('date_dim')}"); add("Période date_dim (calendrier)", f"{mn} -> {mx}", "calendrier de référence, plus large que les faits")
add("store_sales : quantités <= 0", q1(f"SELECT count(*) FROM {V('store_sales')} WHERE ss_quantity <= 0")[0])
add("store_sales : quantité vide", q1(f"SELECT count(*) FROM {V('store_sales')} WHERE ss_quantity IS NULL")[0])
add("store_sales : ss_net_profit < 0 (ventes à perte)", q1(f"SELECT count(*) FROM {V('store_sales')} WHERE ss_net_profit < 0")[0],
    f"{q1(f'SELECT round(100*avg((ss_net_profit<0)::INT),1) FROM {V('store_sales')}')[0]} % des lignes")
add("store_sales : ext_sales_price = quantity x sales_price (écart > 0,01)",
    q1(f"SELECT count(*) FROM {V('store_sales')} WHERE abs(ss_ext_sales_price - ss_quantity*ss_sales_price) > 0.01")[0])
add("web_sales : ext_sales_price = quantity x sales_price (écart > 0,01)",
    q1(f"SELECT count(*) FROM {V('web_sales')} WHERE abs(ws_ext_sales_price - ws_quantity*ws_sales_price) > 0.01")[0])
add("store_sales : nb tickets distincts (ss_ticket_number)", q1(f"SELECT count(DISTINCT ss_ticket_number) FROM {V('store_sales')}")[0],
    f"lignes / ticket = {q1(f'SELECT round(count(*)/count(DISTINCT ss_ticket_number),2) FROM {V('store_sales')}')[0]}")
add("web_sales : nb commandes distinctes (ws_order_number)", q1(f"SELECT count(DISTINCT ws_order_number) FROM {V('web_sales')}")[0],
    f"lignes / commande = {q1(f'SELECT round(count(*)/count(DISTINCT ws_order_number),2) FROM {V('web_sales')}')[0]}")
add("store_sales : un ticket = un seul client / magasin / date ?",
    q1(f"""SELECT count(*) FROM (SELECT ss_ticket_number FROM {V('store_sales')} GROUP BY 1
          HAVING count(DISTINCT ss_store_sk)>1 OR count(DISTINCT ss_sold_date_sk)>1 OR count(DISTINCT ss_customer_sk)>1)""")[0],
    "nb de tickets incohérents")
add("store_returns : retours sans vente d'origine (ticket+article)",
    q1(f"""SELECT count(*) FROM {V('store_returns')} r LEFT JOIN (SELECT DISTINCT ss_ticket_number, ss_item_sk FROM {V('store_sales')}) s
          ON r.sr_ticket_number=s.ss_ticket_number AND r.sr_item_sk=s.ss_item_sk WHERE s.ss_ticket_number IS NULL""")[0],
    f"sur {q1(f'SELECT count(*) FROM {V('store_returns')}')[0]} lignes de retour")
add("web_returns : retours sans vente d'origine (commande+article)",
    q1(f"""SELECT count(*) FROM {V('web_returns')} r LEFT JOIN (SELECT DISTINCT ws_order_number, ws_item_sk FROM {V('web_sales')}) s
          ON r.wr_order_number=s.ws_order_number AND r.wr_item_sk=s.ws_item_sk WHERE s.ws_order_number IS NULL""")[0],
    f"sur {q1(f'SELECT count(*) FROM {V('web_returns')}')[0]} lignes de retour")
add("store_returns : retour antérieur à la vente",
    q1(f"""SELECT count(*) FROM {V('store_returns')} r JOIN {V('store_sales')} s ON r.sr_ticket_number=s.ss_ticket_number AND r.sr_item_sk=s.ss_item_sk
          WHERE r.sr_returned_date_sk < s.ss_sold_date_sk""")[0])
add("store_returns : quantité retournée > quantité vendue",
    q1(f"""SELECT count(*) FROM {V('store_returns')} r JOIN {V('store_sales')} s ON r.sr_ticket_number=s.ss_ticket_number AND r.sr_item_sk=s.ss_item_sk
          WHERE r.sr_return_quantity > s.ss_quantity""")[0])
add("web_clickstreams : clics liés à une vente (wcs_sales_sk renseigné)",
    q1(f"SELECT count(wcs_sales_sk) FROM {V('web_clickstreams')}")[0],
    f"{q1(f'SELECT round(100*count(wcs_sales_sk)/count(*),2) FROM {V('web_clickstreams')}')[0]} % des clics")
add("web_clickstreams : clics anonymes (wcs_user_sk vide)",
    q1(f"SELECT count(*) - count(wcs_user_sk) FROM {V('web_clickstreams')}")[0],
    f"{q1(f'SELECT round(100*(count(*)-count(wcs_user_sk))/count(*),2) FROM {V('web_clickstreams')}')[0]} % des clics")
add("product_reviews : notes (pr_review_rating) min / max / moyenne",
    str(q1(f"SELECT min(pr_review_rating), max(pr_review_rating), round(avg(pr_review_rating),2) FROM {V('product_reviews')}")))
add("item : nb catégories (i_category) distinctes", q1(f"SELECT count(DISTINCT i_category) FROM {V('item')}")[0],
    ", ".join(r[0] or "(vide)" for r in con.execute(f"SELECT DISTINCT i_category FROM {V('item')} ORDER BY 1").fetchall()))
add("store : nb magasins / états", str(q1(f"SELECT count(*), count(DISTINCT s_state) FROM {V('store')}")))
add("inventory : quantités en stock vides", q1(f"SELECT count(*)-count(inv_quantity_on_hand) FROM {V('inventory')}")[0])
add("inventory : fréquence des relevés (nb dates distinctes)", q1(f"SELECT count(DISTINCT inv_date_sk) FROM {V('inventory')}")[0], "photo périodique du stock, pas des mouvements")
add("data_refresh : clés en recouvrement avec data (customer)",
    q1(f"SELECT count(*) FROM {V('customer','data_refresh')} r JOIN {V('customer')} d ON r.c_customer_sk=d.c_customer_sk")[0],
    "0 = le refresh ajoute de nouvelles lignes (pas de mise à jour des existantes)")
add("data_refresh : clés en recouvrement avec data (item)",
    q1(f"SELECT count(*) FROM {V('item','data_refresh')} r JOIN {V('item')} d ON r.i_item_sk=d.i_item_sk")[0])
add("data_refresh/store_sales : ventes sur article absent de data/item",
    q1(f"SELECT count(*) FROM {V('store_sales','data_refresh')} s LEFT JOIN {V('item')} i ON s.ss_item_sk=i.i_item_sk WHERE i.i_item_sk IS NULL")[0],
    "à rapprocher de data_refresh/item")
pd.DataFrame(rows).to_csv(f"{OUT}/controles_metier.csv", index=False)
print("Terminé ->", OUT)
