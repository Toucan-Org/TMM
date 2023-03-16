import os, pefile, json, urllib.request, zipfile, shutil
from utilities.mod_object import ModObjectEncoder, ModObject



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

def check_mod_in_json(mod):
    """Check if a mod is in the json file"""

    if not os.path.exists("modlist.json"):
        print("No modlist.json file found")
        create_modlist_json()
        return False

    with open("modlist.json", "r") as f:
        data = json.load(f)

    for item in data["mods"]:
        if item["id"] == mod.id:
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


def download_install_mod(mod, version, installdir):
    """Download and install a mod"""

    try:
        #Check if it exists in cache
        mod.filename = f"{mod.name}_{version.friendly_version}.zip"
        if os.path.exists(f"data/cache/{mod.filename}"):
            print(f"Found {mod.filename} in cache")
            install_mod(mod, installdir)
        
        else:
            print(f"Downloading {mod.name} ({mod.id})")
            print(f"Downloading from {version.download_path}")
            
            urllib.request.urlretrieve(version.download_path, f"data/cache/{mod.filename}") # Download the mod

        # Add the mod to the json file
        add_mod_to_json(mod)
        version.installed = True
        print("Installed mod!")
        return True
    
    except Exception as e:
        print(f"Error downloading {mod.name} ({mod.id})")
        print(e)

    return False



def install_mod(mod: ModObject, installdir: str) -> bool:
    """Install a mod and check if it was successful"""

    print(f"Installing {mod.name} ({mod.id})")

    if extract_zip(f"data/cache/{mod.filename}", installdir):
        print(f"Installed {mod.name} ({mod.id})")
        return True

    print(f"Error installing {mod.name} ({mod.id})")
    return False


def uninstall_mod(mod, installdir):
    print(f"Uninstalling {mod.name} ({mod.id})")

    remove_mod_from_json(mod) # Remove the mod from the json file

    success = False
    # Try and remove the mod from the BepInEx/plugins folder
    try:
        bp_plugins_dir = os.path.join(installdir, "BepInEx", "plugins", mod.name)
        shutil.rmtree(bp_plugins_dir, ignore_errors=False)
        print(f"Removed {bp_plugins_dir}")
        success = True
    
    except FileNotFoundError:
        print(f"Could not find {bp_plugins_dir}")

    
    # Try and remove the mod from the SpaceWarp/plugins folder
    try:
        sw_plugins_dir = os.path.join(installdir, "SpaceWarp", "plugins", mod.name)
        shutil.rmtree(sw_plugins_dir, ignore_errors=False)
        print(f"Removed {sw_plugins_dir}")
        success = True
    
    except FileNotFoundError:
        print(f"Could not find {sw_plugins_dir}")

    if not success:
        print(f"Could not uninstall {mod.name} ({mod.id})")
        print("Removing from list anyway!")
        remove_mod_from_json(mod)

    return success
    


def extract_zip(zip_path: str, destination_path: str) -> bool:
    """Extract a zip file to destination path"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destination_path)
            print(f"Extracted {zip_path} to {destination_path}")
            return True

    except zipfile.BadZipFile:
        print(f"Could not extract {zip_path}")

    return False

def set_textbox_text(textbox, text):
    """Set the text of a textbox"""
    textbox.configure(state="normal")
    textbox.delete("0.0", "end")  # delete all text
    textbox.insert("end", text)  # insert at the end of the textbox
    textbox.configure(state="disabled")

    
