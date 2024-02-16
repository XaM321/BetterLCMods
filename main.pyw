# Imports
from elevate import elevate
elevate()

from win32api import GetFileVersionInfo, LOWORD, HIWORD
from zipfile import ZipFile, is_zipfile
from chardet import detect

from configparser import ConfigParser
from PIL import Image
import pickle
import shutil
import os

import customtkinter as ctk

from json import JSONDecoder
json = JSONDecoder()

# Constant Paths
CFG_PATH: str = "config.cfg"

parser = ConfigParser()
parser.read(filenames = CFG_PATH)

ACTIVE_PATH: str = parser.get(section = "settings", option = "active_mods")
with open(file = ACTIVE_PATH, mode = "a"): pass

LC_PATH: str = parser.get(section = "settings", option = "lc_path").replace("\\", "/")

if not os.path.isdir(path = LC_PATH): raise FileNotFoundError(f"Lethal Company path cannot be found at \"{LC_PATH}\"\n\nPlease edit config.cfg file.")
for file in os.listdir(path = LC_PATH):
      if "BepInEx" != file and "BepInEx" in file:
            os.rename(src = f"{LC_PATH}/{file}", dst = f"{LC_PATH}/BepInEx"); break

BEPINEX_PATH: str = f"{LC_PATH}/BepInEx"
OG_BEPINEX_PATH: str = BEPINEX_PATH
LC_BUNDLES: str = f"{BEPINEX_PATH}/Bundles"
LC_CONFIG: str = f"{BEPINEX_PATH}/config"
LC_PLUGIN: str = f"{BEPINEX_PATH}/plugins"

if not os.path.isdir(path = LC_BUNDLES): os.mkdir(path = LC_BUNDLES)
if not os.path.isdir(path = LC_CONFIG): os.mkdir(path = LC_CONFIG)
if not os.path.isdir(path = LC_PLUGIN): os.mkdir(path = LC_PLUGIN)

PLUGIN_PATH: str = "mods"
CONFIG_PATH: str = "config"
BUNDLES_PATH: str = "Bundles"

plugins: dict[str: dict[str: str]] = {}
buttons: dict[str: ctk.CTkCheckBox] = {}

# Window Setup
WIDTH: int = 1200
HEIGHT: int = 700

WIN: ctk.CTk = ctk.CTk()
WIN.geometry(geometry_string = f"{WIDTH}x{HEIGHT}")
# WIN.resizable(width = False, height = False)
WIN.title(string = "Lethal Company Mod Manager")

SIDEBAR: ctk.CTkFrame = ctk.CTkFrame(master = WIN, corner_radius = 0)
SIDEBAR.place(relx = 0, rely = 0, relwidth = 0.2, relheight = 1, anchor = ctk.NW)

SCROLLBAR: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(master = WIN, corner_radius = 0)
SCROLLBAR.place(relx = 0.2, rely = 0, relwidth = 0.8, relheight = 1, anchor = ctk.NW)

# Function to remove all mods from BepInEx
def removeAll() -> None:
      os.system(command = f"rmdir /S /Q \"{LC_BUNDLES}\"")
      os.system(command = f"rmdir /S /Q \"{LC_PLUGIN}\"")
      os.mkdir(path = LC_BUNDLES)
      os.mkdir(path = LC_PLUGIN)

# Function to open the game
def openGame() -> None:
      os.startfile(filepath = "steam://rungameid/1966720")

# Function to extract all plugins
def extractPlugins() -> None:
      for mod in os.listdir(path = PLUGIN_PATH):
            mod_path: str = f"{PLUGIN_PATH}/{mod}"
            if is_zipfile(filename = mod_path):
                  folder_path: str = os.path.splitext(p = mod_path)[0]
                  os.mkdir(path = folder_path)

                  mod_zip = ZipFile(file = mod_path)
                  mod_zip.extractall(path = folder_path)
                  mod_zip.close()

                  os.remove(path = mod_path)

                  mod_path = folder_path
                  mod: str = os.path.splitext(p = mod)[0]

            for folder in os.listdir(path = mod_path):
                  folder_path: str = f"{mod_path}/{folder}"
                  if not os.path.isdir(path = folder_path): continue
                  if folder == "config": shutil.rmtree(path = folder_path)
                  elif folder == "BepInEx":
                        for bep_folder in os.listdir(path = folder_path):
                              bep_folder_path: str = f"{folder_path}/{bep_folder}"
                              if not os.path.isdir(path = bep_folder_path): continue
                              if bep_folder == "config": shutil.rmtree(path = bep_folder_path)

            with open(file = f"{mod_path}/manifest.json", mode = "rb") as f:
                  content: bytes = f.read()
                  plugins[mod] = json.decode(s = content.decode(encoding = detect(byte_str = content)["encoding"]))
                  plugins[mod]["dependees"] = []

                  buttons[mod] = ctk.CTkCheckBox(master = SCROLLBAR, fg_color ="#1F6AA5", hover_color = "#1F6AA5", checkmark_color = "#1F6AA5", text = plugins[mod]["name"], variable = ctk.IntVar(value = False))

