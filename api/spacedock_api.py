import requests

from utilities.mod_object import ModObject
import utilities.utility as util

spacedock_internal_id = 22407
categories = ["/featured", "/top", "/new"]


def get_mods(category=""):
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

                    if util.check_mod_in_json(mod.id):
                        print(f"{mod.name} ({mod.id}) is installed in the list")
                        mod = util.get_mod_from_json(mod)
                    
                    _mods.append(mod)
    else:
        print(f"Getting mods from {category}")
        if data:
            for item in data:
                if item["game_id"] == spacedock_internal_id:
                    mod = ModObject(**item)

                    if util.check_mod_in_json(mod.id):
                        print(f"{mod.name} ({mod.id}) is installed in the list")
                        mod = util.get_mod_from_json(mod)

                    _mods.append(mod)

    _mods.sort()
    return _mods



def search_mod(mod_name, mod_id=None):
    if mod_id:
        print(f"Searching for {mod_id}")
        url = f"https://spacedock.info/api/mod/{mod_id}"
        response = requests.get(url)
        data = response.json()

        if data["game_id"] == spacedock_internal_id:
            mod = ModObject(**data)

            if util.check_mod_in_json(mod.id):
                print(f"{mod.name} ({mod.id}) is installed in the list")
                mod = util.get_mod_from_json(mod)

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

                if util.check_mod_in_json(mod.id):
                    print(f"{mod.name} ({mod.id}) is installed in the list")
                    mod = util.get_mod_from_json(mod)
                    
                _mods.append(mod)        

        if len(_mods) == 0:
            print("No mods found")
        
        _mods.sort()
        return _mods

        

    



if __name__ == "__main__":
    # search_results = search_mod("Community Fixes")

    # for mod in search_results:
    #     print(mod)

    get_mods("/new")

