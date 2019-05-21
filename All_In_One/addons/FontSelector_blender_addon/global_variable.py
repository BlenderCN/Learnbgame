extensions = [".otf", ".otc", ".ttf", ".ttc", ".tte", ".pfb", ".dfont", ".OTF", ".OTC", ".TTF", ".TTC", ".TTE", ".DFONT", ".PFB"]

#font selector files
fav_list = "fontselector_favorites"
font_list = "fontselector_fontlist"
filter_list = "fontselector_filter"
subdir_list = "fontselector_subdir"
size_file = "fontselector_size_"

json_file = "fontselector.json"
json_font_folders = "font_folders.json"
json_favorites = "font_favorites.json"

#fontselector fonts path
import os
script_file = os.path.realpath(__file__)

ress_path = os.path.join(os.path.dirname(script_file), "ress")
warning_font_path = os.path.join(ress_path, "FontSelector_Warning_Font.otf")