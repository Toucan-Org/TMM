import customtkinter

class InstallModDialogFrame(customtkinter.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.title("Required Dependencies")
        self.control_panel_frame = kwargs.get("control_panel_frame", None)
        self.resizable(False, False)

        self.label = customtkinter.CTkLabel(self, text="Install Required", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.subtitle_label = customtkinter.CTkLabel(self, text="SpaceWarp and BepInEx are required to install mods. Install them now?")
        self.subtitle_label.grid(row=1, column=0, padx=10, pady=10)

        self.button_frame = customtkinter.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, padx=10, pady=10)

        self.yes_button = customtkinter.CTkButton(self.button_frame, text="Yes", command=self.yes_button_clicked)
        self.yes_button.grid(row=0, column=0, padx=10, pady=10)

        self.no_button = customtkinter.CTkButton(self.button_frame, text="No", command=self.no_button_clicked)
        self.no_button.grid(row=0, column=1, padx=10, pady=10)

    def yes_button_clicked(self):
        self.control_panel_frame.install_bepinex()
        self.destroy()
    
    def no_button_clicked(self):
        self.destroy()