# Function to check plugin dependencies
def checkDependencies() -> None:
      dependencies: dict[str: str] = {}
      updates: dict[str: str] = {}
      
      names: dict[str: str] = {}
      
      info = GetFileVersionInfo(f"{BEPINEX_PATH}/core/BepInEx.dll", "\\")
      ms: int = info["FileVersionMS"]
      ls: int = info["FileVersionLS"]
      if os.path.isdir(path = BEPINEX_PATH):
            for value in plugins.values():
                  try: value["dependencies"].remove(f"BepInEx-BepInExPack-{HIWORD(ms)}.{LOWORD(ms)}.{HIWORD(ls)}{LOWORD(ls)}0")
                  except ValueError: pass
                  names[value["name"]] = value["version_number"]
      else:
            for value in plugins.values(): names[value["name"]] = value["version_number"]
            
      for value in plugins.values():
            non_dependency: list[str] = []
            non_updated: list[str] = []
            
            for dependency in value["dependencies"]:
                  name, version = dependency.split("-")[-2:]
                  if name not in names: non_dependency.append(dependency.split("-", 1)[-1])
                  elif int(names[name].replace(".", "")) < int(version.replace(".", "")): non_updated.append(f"{name} {names[name]} -> {version}")
            
            if non_dependency: dependencies[value["name"].center(32)] = non_dependency
            if non_updated: updates[value["name"].center(32)] = non_updated
            
      if dependencies:
            print("NOT INSTALLED")
            for key, value in dependencies.items(): print(f"{key}\r\t\t\t\twill not work as {value} is not downloaded.")
            
      if updates:
            print("\nWRONG UPDATES")
            for key, value in updates.items(): print(f"{key}\r\t\t\t\tmight not work as {value} is the wrong version.")

# Function to add plugins
def addPlugin() -> None:
      removeAll()
      for mod in os.listdir(path = PLUGIN_PATH):
            if not buttons[mod].get(): continue
            mod_path: str = f"{PLUGIN_PATH}/{mod}"
            for file in os.listdir(path = mod_path):
                  file_path: str = f"{mod_path}/{file}"
                  if os.path.isdir(path = file_path):
                        if file == "BepInEx": shutil.copytree(src = file_path, dst = BEPINEX_PATH, dirs_exist_ok = True)
                        elif file in os.listdir(path = BEPINEX_PATH): shutil.copytree(src = file_path, dst = f"{BEPINEX_PATH}/{file}", dirs_exist_ok = True)
                        else: shutil.copytree(src = file_path, dst = LC_PLUGIN, dirs_exist_ok = True)
                  elif os.path.splitext(p = file_path)[-1] in ["", ".dll"]: shutil.copy(src = file_path, dst = LC_PLUGIN)

# Function to enable dependencies
def enableDependencies(mod: str) -> None:
      if buttons[mod].get():
            for dependency in plugins[mod]["dependencies"]:
                  mod_button: str = list(plugins)[[x.split("-")[:-1] for x in plugins].index(dependency.split("-")[:-1])]
                  if dependency.split("-")[:-1] in [x.split("-")[:-1] for x in plugins]:
                        buttons[mod_button].configure(variable = ctk.IntVar(value = True))
                        if mod not in plugins[mod_button]["dependees"]: plugins[mod_button]["dependees"].append(mod)
                        enableDependencies(mod = mod_button)
      else:
            for dependency in plugins[mod]["dependencies"]:
                  mod_button = list(plugins)[[x.split("-")[:-1] for x in plugins].index(dependency.split("-")[:-1])]
                  if mod in plugins[mod_button]["dependees"]: plugins[mod_button]["dependees"].remove(mod)
                  if dependency.split("-")[:-1] in [x.split("-")[:-1] for x in plugins] and plugins[mod_button]["dependees"] == []:
                        buttons[mod_button].configure(variable = ctk.IntVar(value = False))
                        enableDependencies(mod = mod_button)

# Function to save active mods
def saveActive() -> None:
      with open(file = ACTIVE_PATH, mode = "wb") as f: pickle.dump(obj = {key: value.get() for key, value in buttons.items()}, file = f)

# Function to save configs (BepInEx -> Config)
def saveConfigs() -> None:
      shutil.copytree(src = LC_CONFIG, dst = CONFIG_PATH, dirs_exist_ok = True)

