import customtkinter, threading
import utilities.utility as util
import api.spacedock_api as sdapi
from PIL import Image


class MainHeaderFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)

        self.modlist_frame = kwargs.get("modlist_frame", None)
        self.modlist_header_frame = kwargs.get("modlist_header_frame", None)
        self.footer_frame = kwargs.get("footer_frame", None)
        self.config_file = kwargs.get("config_file", None)
        self.program_version = kwargs.get("program_version", None)
        self.program_logo = kwargs.get("program_logo", None)
        self.program_title = kwargs.get("program_title", None)
        self.program_label = kwargs.get("program_label", None)


        self.logger = kwargs.get("logger", None)

        self.columnconfigure((2,3,4), weight=1)

        self.logo_image = customtkinter.CTkImage(Image.open(self.program_logo), size=(120, 120))

        self.logo_image_label = customtkinter.CTkLabel(self, image=self.logo_image, text="")
        self.logo_image_label.grid(row=0, rowspan=4, column=0, padx=10, pady=10)

        self.logo_label = customtkinter.CTkLabel(self, text=self.program_title, font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=1, column=1, padx=20, pady=(20, 0))

        self.program_label = customtkinter.CTkLabel(self, text=self.program_label, font=customtkinter.CTkFont(size=10))
        self.program_label.grid(row=2, column=1, padx=20, pady=(0, 10))

        self.version_label = customtkinter.CTkLabel(self, text=f"v{self.program_version}", font=customtkinter.CTkFont(size=10, weight="bold"))
        self.version_label.grid(row=3, column=1, padx=20, pady=(0, 10))

        self.install_available_switch_label_left = customtkinter.CTkLabel(self, text="")
        self.install_available_switch_label_left.grid(row=1, column=2, padx=(0, 10), sticky="e")
        self.install_available_switch = customtkinter.CTkSegmentedButton(self, font=customtkinter.CTkFont(size=16), values=["Installed", "Available"], command=self.on_install_available_switch_selected)
        self.install_available_switch.grid(row=0, rowspan=4, column=3, padx=10, pady=10, sticky="nsew")
        self.install_available_switch.set("Available")
        self.install_available_switch_label_right = customtkinter.CTkLabel(self, text="")
        self.install_available_switch_label_right.grid(row=1, column=4, padx=(10, 0), sticky="w")

        # Disabling this for now as its making things more difficult making two colour palettes

        # self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self, values=["Light", "Dark"],
        #                                                                command=self.change_appearance, width=50)
        # self.appearance_mode_optionemenu.grid(row=0, rowspan=2, column=6, padx=10, pady=10)

        # Check for update button
        self.check_for_update_button = customtkinter.CTkButton(self, text="Check for update", command=self.check_version_update)
        self.check_for_update_button.grid(row=1, rowspan=2, column=6, padx=5, pady=(10,0))

        self.notification_label = customtkinter.CTkLabel(self, text="", font=customtkinter.CTkFont(size=10, weight="bold"))
        self.notification_label.grid(row=3, column=6, padx=10, pady=(0,10))

        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self, values=["80%", "90%", "100%", "120%", "140%"],
                                                               command=self.change_scaling_event, width=50)
        self.scaling_optionemenu.grid(row=1, rowspan=2, column=7, padx=10, pady=(10,0))

        #self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.check_version_update()

    def check_version_update(self):
        self.logger.info("Checking for update...")
        latest_version = util.get_latest_2kan_version()

        if latest_version is None:
            self.notification_label.configure(text="Failed to check for update", text_color="red")
            # Clear this after 5 seconds
            self.after(7000, lambda: self.notification_label.configure(text=""))
            return
        
        if latest_version > self.program_version:
            self.notification_label.configure(text=f"Update available on 2KAN GitHub (v{latest_version})", text_color="green")

        else:
            self.notification_label.configure(text="Current version is latest", text_color="dodgerblue")
            self.after(7000, lambda: self.notification_label.configure(text=""))

        
    def change_appearance(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
        self.modlist_frame.update_appearance()
        self.footer_frame.update_appearance()

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def update_available_mods_threaded(self):
        self.modlist_header_frame.set_header_text("Available Mods > All")
        self.modlist_header_frame.toggle_available_mods_menu(False)
        self.modlist_frame.loading_screen_frame.show("Retrieving mod data from spacedock.info...")
        mods = sdapi.get_mods(self.config_file)
        self.modlist_frame.populate_modlist(mods)
        
        

    def on_install_available_switch_selected(self, event=None):
        """Called when the user selects the Installed/Available switch in the header."""
        
        if self.install_available_switch.get() == "Installed":
            self.modlist_frame.loading_screen_frame.show("Retrieving installed mods...")
            installed_mods = util.get_installed_mods(self.config_file["KSP2"]["ModlistPath"])
            installed_mods.sort()
            self.modlist_frame.populate_modlist(installed_mods)
            self.modlist_header_frame.set_header_text("Installed Mods")
            self.modlist_header_frame.toggle_available_mods_menu(True)

        elif self.install_available_switch.get() == "Available":
            thread = threading.Thread(target=self.update_available_mods_threaded)
            thread.start()