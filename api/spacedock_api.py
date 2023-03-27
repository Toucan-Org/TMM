import requests, logging

from utilities.mod_object import ModObject, VersionObject
import utilities.utility as util

spacedock_internal_id = 22407
categories = ["/featured", "/new"]

logger = logging.getLogger(__name__)


def get_mods(config_file, category=""):
    _mods = []

    url = f"https://spacedock.info/api/browse{category}?&game_id={spacedock_internal_id}"
    response = requests.get(url)
    data = response.json()

    if data:
        if category == "":        
            logger.info("Getting all mods")
            total_pages = data["pages"]
            for page in range(1, total_pages + 1):
                page_url = f"{url}&page={page}"
                page_response = requests.get(page_url)
                page_data = page_response.json()
                if category == "":
                    mods = page_data["result"]
                else:
                    mods = page_data
                for item in mods:
                    if item["game_id"] == spacedock_internal_id:
                        mod = ModObject(**item)
                        if util.check_mod_in_json(mod.id, config_file["KSP2"]["ModlistPath"]):
                            logger.info(f"{mod.name} ({mod.id}) is installed in the list")
                            mod = util.get_mod_from_json(mod, config_file["KSP2"]["ModlistPath"])
                        _mods.append(mod)

        else:
            logger.info(f"Getting mods from {category}")
            for item in data:
                if item["game_id"] == spacedock_internal_id:
                    mod = ModObject(**item)
                    if util.check_mod_in_json(mod.id, config_file["KSP2"]["ModlistPath"]):
                        logger.info(f"{mod.name} ({mod.id}) is installed in the list")
                        mod = util.get_mod_from_json(mod, config_file["KSP2"]["ModlistPath"])
                    _mods.append(mod)
    else:
        logger.error("No data returned from Spacedock!")

    _mods.sort()
    return _mods



def search_mod(mod_name, config_file, mod_id=None):
    if mod_id:
        logger.info(f"Searching for {mod_id}")
        url = f"https://spacedock.info/api/mod/{mod_id}"
        response = requests.get(url)
        data = response.json()

        if data["game_id"] == spacedock_internal_id:
            mod = ModObject(**data)

            if util.check_mod_in_json(mod.id, config_file["KSP2"]["ModlistPath"]):
                logger.info(f"{mod.name} ({mod.id}) is installed in the list")
                mod = util.get_mod_from_json(mod, config_file["KSP2"]["ModlistPath"])

            logger.info(mod)

            return mod
        
    else:
        logger.info(f"Searching for {mod_name}")
        query = mod_name.replace(" ", "%20")
        url = f'https://spacedock.info/api/search/mod?query={query}'
        response = requests.get(url)
        data = response.json()

        _mods = []

        for item in data:
            if item["game_id"] == spacedock_internal_id:
                mod = ModObject(**item)

                if util.check_mod_in_json(mod.id, config_file["KSP2"]["ModlistPath"]):
                    logger.info(f"{mod.name} ({mod.id}) is installed in the list")
                    mod = util.get_mod_from_json(mod, config_file["KSP2"]["ModlistPath"])
                    
                _mods.append(mod)        

        if len(_mods) == 0:
            logger.info("No mods found")
        
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
            logger.info(f"{mod.name} has an update available! Latest version: {latest_version.friendly_version}")
            return latest_version
        
    logger.info(f"{mod.name} is up to date")
    return None


