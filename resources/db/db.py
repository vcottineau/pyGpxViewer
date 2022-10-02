#  MIT License
#
#  Copyright (c) 2022 Vincent Cottineau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
import json
import sqlite3
from pathlib import Path

Path("db.sqlite").unlink()
conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()

# DEM
sql = """
CREATE TABLE IF NOT EXISTS zip (
    id INTEGER PRIMARY KEY,
    folder TEXT NOT NULL,
    size INTEGER NOT NULL,
    link TEXT NOT NULL
);
"""
cur.execute(sql)

sql = """
CREATE TABLE IF NOT EXISTS dem (
    id INTEGER PRIMARY KEY,
    hgt TEXT NOT NULL,
    zip_id INTEGER NOT NULL,
    FOREIGN KEY (zip_id)
        REFERENCES zip (id) 
);
"""
cur.execute(sql)

sql = "CREATE INDEX index_dem ON dem (hgt)"
cur.execute(sql)

with open("../dem/dem.json") as json_file:
    dem = json.load(json_file)

records = []
for zip_folder in dem:
    sql = """
    INSERT INTO zip(folder, size, link)
        VALUES(?, ?, ?)
    """

    record = (zip_folder["name"], zip_folder["size"], zip_folder["link"])
    cur.execute(sql, record)

    for hgt_file in zip_folder["files"]:
        records.append(
            (hgt_file, cur.lastrowid)
        )

sql = """
INSERT INTO dem(hgt, zip_id)
    VALUES(?, ?)
"""
cur.executemany(sql, records)

# POI
sql = """
CREATE TABLE IF NOT EXISTS poi (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    link TEXT NOT NULL,
    lat REAL NOT NULL,
    lng REAL NOT NULL
);
"""
cur.execute(sql)

sql = "CREATE INDEX index_poi ON poi (type, lat, lng)"
cur.execute(sql)

with open("../poi/poi.json") as json_file:
    poi = json.load(json_file)

records = []
for poi in poi:
    records.append(
        (poi["name"], poi["type"], poi["link"], poi["lat"], poi["lng"],)
    )

sql = """
INSERT INTO poi(name, type, link, lat, lng)
    VALUES(?, ?, ?, ?, ?)
"""
cur.executemany(sql, records)

conn.commit()
conn.close()

src = Path("db.sqlite")
dest = Path("../../data/db/db.sqlite")
dest.write_bytes(src.read_bytes())
