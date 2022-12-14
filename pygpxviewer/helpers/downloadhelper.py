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
import zipfile
from gettext import gettext as _
from pathlib import Path

import requests

from pygpxviewer import config
from pygpxviewer.logger import Logger

logger = Logger()


class DownloadHelper:
    """Helper to download files from the web."""

    def __init__(self, urls):
        self._urls = urls

    def get_size_in_mb(self) -> float:
        """Get the size in MB of all the zip folders in the url list.

        :return: size in MB
        :rtype: float
        """
        size = [int(url["size"]) for url in self._urls]
        return round(sum(size) / 1000 / 1000, 1)

    def fetch_urls(self):
        """Download and extract zip files from the web."""
        zip_path = config.dem_path.joinpath("tmp.zip")
        for url in self._urls:
            folder = url["folder"]
            link = url["link"]
            size = round(url['size'] / 1000 / 1000, 1)
            logger.info(_(f"Folder: {folder}, Size: {size} MB"))

            try:
                r = requests.get(link, allow_redirects=True)
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.warning(f"HTTPError occurred: {e}")
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"ConnectionError occurred: {e}")
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout occurred: {e}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"RequestException occurred: {e}")
            else:
                with open(zip_path, 'wb') as file:
                    file.write(r.content)
                    self._extract_zip(zip_path)

        if zip_path.is_file():
            zip_path.unlink()

    @staticmethod
    def _extract_zip(zip_path):
        with zipfile.ZipFile(zip_path) as z:
            filenames = [filename for filename in z.namelist() if Path(filename).suffix == ".hgt"]
            for filename in filenames:
                file_path = config.dem_path.joinpath(filename.split("/")[-1])
                with open(file_path, "wb") as f:
                    f.write(z.read(filename))
            logger.info(_(f"Files: {filenames}"))
