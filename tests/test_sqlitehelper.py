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

import pytest

from pygpxviewer.helpers.sqlitehelper import SQLiteHelper


class SQLiteHelperInMemory(SQLiteHelper):

    def __init__(self):
        super().__init__()

        self.clear_gpx_records()

    @contextmanager
    def _db_cur(self):
        conn = sqlite3.connect("tests/test_sqlitehelper.db")
        cur = conn.cursor()
        yield cur
        conn.commit()
        conn.close()


@pytest.fixture
def sqlite_helper_with_record():
    sqlite_helper = SQLiteHelperInMemory()
    sqlite_helper.add_gpx_record(
        ("path_01", 100, 25.0, 100.0, 100.0)
    )
    yield sqlite_helper


@pytest.fixture
def sqlite_helper_with_records():
    sqlite_helper = SQLiteHelperInMemory()
    sqlite_helper.add_gpx_records(
        [
            ("path_01", 100, 25.0, 100.0, 100.0),
            ("path_02", 200, 50.0, 200.0, 200.0)
        ])
    yield sqlite_helper


class TestSQLiteHelper:
    def test_creation(self):
        sqlite_helper = SQLiteHelperInMemory()
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        with sqlite_helper._db_cur() as cur:
            cur.execute(sql)
            res = cur.fetchall()
        assert "gpx" in res[0]

    def test_get_records(self, sqlite_helper_with_records):
        records = sqlite_helper_with_records.get_gpx_records()
        assert len(records) == 2

    def test_add_records(self, sqlite_helper_with_record):
        records = sqlite_helper_with_record.get_gpx_records()
        assert len(records) == 1

    def test_update_record(self, sqlite_helper_with_record):
        sqlite_helper_with_record.update_gpx_record(
            1, ("path_01", 200, 50.0, 200.0, 200.0)
        )
        records = sqlite_helper_with_record.get_gpx_records()
        assert records[0][1] == "path_01"
        assert records[0][2] == 200
        assert records[0][3] == 50.0
        assert records[0][4] == 200.0
        assert records[0][5] == 200.0

    def test_search_records(self, sqlite_helper_with_records):
        records = sqlite_helper_with_records.search_gpx_records("path_02")
        assert records[0][1] == "path_02"
        assert records[0][2] == 200
        assert records[0][3] == 50.0
        assert records[0][4] == 200.0
        assert records[0][5] == 200.0
