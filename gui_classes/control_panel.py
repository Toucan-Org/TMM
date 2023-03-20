import customtkinter, datetime
import utilities.utility as util
import api.spacedock_api as sdapi
from tkinter import IntVar



# The top button frame that contains the install/remove/update buttons
class ControlPanelButtonFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.grid_columnconfigure(2, weight=1)


        # Initialize the buttons and label
        self.label = customtkinter.CTkLabel(self, text="Select a mod to view more details...", font=customtkinter.CTkFont(size=12), bg_color="lightblue" if customtkinter.get_appearance_mode() == "Light" else "gray9", padx=10, anchor="w")
        self.label.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="w")

        self.cp_button1 = customtkinter.CTkButton(self, text="", width=70, height=30, fg_color="green", hover_color="darkgreen")
        self.cp_button2 = customtkinter.CTkButton(self, text="", width=70, height=30, fg_color="red", hover_color="darkred")

        self.status_label = customtkinter.CTkLabel(self, text="", font=customtkinter.CTkFont(size=10), bg_color="lightblue" if customtkinter.get_appearance_mode() == "Light" else "gray9", padx=10, anchor="e")
        self.status_label.grid(row=0, column=3, pady=(10, 0), padx=10, sticky="e")
        # Getting the control panel frame so we can access the selected mod (I dont like passing the entire object, but it works for now)
        self.control_panel_frame = kwargs.get("control_panel_frame", None)

    # Updates the appearance of the buttons and label based on the selected mod
    def update_appearance(self):
        if self.control_panel_frame.selected_mod is not None:
            self.label.grid_remove()
            if self.control_panel_frame.selected_mod.installed:
                self.cp_button1.configure(text="Check for Updates", fg_color="blue", hover_color="darkblue", command=self.update_mod)
                self.cp_button1.grid(row=0, column=0, padx=10, pady=10, sticky="w")
                self.cp_button2.configure(text="Remove Mod", fg_color="red", hover_color="darkred", command=self.remove_mod)
                self.cp_button2.grid(row=0, column=1, padx=10, pady=10, sticky="w")

                self.status_label.configure(text=f"Installed ({self.control_panel_frame.selected_mod.get_installed_version().friendly_version})")
            else:
                self.cp_button1.configure(text="Install Mod", fg_color="green", hover_color="darkgreen", command=lambda: self.install_mod(self.control_panel_frame.selected_mod, self.control_panel_frame.version_frame.selected_version))
                self.cp_button1.grid(row=0, column=0, padx=10, pady=10, sticky="w")
                self.cp_button2.grid_remove()

                self.status_label.configure(text="Not Installed")


    # The functions that are called when the buttons are pressed

    def install_mod(self, mod, version):
        print("Installing mod")
        if util.download_install_mod(mod, version, installdir=self.control_panel_frame.config_file["KSP2"]["InstallDirectory"]):
            self.set_install_status()
            self.control_panel_frame.selected_mod.installed = True
            self.control_panel_frame.selected_mod.set_installed_version(version)
            self.control_panel_frame.modlist_frame.update_appearance()
            # The mod has been installed, so we can now update the buttons and label
            self.update_appearance()


    def set_install_status(self):
        """Sets the install status of the selected mod to installed in the modlist frame"""
        for widget_set, mod in zip(self.control_panel_frame.modlist_frame.item_widgets, self.control_panel_frame.modlist_frame.modlist):
            if mod == self.control_panel_frame.selected_mod:
                widget_set[5].configure(text="Installed")
                break


    def remove_mod(self):
        print("Removing mod")
        if util.uninstall_mod(self.control_panel_frame.selected_mod, self.control_panel_frame.config_file["KSP2"]["InstallDirectory"]):
            self.control_panel_frame.selected_mod.installed = False

            for widget_set, mod in zip(self.control_panel_frame.modlist_frame.item_widgets, self.control_panel_frame.modlist_frame.modlist):
                if mod == self.control_panel_frame.selected_mod:
                    widget_set[5].configure(text="")
                    break

            self.control_panel_frame.modlist_frame.update_appearance()

        else:
            print("Failed to remove mod")
        
        self.update_appearance()


    def update_mod(self):
        print("Updating mod")
        update_version = sdapi.check_mod_update(self.control_panel_frame.selected_mod)
        

        if update_version is not None:
            print(f"Installed version was: {self.control_panel_frame.selected_mod.get_installed_version().friendly_version}")
            # Remove the mod and then install the newest version
            self.remove_mod()
            self.install_mod(self.control_panel_frame.selected_mod, update_version)
            print(f"New version is: {self.control_panel_frame.selected_mod.get_installed_version().friendly_version}")
            self.status_label.configure(text=f"Version Updated to ({self.control_panel_frame.selected_mod.get_installed_version().friendly_version})")
            # Update the version radio button to the newest version
            self.control_panel_frame.version_frame.update_version_radiobuttons(update_version)

        else:
            print("No update available")
            self.status_label.configure(text=f"Version is Latest ({self.control_panel_frame.selected_mod.get_installed_version().friendly_version})")


    def toggle_install_button_state(self, state):
        """Toggles the state of the install button between normal and disabled"""
        self.cp_button1.configure(state=state)

