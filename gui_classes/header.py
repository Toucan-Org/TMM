import customtkinter
import utilities.utility as util
import api.spacedock_api as sdapi
from PIL import Image


class MainHeaderFrame(customtkinter.CTkFrame):
    def __init__(self, master, program_logo, program_version, program_title, **kwargs):
        super().__init__(master)

        self.modlist_frame = kwargs.get("modlist_frame", None)
        self.modlist_header_frame = kwargs.get("modlist_header_frame", None)
        self.footer_frame = kwargs.get("footer_frame", None)

        self.grid_rowconfigure(6, weight=1)
        self.columnconfigure((2,4), weight=1)

        self.logo_image = customtkinter.CTkImage(Image.open(program_logo), size=(70, 70))

        self.logo_image_label = customtkinter.CTkLabel(self, image=self.logo_image, text="")
        self.logo_image_label.grid(row=0, rowspan=2, column=0, padx=10, pady=10)

        self.logo_label = customtkinter.CTkLabel(self, text=program_title, font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=1, padx=20, pady=(20, 10))

        self.version_label = customtkinter.CTkLabel(self, text=f"v{program_version}", font=customtkinter.CTkFont(size=10, weight="bold"))
        self.version_label.grid(row=1, column=1, padx=20, pady=(0, 10))

        self.install_available_switch = customtkinter.CTkSegmentedButton(self, font=customtkinter.CTkFont(size=16), values=["Installed", "Available"], command=self.on_install_available_switch_selected)
        self.install_available_switch.grid(row=0, rowspan=2, column=3, padx=10, pady=10)
        self.install_available_switch.set("Available")

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self, values=["Light", "Dark"],
                                                                       command=self.change_appearance_mode_event, width=50)
        self.appearance_mode_optionemenu.grid(row=0, rowspan=2, column=6, padx=10, pady=10)

        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self, values=["80%", "90%", "100%", "120%", "140%"],
                                                               command=self.change_scaling_event, width=50)
        self.scaling_optionemenu.grid(row=0, rowspan=2, column=7, padx=10, pady=10)

        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
        self.modlist_frame.update_appearance()
        self.footer_frame.update_appearance()

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def on_install_available_switch_selected(self, event):
        if self.install_available_switch.get() == "Installed":
            installed_mods = util.get_installed_mods()
            installed_mods.sort()
            self.modlist_frame.populate_modlist(installed_mods)
            self.modlist_header_frame.set_header_text("Installed Mods")
            self.modlist_header_frame.toggle_available_mods_menu(True)

        elif self.install_available_switch.get() == "Available":
            mods = sdapi.get_mods("")
            self.modlist_frame.populate_modlist(mods)
            self.modlist_header_frame.set_header_text("Available Mods > All")
            self.modlist_header_frame.toggle_available_mods_menu(False)