import os

DATA_DIR = "data"
SETTINGS_FILE = "settings.json"
MAGIC_DIR = "magic"
MAGIC_FILE = "magic.xml"
ALEX_BRUSH_FILE = "alexbrushregular.ttf"

SETTINGS_PATH = os.path.join(DATA_DIR, SETTINGS_FILE)
IMAGE_DIR = os.path.join(DATA_DIR, "images")
MUSIC_DIR = os.path.join(DATA_DIR, "music")
FONT_DIR = os.path.join(DATA_DIR, "fonts")
SOUND_DIR = os.path.join(DATA_DIR, "sounds")

MAGIC_PATH = os.path.join(os.path.join(DATA_DIR, MAGIC_DIR), MAGIC_FILE)
FONT_ALEX_BRUSH = os.path.join(FONT_DIR, ALEX_BRUSH_FILE)
