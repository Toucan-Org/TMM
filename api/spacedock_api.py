import requests

from utilities.mod_object import ModObject, VersionObject
import utilities.utility as util

spacedock_internal_id = 22407
categories = ["/featured", "/top", "/new"]


def get_mods(config_file, category="",):
    _mods = []

    url = f"https://spacedock.info/api/browse{category}?&game_id={spacedock_internal_id}"
    response = requests.get(url)
    data = response.json()

    if category == "":        
        print("Getting all mods")
        if data:
            for item in data["result"]:
                if item["game_id"] == spacedock_internal_id:
                    #check if the mod is in the installed list
                    mod = ModObject(**item)

                    if util.check_mod_in_json(mod.id, config_file["KSP2"]["ModlistPath"]):
                        print(f"{mod.name} ({mod.id}) is installed in the list")
                        mod = util.get_mod_from_json(mod, config_file["KSP2"]["ModlistPath"])
                    
                    _mods.append(mod)
    else:
        print(f"Getting mods from {category}")
        if data:
            for item in data:
                if item["game_id"] == spacedock_internal_id:
                    mod = ModObject(**item)

                    if util.check_mod_in_json(mod.id, config_file["KSP2"]["ModlistPath"]):
                        print(f"{mod.name} ({mod.id}) is installed in the list")
                        mod = util.get_mod_from_json(mod, config_file["KSP2"]["ModlistPath"])

                    _mods.append(mod)

    _mods.sort()
    return _mods



def search_mod(mod_name, config_file, mod_id=None):
    if mod_id:
        print(f"Searching for {mod_id}")
        url = f"https://spacedock.info/api/mod/{mod_id}"
        response = requests.get(url)
        data = response.json()

        if data["game_id"] == spacedock_internal_id:
            mod = ModObject(**data)

            if util.check_mod_in_json(mod.id, config_file["KSP2"]["ModlistPath"]):
                print(f"{mod.name} ({mod.id}) is installed in the list")
                mod = util.get_mod_from_json(mod, config_file["KSP2"]["ModlistPath"])

            print(mod)

            return mod
        
    else:
        print(f"Searching for {mod_name}")
        query = mod_name.replace(" ", "%20")
        url = f'https://spacedock.info/api/search/mod?query={query}'
        response = requests.get(url)
        data = response.json()

        _mods = []

        for item in data:
            if item["game_id"] == spacedock_internal_id:
                mod = ModObject(**item)

                if util.check_mod_in_json(mod.id, config_file["KSP2"]["ModlistPath"]):
                    print(f"{mod.name} ({mod.id}) is installed in the list")
                    mod = util.get_mod_from_json(mod, config_file["KSP2"]["ModlistPath"])
                    
                _mods.append(mod)        

        if len(_mods) == 0:
            print("No mods found")
        
        _mods.sort()
        return _mods
    

def check_mod_update(mod):
    url = f"https://spacedock.info/api/mod/{mod.id}"
    response = requests.get(url)
    data = response.json()

    if data["game_id"] == spacedock_internal_id:
        latest_version_data = data["versions"][0]
        latest_version = VersionObject(
            url=mod.url,
            installed=True,
            friendly_version=latest_version_data["friendly_version"],
            game_version=latest_version_data["game_version"],
            created=latest_version_data["created"],
            downloads=latest_version_data["downloads"],
            download_path=latest_version_data["download_path"],
        )

        if latest_version.friendly_version != mod.get_installed_version().friendly_version:
            print(f"{mod.name} has an update available! Latest version: {latest_version.friendly_version}")
            return latest_version
        
    print(f"{mod.name} is up to date")
    return None


