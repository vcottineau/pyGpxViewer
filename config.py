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

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(str(Path(__file__).resolve().parent) + "/.env")


class Config(object):
    PROGRAM_NAME = "pyGpxViewer"
    APPLICATION_ID = "com.github.pygpxviewer"
    VERSION = "1.0"
    MAPBOX_API_KEY = os.environ.get("MAPBOX_API_KEY")


HOME_CACHE_FOLDER = Path.home().joinpath(".cache", Config.APPLICATION_ID)
HOME_CONFIG_FOLDER = Path.home().joinpath(".config", Config.APPLICATION_ID)
HOME_DATA_FOLDER = Path.home().joinpath(".local", "share", Config.APPLICATION_ID)

for path in [HOME_CACHE_FOLDER, HOME_CONFIG_FOLDER, HOME_DATA_FOLDER]:
    path.mkdir(parents=True, exist_ok=True)
