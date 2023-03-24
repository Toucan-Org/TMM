import os, pefile, json, urllib.request, zipfile, shutil, requests
from utilities.mod_object import ModObjectEncoder, ModObject

#modlist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modlist.json")

def get_latest_version():
    """Check if a newer version of 2KAN is available"""
    url = f"https://api.github.com/repos/Loki-Lokster/2KAN/releases/latest"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        latest_version = data["tag_name"]
        return latest_version
    
    return None


def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if hours >= 1000:
        formatted_hours = "{:,}".format(hours)
    else:
        formatted_hours = f"{hours:02d}"

    return f"{formatted_hours}h {minutes:02d}m {seconds:02d}s"


def scan_common_ksp2_installs():
    """Scan common places for KSP 2 installs"""

    print("Scanning for KSP 2 installs")
    common_paths = ["C:\\Program Files (x86)\\Steam\\steamapps\\common\\Kerbal Space Program 2",
                    "C:\\Program Files\\Steam\\steamapps\\common\\Kerbal Space Program 2"]
    for path in common_paths:
        if os.path.exists(path):
            print(f"Found KSP 2 install at {path}")
            return path
        
    print("No KSP 2 install found")
    return None


def detect_game_version(path):
    # Check if KSP2_x64.exe exists
    if not os.path.exists(os.path.join(path, "KSP2_x64.exe")):
        print("Could not find KSP2_x64.exe")
        return None
    
    # Use pefile to get the version info from the exe
    # (This took way too long to get working)
    pe = pefile.PE(os.path.join(path, "KSP2_x64.exe"))
    for fileinfo in pe.FileInfo:
        for info in fileinfo:
            if info.Key == b'StringFileInfo':
                for st in info.StringTable:
                    for entry in st.entries.items():
                        if entry[0] == b"ProductVersion":
                            version = entry[1].decode('utf-8')
                            return version
                        
    print("Could not find KSP 2 version")
    return None

def create_modlist_json(modlist_path):
    """Create a modlist.json file"""

    with open(modlist_path, "w") as f:
        json.dump({"mods": []}, f, indent=4)


def add_mod_to_json(mod, modlist_path):
    """Add a mod to the json file"""

    # Check if modlist.json exists
    if not os.path.exists(modlist_path):
        create_modlist_json(modlist_path)

    # Load json file
    with open(modlist_path, "r") as f:
        data = json.load(f)
    
    # Check if mod is already in list
    for item in data["mods"]:
        if item["id"] == mod.id:
            print(f"{mod.name} ({mod.id}) is already in the list")
            return
    else:
        data["mods"].append(mod.__dict__)

    with open(modlist_path, "w") as f:
        json.dump(data, f, indent=4, cls=ModObjectEncoder)


def remove_mod_from_json(mod, modlist_path):
    """Remove a mod from the json file"""

    if not os.path.exists(modlist_path):
        print("No modlist.json file found")
        return

    with open(modlist_path, "r") as f:
        data = json.load(f)

    for item in data["mods"]:
        if item["id"] == mod.id:
            data["mods"].remove(item)
            print(f"Removed {item['name']} ({item['id']}) from the list")
            break
    else:
        print(f"Could not find mod with id {mod.id} in the list")

    with open(modlist_path, "w") as f:
        json.dump(data, f, indent=4, cls=ModObjectEncoder)

def check_mod_in_json(mod_id, modlist_path):
    """Check if a mod is in the json file"""

    if not os.path.exists(modlist_path):
        print("No modlist.json file found")
        create_modlist_json(modlist_path)
        return False

    with open(modlist_path, "r") as f:
        data = json.load(f)

    for item in data["mods"]:
        if item["id"] == mod_id:
            return True
        
    return False

def get_mod_from_json(mod, modlist_path):
    """Get a mod from the json file"""

    if not os.path.exists(modlist_path):
        print("No modlist.json file found")
        create_modlist_json(modlist_path)
        return None

    with open(modlist_path, "r") as f:
        data = json.load(f)

    for item in data["mods"]:
        if item["id"] == mod.id:
            return ModObject(**item)
        
    return None


def get_installed_mods(modlist_path):
    """Get a list of installed mods"""

    if not os.path.exists(modlist_path):
        print("No modlist.json file found")
        return []

    with open(modlist_path, "r") as f:
        print("Loading modlist.json")
        data = json.load(f)
        return [ModObject(**item) for item in data["mods"]]


# This is giving some strange errors, so I'm commenting it out for now
# def install_mod_threaded(mod, version, installdir):
#     t = threading.Thread(target=download_install_mod, args=(mod, version, installdir))
#     t.start()
#     return t


def download_install_mod(mod, version, config_file):
    """Download and install a mod"""

    try:
        #Check if it exists in cache
        mod.filename = f"{mod.name}_{version.friendly_version}"
        if os.path.exists(f"data/cache/{mod.filename}.zip"):
            print(f"Found {mod.filename} in cache")
            install_mod(mod, config_file["KSP2"]["InstallDirectory"])
        
        else:
            print(f"Downloading {mod.name} ({mod.id})")
            print(f"Downloading from {version.download_path}")
            
            urllib.request.urlretrieve(version.download_path, f"data/cache/{mod.filename}.zip") # Download the mod
            install_mod(mod, config_file["KSP2"]["InstallDirectory"])

        mod.installed = True
        mod.set_installed_version(version)

        add_mod_to_json(mod, config_file["KSP2"]["ModlistPath"])
        print("Installed mod!")
        return True
    
    except Exception as e:
        print(f"Error installing {mod.name} ({mod.id})")
        print(e)

    return False


