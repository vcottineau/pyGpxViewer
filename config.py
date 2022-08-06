import os
from pathlib import Path


from dotenv import load_dotenv


load_dotenv(str(Path(__file__).resolve().parent) + "/.env")


class Config(object):
    PROGRAM_NAME = "pyGpxViewer"
    VERSION = "1.0"
    MAPBOX_API_KEY = os.environ.get("MAPBOX_API_KEY")
