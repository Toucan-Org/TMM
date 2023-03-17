import requests, threading, json
from bs4 import BeautifulSoup

root_url = "https://spacedock.info"

class ModObject():
    def __init__(self, **kwargs):
        self.enabled = kwargs.get("enabled", False)
        self.installed = kwargs.get("installed", False)
        self.name = kwargs.get("name", "Unknown Mod")
        self.id = kwargs.get("id", "Unknown ID")
        self.short_description = kwargs.get("short_description", "No summary provided.")
        self.downloads = kwargs.get("downloads", 0)
        self.followers = kwargs.get("followers", 0)
        self.author = kwargs.get("author", "Unknown Author")
        self.game_version = kwargs.get("game_version", "0.0.0")
        self.website = kwargs.get("website", None)
        self.donations = kwargs.get("donations", None)

        self.filename = kwargs.get("filename", None)

        # Check if the mod is installed and get its URL, otherwise craft the URL
        if self.installed:
            self.url = kwargs.get("url", "No modpage URL provided.")
        else:
            self.url = f'{root_url}{kwargs.get("url", "No modpage URL provided.")}'

        if self.donations == "":
            self.donations = "No donation URL provided."

        if self.website == "":
            self.website = "No website URL provided."

        self.versions = []

        for version in kwargs.get("versions", []):
            # Check if url exists in version
            if "url" not in version:
                version["url"] = self.url

            self.versions.append(VersionObject(**version))

        self.game_version = self.get_newest_version().game_version

    def get_newest_version(self):
        """Returns the newest version of the mod."""
        version = max(self.versions, key=lambda v: v.created)
        return version

    def __str__(self):
        return f"{self.name} - {self.short_description} ({self.installed})"
    
    def __eq__(self, other):
        return self.name.lower() == other.name.lower()
    
    def __lt__(self, other):
        return self.name.lower() < other.name.lower()

class ModObjectEncoder(json.JSONEncoder):
    # This class is used to encode the ModObject class into JSON
    def default(self, obj):
        if isinstance(obj, ModObject):
            return obj.__dict__
        
        elif isinstance(obj, VersionObject):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

class VersionObject():
    def __init__(self, **kwargs):
        self.url = kwargs.get("url", "No modpage URL provided.")
        self.installed = kwargs.get("installed", False)
        self.friendly_version = kwargs.get("friendly_version", "Unknown Version")
        self.game_version = kwargs.get("game_version", "0.0.0")
        self.created = kwargs.get("created", "Unknown Date")
        self.downloads = kwargs.get("downloads", 0)
        self.download_size = self.get_file_size()

        if self.installed:
            self.download_path = kwargs.get("download_path", "No download URL provided.")

        else:
            self.download_path = f"{root_url}{kwargs.get('download_path', 'No download URL provided.')}"

    # Spacedock API does not include file sizes so instead I have to get it from the modpage using BeautifulSoup and requests
    # This is done in a separate thread to prevent the GUI from freezing
    def get_file_size(self):
        def get_size():
            try:
                response = requests.get(self.url)
                soup = BeautifulSoup(response.text, "html.parser")
                download_link = soup.find("a", {"id": "download-link-primary"})
                download_size = download_link.get_text(strip=True).split('(')[-1].split(')')[0]
                self.download_size = download_size
            
            except Exception as e:
                print(f"Failed to get file size for {self.friendly_version} of {self.url}!")
                print(e)
                self.download_size = "Unknown Size"
        t = threading.Thread(target=get_size)
        t.start()

    def __str__(self):
        return f"{self.friendly_version} - {self.game_version}"
    
    def __eq__(self, other):
        return self.friendly_version.lower() == other.friendly_version.lower()
    
    def __lt__(self, other):
        return self.friendly_version.lower() < other.friendly_version.lower()