# The main control panel frame
class ControlPanelFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        
        self.grid_columnconfigure((0,1,2,3), weight=1)
        self.selected_mod = None
        self.install_version = None
        self.config_file = kwargs.get("config_file", None)

        self.cp_button_frame = kwargs.get("cp_button_frame", None)
        self.modlist_frame = kwargs.get("modlist_frame", None)

        # Init the labels and textboxes

        self.cp_mod_name_label = customtkinter.CTkLabel(self, text="Mod Name:", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.cp_mod_name_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.cp_mod_name = customtkinter.CTkTextbox(self, height=10, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
        self.cp_mod_name.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        self.cp_game_version_label = customtkinter.CTkLabel(self, text="Game Version:", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.cp_game_version_label.grid(row=0, column=2, padx=20, pady=10, sticky="w")
        self.cp_game_version = customtkinter.CTkTextbox(self, height=10,  font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
        self.cp_game_version.grid(row=1, column=2, padx=20, pady=10, sticky="nsew")

        self.cp_mod_version_label = customtkinter.CTkLabel(self, text="Mod Version:", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.cp_mod_version_label.grid(row=0, column=3, padx=20, pady=10, sticky="w")
        self.cp_mod_version = customtkinter.CTkTextbox(self, height=10, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
        self.cp_mod_version.grid(row=1, column=3, padx=20, pady=10, sticky="nsew")

        self.cp_mod_author_label = customtkinter.CTkLabel(self, text="Author:", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.cp_mod_author_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.cp_mod_author = customtkinter.CTkTextbox(self, height=10, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
        self.cp_mod_author.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        self.cp_download_count_label = customtkinter.CTkLabel(self, text="Downloads:", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.cp_download_count_label.grid(row=2, column=2, padx=20, pady=10, sticky="w")
        self.cp_download_count = customtkinter.CTkTextbox(self, height=10, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
        self.cp_download_count.grid(row=3, column=2, padx=20, pady=10, sticky="nsew")

        self.cp_download_size_label = customtkinter.CTkLabel(self, text="Size:", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.cp_download_size_label.grid(row=2, column=3, padx=20, pady=10, sticky="w")
        self.cp_download_size = customtkinter.CTkTextbox(self, height=10, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
        self.cp_download_size.grid(row=3, column=3, padx=20, pady=10, sticky="nsew")

        self.cp_mod_summary_label = customtkinter.CTkLabel(self, text="Summary: ", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.cp_mod_summary_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.cp_mod_summary = customtkinter.CTkTextbox(self, height=100, font=customtkinter.CTkFont(size=12), wrap="word", state="disabled")
        self.cp_mod_summary.grid(row=5, column=0, columnspan=4, padx=20, pady=10, sticky="nsew")

        self.cp_mod_id_label = customtkinter.CTkLabel(self, text="Mod ID:", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.cp_mod_id_label.grid(row=6, column=0, padx=20, pady=10, sticky="w")
        self.cp_mod_id = customtkinter.CTkTextbox(self, height=10, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
        self.cp_mod_id.grid(row=7, column=0, padx=20, pady=10, sticky="nsew")

        self.cp_url_label = customtkinter.CTkLabel(self, text="URL:", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.cp_url_label.grid(row=6, column=1,columnspan=3, padx=20, pady=10, sticky="w")
        self.cp_url = customtkinter.CTkTextbox(self, height=10, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
        self.cp_url.grid(row=7, column=1, columnspan=3, padx=20, pady=10, sticky="nsew")

        self.cp_website_url_label = customtkinter.CTkLabel(self, text="Website:", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.cp_website_url_label.grid(row=8, column=2, padx=20, pady=10, sticky="w")
        self.cp_website_url = customtkinter.CTkTextbox(self, height=10, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
        self.cp_website_url.grid(row=9, column=2, columnspan=2, padx=20, pady=10, sticky="nsew")

        self.cp_donations_url_label = customtkinter.CTkLabel(self, text="Donations:", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.cp_donations_url_label.grid(row=8, column=0, padx=20, pady=10, sticky="w")
        self.cp_donations_url = customtkinter.CTkTextbox(self, height=10, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
        self.cp_donations_url.grid(row=9, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        #Versions submenu (see VersionFrame class)
        self.version_label = customtkinter.CTkLabel(self, text="Versions", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.version_label.grid(row=10, column=0, columnspan=4, padx=20, pady=20, sticky="w")
        self.version_frame = VersionFrame(self, config_file=self.config_file)
        self.version_frame.grid(row=11, column=0, columnspan=4, padx=20, pady=10, sticky="nsew")


    def set_mod(self, mod):
        """Called when a mod is selected in the modlist. 
        Updates the mod info and the version list in the control panel."""

        self.selected_mod = mod
        self.cp_button_frame.update_appearance()

        newest_version = mod.get_newest_version()

        util.set_textbox_text(self.cp_mod_name, mod.name)
        util.set_textbox_text(self.cp_mod_summary, mod.short_description)
        util.set_textbox_text(self.cp_game_version, newest_version.game_version)
        util.set_textbox_text(self.cp_mod_version, newest_version.friendly_version)
        util.set_textbox_text(self.cp_download_count, str(mod.downloads))
        util.set_textbox_text(self.cp_download_size, newest_version.download_size)
        util.set_textbox_text(self.cp_mod_author, mod.author)
        util.set_textbox_text(self.cp_url, mod.url)
        util.set_textbox_text(self.cp_mod_id, mod.id)
        util.set_textbox_text(self.cp_website_url, mod.website)
        util.set_textbox_text(self.cp_donations_url, mod.donations)

        self.version_frame.populate_version_list(mod)


    def install_bepinex(self):
        mod = sdapi.search_mod(mod_name=None, mod_id=3277)
        version = mod.get_newest_version()
        self.selected_mod = mod
        self.cp_button_frame.install_mod(mod, version)


# This frame contains a list of versions for a selected mod
class VersionFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="gray8")
        self.grid_columnconfigure((1,2,3,4,5), weight=1)
        self.radio_var = IntVar(self, 0) # This tracks which version radio button is selected
        self.config_file = kwargs.get("config_file", None)

        self.selected_label = customtkinter.CTkLabel(self, text="Selected", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.selected_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")

        self.version_label = customtkinter.CTkLabel(self, text="Mod Version", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.version_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        self.game_version_label = customtkinter.CTkLabel(self, text="Game Version", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.game_version_label.grid(row=0, column=2, padx=5, pady=10, sticky="w")

        self.downloads_label = customtkinter.CTkLabel(self, text="Downloads", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.downloads_label.grid(row=0, column=3, padx=5, pady=10, sticky="w")

        self.download_size_label = customtkinter.CTkLabel(self, text="Size", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.download_size_label.grid(row=0, column=4, padx=5, pady=10, sticky="w")

        self.created_label = customtkinter.CTkLabel(self, text="Created", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.created_label.grid(row=0, column=5, padx=5, pady=5, sticky="w")


    def populate_version_list(self, mod):
        """Populates the version list with the versions of the selected mod."""
        self.clear_version_list()
        if mod.versions:
            self.selected_version = mod.versions[0]

        def radiobutton_event():
            """Called when a version radio button is selected."""
            self.selected_version = mod.versions[self.radio_var.get()]
            print(f"Selected version number: {self.selected_version}")


        for i, version in enumerate(mod.versions):
            self.selected = customtkinter.CTkRadioButton(self, width=10, variable=self.radio_var, value=i, text="", command=radiobutton_event)
            self.selected.grid(row=i+1, column=0, padx=10, pady=10, sticky="w")

            # Select the radio button if the version is installed already
            if version.installed:
                self.selected.select()

            self.version = customtkinter.CTkTextbox(self, height=15, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
            self.version.grid(row=i+1, column=1, padx=5, pady=10, sticky="w")
            util.set_textbox_text(self.version, version.friendly_version)


            self.game_version = customtkinter.CTkTextbox(self, height=15, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
            self.game_version.grid(row=i+1, column=2, padx=5, pady=10, sticky="w")
            util.set_textbox_text(self.game_version, version.game_version)

            # Set the color of the mod game version text to green if it matches the current game version
            if version.game_version.strip() == self.config_file['KSP2']['GameVersion'].strip():
                util.set_label_color(self.game_version, "green")
            else:
                util.set_label_color(self.game_version, "red")

            self.downloads = customtkinter.CTkTextbox(self, height=15, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
            self.downloads.grid(row=i+1, column=3, padx=5, pady=10, sticky="w")
            util.set_textbox_text(self.downloads, version.downloads)

            self.download_size = customtkinter.CTkTextbox(self, height=15, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
            self.download_size.grid(row=i+1, column=4, padx=5, pady=10, sticky="w")
            util.set_textbox_text(self.download_size, version.download_size)

            self.created = customtkinter.CTkTextbox(self, height=15, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
            self.created.grid(row=i+1, column=5, padx=5, pady=10, sticky="w")
            date_format = datetime.datetime.fromisoformat(version.created).strftime("%d %b %Y")
            util.set_textbox_text(self.created, date_format)

    def clear_version_list(self):
        """Clears the version list."""
        for widget in self.winfo_children():
            if isinstance(widget, (customtkinter.CTkRadioButton, customtkinter.CTkTextbox)):
                widget.destroy()

    def update_version_radiobuttons(self):
        """Updates the version radio buttons to reflect the installed status of the version."""
        for i, version in enumerate(self.selected_mod.versions):
            if version.installed:
                self.selected.select()
            else:
                self.selected.deselect()