import customtkinter, threading
import api.spacedock_api as sdapi


class AvailableModMenu(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.modlist_frame = kwargs.get("modlist_frame", None)
        self.header_text_frame = kwargs.get("header_text_frame", None)

        self.available_mods_menu = customtkinter.CTkOptionMenu(self, values=["All", "Featured", "Top", "New"], command=self.optionmenu_callback, width=100)
        self.available_mods_menu.grid(row=0, column=0)
        self.available_mods_menu.set("All")

    def fetch_mods(self, category):
        """Fetches the available mods from the website and populates the mod list"""

        print("Fetching available mods")

        mods = []
        mods = sdapi.get_mods(category)
        self.modlist_frame.populate_modlist(mods)

    def get_available_mods_category(self, category):
        print("Fetching available mods")
        self.modlist_frame.clear_modlist()   
        self.modlist_frame.loading_screen_frame.show() 
        t = threading.Thread(target=self.fetch_mods, args=(category,))
        t.start()

    def optionmenu_callback(self, choice):
        print("optionmenu dropdown clicked:", choice)
        if choice == "All":
            self.get_available_mods_category("")
            self.set_header_text("Available Mods > All")

        elif choice == "Featured":
            self.get_available_mods_category("/featured")
            self.set_header_text("Available Mods > Featured")

        elif choice == "Top":
            self.get_available_mods_category("/top")
            self.set_header_text("Available Mods > Top")

        elif choice == "New":

            self.get_available_mods_category("/new")
            self.set_header_text("Available Mods > New")

    def set_header_text(self, text):
        self.header_text_frame.configure(text=text)


        
class ModListHeaderFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.modlist_frame = kwargs.get("modlist_frame", None)

        self.header_text_frame = customtkinter.CTkLabel(self, text="", font=customtkinter.CTkFont(size=18, weight="bold"))
        self.header_text_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.available_mods_menu = AvailableModMenu(self, modlist_frame=self.modlist_frame, header_text_frame=self.header_text_frame)
        self.available_mods_menu.grid(row=0, column=1, sticky="e", padx=10, pady=10)

    def set_header_text(self, text):
        self.header_text_frame.configure(text=text)

    def toggle_available_mods_menu(self, val):
        """Toggles the available mods menu from appearing"""

        if val:
            self.available_mods_menu.grid_remove()
        else:
            self.available_mods_menu.grid(row=0, column=1, sticky="e", padx=10, pady=10)

        

class LoadingScreenFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.loading_label = customtkinter.CTkLabel(self, text="Retrieving mod data from spacedock.info...", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.loading_label.pack(pady=30)

    def show(self):
        self.grid(row=0, column=0, sticky="nsew")

    def hide(self):
        self.grid_remove()



class ModListFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.control_panel_frame = kwargs.get("control_panel_frame", None)
        self.loading_screen_frame = LoadingScreenFrame(self)
        self.item_widgets = []
        self.modlist = []

    def add_item(self, item):
        """Adds a mod item to the mod list"""

        row_frame = customtkinter.CTkFrame(self, fg_color="lightgray" if customtkinter.get_appearance_mode() == "Light" else "black", cursor="hand2")
        
        name_label = customtkinter.CTkLabel(row_frame, text=item.name, font=customtkinter.CTkFont(size=14, weight="bold"), bg_color="lightblue" if customtkinter.get_appearance_mode() == "Light" else "gray9", padx=10, anchor="w")
        name_label.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="w")
        
        author_label = customtkinter.CTkLabel(row_frame, text=f"by {item.author}", font=customtkinter.CTkFont(size=12), padx=5)
        author_label.grid(row=1, column=0, padx=10, sticky="w")
        
        summary_label = customtkinter.CTkLabel(row_frame, text=item.short_description[:50] + '...' if len(item.short_description) > 50 else item.short_description, font=customtkinter.CTkFont(size=12), padx=5, anchor="w")
        summary_label.grid(row=2, column=0, pady=(0, 10), padx=10, sticky="w")
        
        game_version_label = customtkinter.CTkLabel(row_frame, text=f"Game Version: {item.game_version}", font=customtkinter.CTkFont(size=10), padx=10)
        game_version_label.grid(row=2, column=4, padx=10, sticky="w")

        downloads_label = customtkinter.CTkLabel(row_frame, text=f"\u2193 {item.downloads}", font=customtkinter.CTkFont(size=12), padx=10)
        downloads_label.grid(row=1, column=4, padx=10, sticky="e")

        installed_label = customtkinter.CTkLabel(row_frame, text="Installed" if item.installed else "", font=customtkinter.CTkFont(size=12), text_color="green", padx=10)
        installed_label.grid(row=0, column=4, padx=10, sticky="e")
        
        row_frame.grid(sticky="ew", padx=5, pady=5)
        row_frame.columnconfigure(2, weight=1)

        row_frame.columnconfigure(4, minsize=70)
        self.item_widgets.append((row_frame, name_label, author_label, summary_label, game_version_label, installed_label))

        # Bind mod_select_event to button click event
        row_frame.bind("<Button-1>", lambda event: self.modlist_select(item))

        # On row_frame hover, do something
        row_frame.bind("<Enter>", lambda event, frame=row_frame: self.on_frame_hover(event, frame, name_label))
        row_frame.bind("<Leave>", lambda event, frame=row_frame: self.on_frame_leave(event, frame, name_label))


    def clear_modlist(self):
        """Clears the mod list"""

        self.modlist = []
        for widget_set in self.item_widgets:
            widget_set[0].destroy()
        self.item_widgets.clear()

    def populate_modlist(self, mods):     
        """Populates the mod list with the given mods"""   
        self.clear_modlist()

        for i in range(len(mods)):
            self.add_item(mods[i])
            self.modlist.append(mods[i])

        self.loading_screen_frame.hide()

    def update_appearance(self):
        """Updates the appearance of the mod list based on darkmode or lightmode selection"""

        for widget_set in self.item_widgets:
            widget_set[0].configure(fg_color="lightgray" if customtkinter.get_appearance_mode() == "Light" else "black")
            widget_set[1].configure(bg_color="lightblue" if customtkinter.get_appearance_mode() == "Light" else "gray9")
        
    def on_frame_hover(self, event, frame, name_label):
        frame.configure(fg_color="gray" if customtkinter.get_appearance_mode() == "Light" else "gray8")
        name_label.configure(bg_color="lightblue" if customtkinter.get_appearance_mode() == "Light" else "gray9")

    def on_frame_leave(self, event, frame, name_label):
        frame.configure(fg_color="lightgray" if customtkinter.get_appearance_mode() == "Light" else "black")
        name_label.configure(bg_color="lightblue" if customtkinter.get_appearance_mode() == "Light" else "gray9")
    
    def modlist_select(self, item):
        """Event handler for when a mod is selected in the mod list.
        loads the mod's info into the control panel"""

        print(f"Mod selected {item}")
        self.control_panel_frame.set_mod(item)