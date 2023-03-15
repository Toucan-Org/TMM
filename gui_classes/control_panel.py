import customtkinter, datetime
import utilities.utility as util
from tkinter import IntVar

class ControlPanelButtonFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)

        self.label = customtkinter.CTkLabel(self, text="Select a mod to view more details...", font=customtkinter.CTkFont(size=12), bg_color="lightblue" if customtkinter.get_appearance_mode() == "Light" else "gray9", padx=10, anchor="w")
        self.label.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="w")

        self.cp_button1 = customtkinter.CTkButton(self, text="", width=70, height=30, fg_color="green", hover_color="darkgreen")
        self.cp_button2 = customtkinter.CTkButton(self, text="", width=70, height=30, fg_color="red", hover_color="darkred")

        self.control_panel_frame = kwargs.get("control_panel_frame", None)


    def update_appearance(self):
        if self.control_panel_frame.selected_mod is not None:
            self.label.grid_remove()
            if self.control_panel_frame.selected_mod.installed:
                self.cp_button1.configure(text="Check for Updates", fg_color="blue", hover_color="darkblue", command=self.update_mod)
                self.cp_button1.grid(row=0, column=0, padx=10, pady=10, sticky="w")
                self.cp_button2.configure(text="Remove Mod", fg_color="red", hover_color="darkred", command=self.remove_mod)
                self.cp_button2.grid(row=0, column=1, padx=10, pady=10, sticky="w")
            else:
                self.cp_button1.configure(text="Install Mod", fg_color="green", hover_color="darkgreen", command=self.install_mod)
                self.cp_button1.grid(row=0, column=0, padx=10, pady=10, sticky="w")
                self.cp_button2.grid_remove()

    def install_mod(self):
        print("Installing mod")
        if util.download_mod(self.control_panel_frame.selected_mod, self.control_panel_frame.version_frame.selected_version, installdir=self.control_panel_frame.config["KSP2"]["install_path"]):
            self.control_panel_frame.selected_mod.installed = True
            # Set the modlist entry to installed
            self.set_install_status()
            self.control_panel_frame.modlist_frame.update_appearance()        

            self.update_appearance()

    def set_install_status(self):
        for widget_set, mod in zip(self.control_panel_frame.modlist_frame.item_widgets, self.control_panel_frame.modlist_frame.modlist):
            if mod == self.control_panel_frame.selected_mod:
                widget_set[5].configure(text="Installed")
                break

    def remove_mod(self):
        print("Removing mod")
        if util.uninstall_mod_ksp2(self.control_panel_frame.selected_mod, self.control_panel_frame.config["KSP2"]["install_path"]):
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

    def toggle_install_button_state(self, state):
        self.cp_button1.configure(state=state)


class ControlPanelFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        
        self.grid_columnconfigure((0,1,2,3), weight=1)
        self.selected_mod = None
        self.config = kwargs.get("config", None)

        self.cp_button_frame = kwargs.get("cp_button_frame", None)
        self.modlist_frame = kwargs.get("modlist_frame", None)

        # self.cp_button_frame = ControlPanelButtonFrame(self)
        # self.cp_button_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=10, pady=10)

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

        #Versions submenu
        self.version_label = customtkinter.CTkLabel(self, text="Versions", font=customtkinter.CTkFont(size=12, weight="bold", underline=True))
        self.version_label.grid(row=10, column=0, columnspan=4, padx=20, pady=20, sticky="w")
        self.version_frame = VersionFrame(self, fg_color="gray7")
        self.version_frame.grid(row=11, column=0, columnspan=4, padx=20, pady=10, sticky="nsew")


    def set_mod(self, item):
        self.selected_mod = item
        self.cp_button_frame.update_appearance()

        newest_version = item.get_newest_version()

        util.set_textbox_text(self.cp_mod_name, item.name)
        util.set_textbox_text(self.cp_mod_summary, item.short_description)
        util.set_textbox_text(self.cp_game_version, newest_version.game_version)
        util.set_textbox_text(self.cp_mod_version, newest_version.friendly_version)
        util.set_textbox_text(self.cp_download_count, str(item.downloads))
        util.set_textbox_text(self.cp_download_size, newest_version.download_size)
        util.set_textbox_text(self.cp_mod_author, item.author)
        util.set_textbox_text(self.cp_url, item.url)
        util.set_textbox_text(self.cp_mod_id, item.id)
        util.set_textbox_text(self.cp_website_url, item.website)
        util.set_textbox_text(self.cp_donations_url, item.donations)

        self.version_frame.populate_version_list(item)

class VersionFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure((1,2,3,4,5), weight=1)
        self.radio_var = IntVar(self, 0)

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
        self.clear_version_list()
        if mod.versions:
            self.selected_version = mod.versions[0]

        def radiobutton_event():
            self.selected_version = mod.versions[self.radio_var.get()]
            print(f"Selected version number: {self.selected_version}")


        for i, version in enumerate(mod.versions):
            self.selected = customtkinter.CTkRadioButton(self, width=10, variable=self.radio_var, value=i, text="", command=radiobutton_event)
            self.selected.grid(row=i+1, column=0, padx=10, pady=10, sticky="w")

            if version.installed:
                self.selected.select()

            self.version = customtkinter.CTkTextbox(self, height=15, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
            self.version.grid(row=i+1, column=1, padx=5, pady=10, sticky="w")
            util.set_textbox_text(self.version, version.friendly_version)

            self.game_version = customtkinter.CTkTextbox(self, height=15, font=customtkinter.CTkFont(size=12), wrap="none", state="disabled")
            self.game_version.grid(row=i+1, column=2, padx=5, pady=10, sticky="w")
            util.set_textbox_text(self.game_version, version.game_version)

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
        for widget in self.winfo_children():
            if isinstance(widget, (customtkinter.CTkRadioButton, customtkinter.CTkTextbox)):
                widget.destroy()