def install_mod(mod: ModObject, installdir: str) -> bool:
    """Install a mod and check if it was successful"""
    print(f"Installing {mod.name} ({mod.id})")
    installed_files = extract_zip(f"data/cache/{mod.filename}.zip", installdir)
    if installed_files != []:
        # Save the list of installed files to a JSON file
        set_installed_files(mod, installed_files)
        print(f"Installed {mod.name} ({mod.id})")
        return True

    print(f"Error installing {mod.name} ({mod.id})")
    return False


def uninstall_mod(mod, config_file):
    excluded_dirs = ["BepInEx/", "BepInEx/plugins/", "BepInEx/config/"]
    print(f"Uninstalling {mod.name} ({mod.id})")

    # Load the list of installed files from the JSON file
    installed_files = get_installed_files(mod)

    for filename in installed_files:
        filepath = os.path.join(config_file["KSP2"]["InstallDirectory"], filename)

        # Check if the file exists
        if os.path.isfile(filepath):
            os.remove(filepath)
            print(f"Removed file {filepath}")

        # Else check if the directory exists
        elif os.path.isdir(filepath):
            # Check if the directory is excluded
            if any(filepath.endswith(excluded_dir) for excluded_dir in excluded_dirs):
                print(f"Skipping {filepath}")
            else:
                shutil.rmtree(filepath, ignore_errors=True)
                print(f"Removed directory {filepath}")
        else:
            print(f"Could not find {filepath}")

    # Remove the mod from the JSON file
    remove_mod_from_json(mod, config_file["KSP2"]["ModlistPath"])

    # Delete the JSON file containing the list of installed files
    os.remove(os.path.join("data", "logs", "install_logs", f"{mod.filename}.json"))
    print(f"Removed {mod.filename}.json")

    return True

def extract_zip(zip_path: str, destination_path: str) -> bool:
    """Extract a zip to the proper directory"""

    installed_files = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Check if the first directory is called "BepInEx"
            has_bepinex = False
            for name in zip_ref.namelist():
                if "bepinex" in name.lower():
                    print(f"Found BepInEx in {name}")
                    has_bepinex = True
                    break

            if has_bepinex:
                print("First directory is BepInEx")
                # Extract the zip file directly to the destination_path directory
                zip_ref.extractall(destination_path)
                print(f"Extracted {zip_path} to {destination_path}")
                for name in zip_ref.namelist():
                    installed_files.append(os.path.join(destination_path, name))

            else:
                # Extract the entire directory to BepInEx/plugins within the destination_path
                extracted_path = os.path.join(destination_path, "BepInEx", "plugins")
                zip_ref.extractall(extracted_path)
                print(f"Extracted {zip_path} to {extracted_path}")
                for name in zip_ref.namelist():
                    installed_files.append(os.path.join(extracted_path, name))

            return installed_files
        
    except zipfile.BadZipFile:
        print(f"Could not extract {zip_path}")

    return []


def get_installed_files(mod: ModObject) -> dict:
    """
    Load the paths of all installed files and folders.
    Returns a dictionary where keys are the filenames
    and values are the paths to the installed files.
    """
    try:
        with open(f"data/logs/install_logs/{mod.filename}.json", "r") as f:
            installed_files = json.load(f)
    except FileNotFoundError:
        print(f"Could not find {mod.filename}.json")
        installed_files = {}
    return installed_files


def set_installed_files(mod: ModObject, installed_files: dict):
    """Save the paths of all installed files and folders to a JSON file"""
    with open(f"data/logs/install_logs/{mod.filename}.json", "w") as f:
        json.dump(installed_files, f, indent=4)


def set_textbox_text(textbox, text, color="white"):
    """Set the text of a textbox"""
    textbox.configure(state="normal", text_color=color)
    textbox.delete("0.0", "end")  # delete all text
    textbox.insert("end", text)  # insert at the end of the textbox
    textbox.configure(state="disabled", text_color=color)

def set_label_color(label, color):
    """Sets the color of the game version label."""
    label.configure(text_color=color)

def check_bepinex_installed(config_file):
    """Check if Space Warp + BepInEx is installed"""
    internal_mod_id = 3277
    if check_mod_in_json(internal_mod_id, config_file["KSP2"]["ModlistPath"]):
        return True
    
    return False

def build_directories():
    """Build the directory"""
    if not os.path.exists("data"):
        os.mkdir("data")
        print("Created data directory")
    if not os.path.exists("data/cache"):
        os.mkdir("data/cache")
        print("Created cache directory")
    if not os.path.exists("data/logs"):
        os.mkdir("data/logs")
        print("Created logs directory")
    if not os.path.exists("data/logs/install_logs"):
        os.mkdir("data/logs/install_logs")
        print("Created install_logs directory")
