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
import sqlite3
from contextlib import contextmanager

import pygpxviewer.config as config


class SQLiteHelper:
    """Helper to handle CRUD statements on a sqlite database."""

    def __init__(self):
        sql = """
            CREATE TABLE IF NOT EXISTS gpx (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL,
                points INTEGER,
                length REAL,
                up_hill REAL,
                down_hill REAL
            );
        """
        with self._db_cur() as cur:
            cur.execute(sql)

    def clear_records(self):
        """Clear all records of the database."""
        sql = "DELETE from gpx"
        with self._db_cur() as cur:
            cur.execute(sql)

    def add_record(self, record: tuple) -> None:
        """Add a single record to the database.

        :param record: Single record
        :type record: tuple
        """
        sql = """
            INSERT INTO gpx(path,points,length,up_hill,down_hill)
                VALUES(?,?,?,?,?)
        """
        with self._db_cur() as cur:
            cur.execute(sql, record)

    def add_records(self, records: tuple) -> None:
        """Add many records to the database.

        :param records: List of records
        :type records: tuple
        """
        sql = """
            INSERT INTO gpx(path,points,length,up_hill,down_hill)
                VALUES(?,?,?,?,?)
        """
        with self._db_cur() as cur:
            cur.executemany(sql, records)

    def update_record(self, id: int, record: tuple) -> None:
        """Update a single record based on his id.

        :param id: Id of the record
        :type id: int
        :param record: Single record
        :type record: tuple
        """
        sql = f"""
            UPDATE gpx
            SET
                points = {record[1]},
                length = {record[2]},
                up_hill = {record[3]},
                down_hill = {record[4]}
            WHERE
                id = '{id}'
        """
        with self._db_cur() as cur:
            cur.execute(sql)

    def get_records(self) -> tuple:
        """Get all records.

        :returns: List of records
        :rtype: tuple
        """
        sql = """
            SELECT * FROM gpx
            ORDER BY
                gpx.path
        """
        with self._db_cur() as cur:
            cur.execute(sql)
            records = cur.fetchall()
        return records

    def search_records(self, search_entry: str) -> tuple:
        """Get records with a text filter.

        :param search_entry:
        :type search_entry: str
        :returns: List of records
        :rtype: tuple
        """
        sql = f"""
            SELECT * FROM gpx
            WHERE
                gpx.path LIKE '%{search_entry}%'
            ORDER BY
                gpx.path
        """
        with self._db_cur() as cur:
            cur.execute(sql)
            records = cur.fetchall()
        return records

    @contextmanager
    def _db_cur(self):
        conn = sqlite3.connect(config.db_file)
        cur = conn.cursor()
        yield cur
        conn.commit()
        conn.close()
