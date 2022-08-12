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
