from app.db import connect

# 既有库缺列时补齐（新库由下方 CREATE TABLE 一次带齐）。
CALC_RUN_COLUMNS = {
    "bleed_mm": "ALTER TABLE calc_runs ADD COLUMN bleed_mm REAL NOT NULL DEFAULT 0",
    "eff_length": "ALTER TABLE calc_runs ADD COLUMN eff_length REAL",
    "eff_width": "ALTER TABLE calc_runs ADD COLUMN eff_width REAL",
    "eff_height": "ALTER TABLE calc_runs ADD COLUMN eff_height REAL",
    "paper_m2": "ALTER TABLE calc_runs ADD COLUMN paper_m2 REAL",
}


def _ensure_calc_run_columns(c):
    have = {r["name"] for r in c.execute("PRAGMA table_info(calc_runs)").fetchall()}
    for name, ddl in CALC_RUN_COLUMNS.items():
        if name not in have:
            c.execute(ddl)


def init_db():
    c = connect()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS boxes(id INTEGER PRIMARY KEY,name TEXT,length REAL,width REAL,height REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS papers(id INTEGER PRIMARY KEY,name TEXT,roll_width REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE IF NOT EXISTS calc_runs(id INTEGER PRIMARY KEY AUTOINCREMENT,box_id INT,overlap REAL,bleed_mm REAL NOT NULL DEFAULT 0,eff_length REAL,eff_width REAL,eff_height REAL,paper_m2 REAL,result_json TEXT,note TEXT,created_at TEXT);
    """)
    _ensure_calc_run_columns(c)
    c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES ('overlap','1.15'),('bleed_mm','0')")
    if c.execute("SELECT COUNT(*) c FROM boxes").fetchone()["c"] == 0:
        c.executemany("INSERT INTO boxes(name,length,width,height,data_quality,note) VALUES (?,?,?,?,?,?)",[
            ("书型盒",0.30,0.20,0.15,"clean",""),
            ("方形礼盒",0.25,0.25,0.10,"clean",""),
            ("脏数据-负高",0.2,0.2,-0.1,"dirty","高度负"),
        ])
        c.executemany("INSERT INTO papers(name,roll_width,data_quality,note) VALUES (?,?,?,?)",[
            ("哑光纸1.0m",1.0,"clean",""),
            ("牛皮纸0.7m",0.7,"clean",""),
        ])
    c.commit()
    c.close()
