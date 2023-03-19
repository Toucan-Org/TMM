import os, pefile, json, urllib.request, zipfile, shutil, requests
from utilities.mod_object import ModObjectEncoder, ModObject


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

def create_modlist_json():
    """Create a modlist.json file"""

    with open("modlist.json", "w") as f:
        json.dump({"mods": []}, f, indent=4)


def add_mod_to_json(mod):
    """Add a mod to the json file"""

    # Check if modlist.json exists
    if not os.path.exists("modlist.json"):
        create_modlist_json()

    # Load json file
    with open("modlist.json", "r") as f:
        data = json.load(f)
    
    # Check if mod is already in list
    for item in data["mods"]:
        if item["id"] == mod.id:
            print(f"{mod.name} ({mod.id}) is already in the list")
            return
    else:
        data["mods"].append(mod.__dict__)

    with open("modlist.json", "w") as f:
        json.dump(data, f, indent=4, cls=ModObjectEncoder)


def remove_mod_from_json(mod):
    """Remove a mod from the json file"""

    if not os.path.exists("modlist.json"):
        print("No modlist.json file found")
        return

    with open("modlist.json", "r") as f:
        data = json.load(f)

    for item in data["mods"]:
        if item["id"] == mod.id:
            data["mods"].remove(item)
            print(f"Removed {item['name']} ({item['id']}) from the list")
            break
    else:
        print(f"Could not find mod with id {mod.id} in the list")

    with open("modlist.json", "w") as f:
        json.dump(data, f, indent=4, cls=ModObjectEncoder)

def check_mod_in_json(mod_id):
    """Check if a mod is in the json file"""

    if not os.path.exists("modlist.json"):
        print("No modlist.json file found")
        create_modlist_json()
        return False

    with open("modlist.json", "r") as f:
        data = json.load(f)

    for item in data["mods"]:
        if item["id"] == mod_id:
            return True
        
    return False

def get_mod_from_json(mod):
    """Get a mod from the json file"""

    if not os.path.exists("modlist.json"):
        print("No modlist.json file found")
        create_modlist_json()
        return None

    with open("modlist.json", "r") as f:
        data = json.load(f)

    for item in data["mods"]:
        if item["id"] == mod.id:
            return ModObject(**item)
        
    return None


def get_installed_mods():
    """Get a list of installed mods"""

    if not os.path.exists("modlist.json"):
        print("No modlist.json file found")
        return []

    with open("modlist.json", "r") as f:
        data = json.load(f)

    return [ModObject(**item) for item in data["mods"]]


# This is giving some strange errors, so I'm commenting it out for now
# def install_mod_threaded(mod, version, installdir):
#     t = threading.Thread(target=download_install_mod, args=(mod, version, installdir))
#     t.start()
#     return t


def download_install_mod(mod, version, installdir):
    """Download and install a mod"""

    try:
        #Check if it exists in cache
        mod.filename = f"{mod.name}_{version.friendly_version}"
        if os.path.exists(f"data/cache/{mod.filename}.zip"):
            print(f"Found {mod.filename} in cache")
            install_mod(mod, installdir)
        
        else:
            print(f"Downloading {mod.name} ({mod.id})")
            print(f"Downloading from {version.download_path}")
            
            urllib.request.urlretrieve(version.download_path, f"data/cache/{mod.filename}.zip") # Download the mod
            install_mod(mod, installdir)

        # Add the mod to the json file
        version.installed = True
        mod.installed = True

        add_mod_to_json(mod)
        print("Installed mod!")
        return True
    
    except Exception as e:
        print(f"Error installing {mod.name} ({mod.id})")
        print(e)

    return False


def install_mod(mod: ModObject, installdir: str) -> bool:
    """Install a mod and check if it was successful"""
    print(f"Installing {mod.name} ({mod.id})")

    installed_files = []
    if extract_zip(f"data/cache/{mod.filename}.zip", installdir, installed_files):
        # Save the list of installed files to a JSON file
        set_installed_files(mod, installed_files)
        print(f"Installed {mod.name} ({mod.id})")
        return True

    print(f"Error installing {mod.name} ({mod.id})")
    return False


def uninstall_mod(mod, installdir):
    excluded_dirs = ["BepInEx/", "BepInEx/plugins/", "BepInEx/config/"]
    print(f"Uninstalling {mod.name} ({mod.id})")

    # Load the list of installed files from the JSON file
    installed_files = get_installed_files(mod)

    for filename in installed_files:
        filepath = os.path.join(installdir, filename)

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
    remove_mod_from_json(mod)

    # Delete the JSON file containing the list of installed files
    os.remove(os.path.join("data", "logs", "install_logs", f"{mod.filename}.json"))
    print(f"Removed {mod.filename}.json")

    return True


def extract_zip(zip_path: str, destination_path: str, installed_files: list) -> bool:
    """Extract a zip file to destination path"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destination_path)
            print(f"Extracted {zip_path} to {destination_path}")
            # Append the paths of the extracted files and folders to the list
            for name in zip_ref.namelist():
                installed_files.append(name)

            print(f"Installed files: {installed_files}")
            return True

    except zipfile.BadZipFile:
        print(f"Could not extract {zip_path}")

    return False


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


def set_textbox_text(textbox, text):
    """Set the text of a textbox"""
    textbox.configure(state="normal")
    textbox.delete("0.0", "end")  # delete all text
    textbox.insert("end", text)  # insert at the end of the textbox
    textbox.configure(state="disabled")
    

def check_bepinex_installed():
    """Check if Space Warp + BepInEx is installed"""
    internal_mod_id = 3277
    if check_mod_in_json(internal_mod_id):
        return True
    
    return False