# Function to update configs (Config -> BepInEx)
def updateConfigs() -> None:
      shutil.copytree(src = CONFIG_PATH, dst = LC_CONFIG, dirs_exist_ok = True)

# Function to toggle all mods
def toggleBepInEx() -> None:
      global BEPINEX_PATH, LC_BUNDLES, LC_CONFIG, LC_PLUGIN
      if toggle_bepinex.get():
            toggle_bepinex.configure(text = "Modded")
            os.rename(src = BEPINEX_PATH, dst = OG_BEPINEX_PATH)
            BEPINEX_PATH = OG_BEPINEX_PATH
      else:
            toggle_bepinex.configure(text = "Vanilla")
            os.rename(src = BEPINEX_PATH, dst = f"{LC_PATH}/_BepInEx")
            BEPINEX_PATH = f"{LC_PATH}/_BepInEx"

      LC_BUNDLES = f"{BEPINEX_PATH}/Bundles"
      LC_CONFIG = f"{BEPINEX_PATH}/config"
      LC_PLUGIN = f"{BEPINEX_PATH}/plugins"

# Function to remove all plugins from BepInEx and close
def close() -> None:
      removeAll()
      WIN.destroy()

extractPlugins()
checkDependencies()

# Remove all old mods from BepInEx
removeAll()

PADDING: float = 0.01
SB_REL: float = HEIGHT / (0.2 * WIDTH)
COLUMNS: int = len(buttons) // 3 + 1

with open(file = ACTIVE_PATH, mode = "rb") as f:
      content: bytes = f.read()
      if content: temp: dict[str, bool] = pickle.loads(content)
      else: temp: dict = {}

for idx, mod in enumerate(iterable = plugins):
      if mod in temp:
            buttons[mod].configure(variable = ctk.IntVar(value = temp[mod]))
            if temp[mod]: enableDependencies(mod = mod)
            temp.pop(mod)

      buttons[mod].configure(command = lambda mod = mod: enableDependencies(mod = mod))

      icon: ctk.CTkImage = ctk.CTkImage(light_image = Image.open(fp = f"{PLUGIN_PATH}/{mod}/icon.png"), size = (80, 80))
      icon_label: ctk.CTkLabel = ctk.CTkLabel(master = SCROLLBAR, image = icon, text = "")

      icon_label.grid(column = idx // COLUMNS * 2, row = idx % COLUMNS, padx = (20, 10), pady = (5, 5), sticky = ctk.NW)
      buttons[mod].grid(column = idx // COLUMNS * 2 + 1, row = idx % COLUMNS, padx = 0, pady = 0, sticky = ctk.W)

for mod in temp:
      if temp[mod]: print(f"Couldn't find {f"{mod}, available at https://thunderstore.io/c/lethal-company/p/{"/".join(mod.split("-")[:-1])}"}")

# Create items
# -On top-
open_game: ctk.CTkButton = ctk.CTkButton(master = SIDEBAR, width = 0, height = 0, text = "Open Game", fg_color = "green", hover_color = "#28501e", command = openGame)
toggle_bepinex: ctk.CTkSwitch = ctk.CTkSwitch(master = SIDEBAR, width = 0, height = 0, text = "Modded", variable = ctk.IntVar(value = 1), command = toggleBepInEx)
update_plugin: ctk.CTkButton = ctk.CTkButton(master = SIDEBAR, width = 0, height = 0, text = "Update Selected Plugins", command = addPlugin)

# -On bottom-
update_configs: ctk.CTkButton = ctk.CTkButton(master = SIDEBAR, width = 0, height = 0, text = "Update Configs (config -> bepinex)", command = updateConfigs)
save_config: ctk.CTkButton = ctk.CTkButton(master = SIDEBAR, width = 0, height = 0, text = "Save Configs (bepinex -> config)", command = saveConfigs)
save_active: ctk.CTkButton = ctk.CTkButton(master = SIDEBAR, width = 0, height = 0, text = "Save Active Mods", command = saveActive)
close_btn: ctk.CTkButton = ctk.CTkButton(master = SIDEBAR, width = 0, height = 0, text = "Close", fg_color = "red", hover_color = "#780000", command = close)

# Place items
# -On top-
for idx, obj in enumerate(iterable = [open_game,
                                      update_plugin,
                                      toggle_bepinex], start = 1):
      obj.place(relx = SB_REL * PADDING, rely = PADDING * idx + 0.05 * (idx - 1), relwidth = 0.96, relheight = 0.05)

# -On bottom-
for idx, obj in enumerate(iterable = [close_btn,
                                      save_active,
                                      save_config,
                                      update_configs], start = 1):
      obj.place(relx = SB_REL * PADDING, rely = 1 - 0.05 * idx - PADDING * idx, relwidth = 0.96, relheight = 0.05)

WIN.mainloop()