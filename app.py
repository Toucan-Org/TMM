import customtkinter, configparser, os, json, logging, sys

import api.spacedock_api as sdapi
import utilities.utility as util
from gui_classes.header import MainHeaderFrame
from gui_classes.control_panel import ControlPanelButtonFrame, ControlPanelFrame
from gui_classes.modlist import ModListFrame, ModListHeaderFrame
from gui_classes.footer import FooterFrame
from gui_classes.dialog import InstallModDialogFrame

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        util.build_directories()

        logging.basicConfig(filename="./data/logs/2kan.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")
        self.logger = logging.getLogger(__name__)
        sdapi.logger = self.logger
        util.logger = self.logger

        self.program_version = "0.1.1"
        self.program_title = "2KAN"
        self.program_label = "Kerbal Space Program 2 Mod Manager"
        self.program_icon = "./data/images/icon.ico"
        self.program_logo = "./data/images/2kan_logo2.png"  

        self.load_config()
        self.load_modlist()


        # Configure window
        self.title(f"{self.program_title} - v{self.program_version}")
        self.geometry(f"{1300}x{1000}")
        
        # Set window icon
        self.wm_iconbitmap(self.program_icon)

        # Configure grid layout
        self.grid_columnconfigure((0,1,2,3), weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Create frames

        self.cp_button_frame = ControlPanelButtonFrame(master=self, config_file=self.config_file, logger=self.logger)
        self.cp_button_frame.grid(row=1, column=2, columnspan=2, padx=20, pady=(20, 5), sticky="nsew")
        
        self.control_panel_frame = ControlPanelFrame(master=self, cp_button_frame=self.cp_button_frame, config_file=self.config_file, logger=self.logger)
        self.control_panel_frame.grid(row=2, rowspan=2, column=2, columnspan=2, padx=20, pady=20, sticky="nsew")

        self.cp_button_frame.control_panel_frame = self.control_panel_frame

        self.modlist_frame = ModListFrame(master=self, control_panel_frame=self.control_panel_frame, logger=self.logger)
        self.modlist_frame.grid(row=2, rowspan=2, column=0, columnspan=2, pady=20, padx=20, sticky="nsew")

        self.control_panel_frame.modlist_frame = self.modlist_frame

        self.modlist_header = ModListHeaderFrame(master=self, modlist_frame=self.modlist_frame, config_file=self.config_file, logger=self.logger)
        self.modlist_header.grid(row=1, column=0, columnspan=2, padx=20, pady=(20,5), sticky="nsew")

        self.footer_frame = FooterFrame(master=self, modlist_frame=self.modlist_frame, config_file=self.config_file, logger=self.logger)
        self.footer_frame.install_directory_frame.cp_button_frame = self.cp_button_frame

        self.footer_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")

        self.main_header = MainHeaderFrame(master=self, modlist_frame=self.modlist_frame, modlist_header_frame=self.modlist_header,
                                           footer_frame=self.footer_frame, program_version=self.program_version, program_title=self.program_title,
                                            program_logo=self.program_logo, config_file=self.config_file, logger=self.logger)
        self.main_header.grid(row=0, column=0, columnspan=4, sticky="nsew")

        self.modlist_header.available_mods_menu.optionmenu_callback("All")
        self.install_mod_dialog = None

        if not util.check_bepinex_installed(self.config_file):
            # Check if there is a valid game install directory
            if self.config_file["KSP2"]["InstallDirectory"] != "":
                if self.install_mod_dialog is None or not self.install_mod_dialog.winfo_exists():
                    self.install_mod_dialog = InstallModDialogFrame(master=self, control_panel_frame=self.control_panel_frame)
                else:
                    self.install_mod_dialog.focus()        


    def load_config(self):
        self.config_file = configparser.ConfigParser()

        if os.path.isfile("config.ini"):
            self.logger.info("Config file found")
            self.config_file.read("config.ini")

        else:
            self.logger.info("Config file not found")
            self.config_file["KSP2"] = {}
            self.config_file["KSP2"]["InstallDirectory"] = ""
            self.config_file["KSP2"]["GameVersion"] = ""
            self.config_file["KSP2"]["GameTimeLog"] = "0"
            self.config_file["KSP2"]["ModlistPath"] = ""


    def load_modlist(self):
        if os.path.isfile("modlist.json"):
            self.logger.info("Modlist found!")
        else:
            with open("modlist.json", "w") as f:
                json.dump({"mods": []}, f, indent=4)

        self.config_file["KSP2"]["ModlistPath"] = os.path.abspath("modlist.json")

if __name__ == "__main__":
    app = App()
    app.mainloop()