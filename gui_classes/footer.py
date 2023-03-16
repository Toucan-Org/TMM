import customtkinter, subprocess
import utilities.utility as util
import api.spacedock_api as sdapi
import tkinter as tk

from PIL import Image


class FooterFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.grid_columnconfigure((0,1,2,3), weight=1)
        self.configure(fg_color="gray13")

        self.config_file = kwargs.get("config", None)

        self.modlist_frame = kwargs.get("modlist_frame", None)

        self.search_bar_frame = SearchBarFrame(master=self, modlist_frame=self.modlist_frame)
        self.search_bar_frame.grid(row=0, column=0, columnspan=2, padx=20, sticky="nsew")

        self.install_directory_frame = InstallDirectoryFrame(master=self, config=self.config_file)
        self.install_directory_frame.grid(row=0, column=2, padx=20, sticky="nsew")

        self.launch_button = LaunchButton(master=self)
        self.launch_button.grid(row=0, column=3, padx=20, sticky="nsew")


    def update_appearance(self):
        if customtkinter.get_appearance_mode() == "Light":
            self.configure(fg_color="white")

        else:
            self.configure(fg_color="gray13")



class InstallDirectoryFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.config_file = kwargs.get("config", None)
        self.cp_button_frame = kwargs.get("cp_button_frame", None)

        self.detected_label = customtkinter.CTkLabel(self, text="", font=customtkinter.CTkFont(size=11, weight="bold"), text_color="green")
        self.detected_label.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")

        # Check if an InstallDirectory is saved in the config file
        if self.config_file.has_section('InstallDirectory'):
            self.install_path = self.config_file.get('InstallDirectory', None)
        else:
            self.install_path = util.scan_common_ksp2_installs()

        if self.config_file.has_section('GameVersion'):
            self.game_version = self.config_file.get('GameVersion', None)
        else:
            self.game_version = util.detect_game_version(self.install_path)
            print(f"Version: {self.game_version}")

            if self.game_version:
                self.set_game_version_label(f"Game Version: ({self.game_version}) detected!")
                self.save_config()

            else:
                self.set_game_version_label("Game not found!", "red")
            
        self.install_location = customtkinter.CTkEntry(self)
        self.install_location.insert(0, self.install_path)
        self.install_location.grid(row=1, column=0, sticky="nsew")      

        self.label = customtkinter.CTkLabel(self, text="Install Path", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.label.grid(row=0, column=0, pady=10, sticky="w")

        self.browse_button = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, width=80, text_color=("gray10", "#DCE4EE"), text="Browse", command=self.browse_for_folder)
        self.browse_button.grid(row=1, column=1, sticky="nsew", padx=5)



    def browse_for_folder(self):
        """Opens a file dialog to select a folder and sets the install path to the selected folder"""
        folder_path = tk.filedialog.askdirectory()
        if folder_path:
            self.install_path = folder_path
            self.install_location.delete(0, "end")
            self.install_location.insert(0, folder_path)
            print(folder_path)
            self.game_version = util.detect_game_version(f"{folder_path}")

            if self.game_version:
                # If the game version is detected, save the install path and game version to the config file and enable the install button
                self.set_game_version_label(f"Game Version: ({self.game_version}) detected!")
                self.cp_button_frame.toggle_install_button_state("normal")
                self.save_config()

            else:
                # Otherwise disable the install button and set the game version label to red
                self.set_game_version_label("Game not found!", "red")
                self.cp_button_frame.toggle_install_button_state("disabled")


    def save_config(self):
        """Saves the install path and game version to the config file"""
        self.config_file["KSP2"]["install_path"] = str(self.install_path)
        self.config_file["KSP2"]["game_version"] = str(self.game_version)
        with open("config.ini", "w") as config_file:
            self.config_file.write(config_file)


    def set_game_version_label(self, text, color="green"):
        """Sets the game version label to the given text and color"""
        self.detected_label.configure(text=text, text_color=color)



class LaunchButton(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config_file = self.master.config_file

        self.launch_image = customtkinter.CTkImage(Image.open("./data/images/launch_button/launch_button.png"), size=(200, 80))
        self.launch_image_hover = customtkinter.CTkImage(Image.open("./data/images/launch_button/launch_button_hover.png"), size=(200, 80))
        self.grid_columnconfigure(0, weight=1)

        self.launch_button = customtkinter.CTkButton(self, image=self.launch_image, fg_color="transparent", text="", bg_color="transparent", command=self.launch, hover=False)
        self.launch_button.grid(row=0, column=0, sticky="e", pady=20, padx=20 )

        self.launch_button.bind("<Enter>", self.on_enter)
        self.launch_button.bind("<Leave>", self.on_leave)

    def on_enter(self):
        self.launch_button.configure(image=self.launch_image_hover)
    
    def on_leave(self):
        self.launch_button.configure(image=self.launch_image)

    def launch(self):
        print("Launching KSP2...")
        #Launch the exe found in the config file
        if self.config_file["KSP2"]["install_path"]:
            try:
                subprocess.Popen(f"{self.config_file['KSP2']['install_path']}\\KSP2_x64.exe")
            except FileNotFoundError:
                print("Could not find KSP2_x64.exe")

class SearchBarFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.modlist_frame = kwargs.get("modlist_frame", None)

        self.label = customtkinter.CTkLabel(self, text="Search Mods", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.label.grid(row=0, column=0, pady=10, sticky="w")

        self.search_bar = customtkinter.CTkEntry(self, font=customtkinter.CTkFont(size=12), width=250)
        self.search_bar.grid(row=1, column=0, sticky="ew")
        self.search_bar.bind("<Return>", self.search_mods)

        self.search_button = customtkinter.CTkButton(self, text="Search", command=self.search_mods, fg_color="transparent", border_width=2, width=80, text_color=("gray10", "#DCE4EE"))
        self.search_button.grid(row=1, column=1, padx=(10, 30), sticky="ew")


    def search_mods(self):
        """Searches the modlist for the query in the search bar. 
        If the query is not found in the modlist, it will search the API for the query"""
        
        query = self.search_bar.get()

        if query == "":
            mods = sdapi.get_mods("")
            self.modlist_frame.populate_modlist(mods)
            return
        
        found_mods = []

        for mod in self.modlist_frame.modlist:
            if query.lower() in mod.name.lower():
                found_mods.append(mod)

        if found_mods:
            print("Found in modlist")
            self.modlist_frame.clear_modlist()
            for mod in found_mods:
                self.modlist_frame.add_item(mod)
        else:
            print("Not found in modlist")
            # Search the API
            found_mods = sdapi.search_mod(self.search_bar.get())
            self.modlist_frame.clear_modlist()
            for mod in found_mods:
                self.modlist_frame.add_item(mod)