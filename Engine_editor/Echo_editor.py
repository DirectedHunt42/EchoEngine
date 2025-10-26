# Jack Murray
# Nova Foundry / Echo Editor
# v1.0.6

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageTk
import subprocess
import os
import shutil
import webbrowser
import tkinter as tk
from tkinter import font as tkFont, filedialog, Toplevel, Label

# ========================= Tooltip Helper =========================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
        widget.bind("<Motion>", self.move_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        self.tip_window = Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        label = Label(self.tip_window, text=self.text, justify="left",
                      background="#333", foreground="white",
                      relief="solid", borderwidth=1,
                      font=("Arial", 10))
        label.pack(ipadx=5, ipady=3)
        self.move_tip(event)

    def move_tip(self, event):
        if self.tip_window:
            x = event.x_root + 15
            y = event.y_root + 15
            screen_w = self.widget.winfo_screenwidth()
            screen_h = self.widget.winfo_screenheight()
            self.tip_window.update_idletasks()
            tw_w, tw_h = self.tip_window.winfo_width(), self.tip_window.winfo_height()
            if x + tw_w > screen_w:
                x = screen_w - tw_w - 10
            if y + tw_h > screen_h:
                y = screen_h - tw_h - 10
            self.tip_window.wm_geometry(f"+{x}+{y}")

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ========================= Main App =========================
app = ctk.CTk()
app.title("Echo Editor")

# ---------- Custom App Icon ----------
icon_path = r"Engine_editor\Icons\App_icon\Echo_editor.ico"
if os.path.exists(icon_path):
    try:
        app.iconbitmap(icon_path)
    except Exception as e:
        print(f"Could not set window icon: {e}")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
app.state("zoomed")
app.update()
screen_w, screen_h = app.winfo_screenwidth(), app.winfo_screenheight()

# ---------- Load Custom Font ----------
try:
    test_font = tkFont.Font(family="NovaFont", size=14)
    custom_font_family = test_font.actual("family")
except tk.TclError:
    test_font = tkFont.Font(family="Arial", size=14)
    custom_font_family = test_font.actual("family")

# ========================= Helper Functions =========================
def display_image_scaled(img_path, parent, scale=0.2):
    img_orig = Image.open(img_path)
    new_w = max(1, int(img_orig.width * scale))
    new_h = max(1, int(img_orig.height * scale))
    img_resized = img_orig.resize((new_w, new_h), Image.LANCZOS)
    tk_img = ImageTk.PhotoImage(img_resized)
    canvas = ctk.CTkCanvas(parent, width=new_w, height=new_h, bg=getattr(parent, "_fg_color", "#222222"), highlightthickness=0)
    canvas.pack(pady=10)
    canvas.create_image(new_w//2, new_h//2, image=tk_img)
    canvas.image = tk_img
    return canvas

# ========================= Game Setup Tab =========================
def setup_main_ui():
    main_frame = ctk.CTkFrame(app)
    main_frame.pack(expand=True, fill="both")

    tab_view = ctk.CTkTabview(main_frame, corner_radius=5, fg_color="#222222",
                              segmented_button_selected_color="#333333",
                              segmented_button_unselected_color="#555555")
    tab_view.pack(expand=True, fill="both")

    SAVE_COLOR = "#90EE90"
    SAVE_HOVER = "#6ECC6E"
    TEST_COLOR = "#FFB347"
    TEST_HOVER = "#FF9A00"
    RETURN_COLOR = "#FF6961"
    RETURN_HOVER = "#E04F4F"
    ABOUT_COLOR = "#2638DB"
    ABOUT_HOVER = "#321FDD"

    # ---------- Tabs ----------
    game_setup_tab = tab_view.add("Game Setup")
    tutorial_tab = tab_view.add("Tutorial")
    main_level_tab = tab_view.add("Main Level")
    export_tab = tab_view.add("Export")
    return_tab = tab_view.add("Return to Hub")
    test_app_tab = tab_view.add("Test App")
    about_tab = tab_view.add("About")
    help_tab = tab_view.add("Help")

    # ---------- Scrollable Inputs ----------
    scroll_frame = ctk.CTkScrollableFrame(game_setup_tab, fg_color="#2b2b2b")
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=(20,60))

    inputs = {}

    # ---------- Input Helpers ----------
    def add_input(parent, label_text, file_picker=False, font_only=False, tooltip_text="", accepted_ext=None, int_only=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5, padx=20)

        label = ctk.CTkLabel(row, text=label_text, font=(custom_font_family, 14), width=150, anchor="e")
        label.pack(side="left", padx=(0,10))
        if tooltip_text:
            ToolTip(label, tooltip_text)

        entry = ctk.CTkEntry(row, font=(custom_font_family, 14), fg_color="#444444", text_color="white")
        entry.pack(side="left", fill="x", expand=True, padx=(0,10))

        error_label = ctk.CTkLabel(row, text="", font=(custom_font_family, 10), text_color="red")
        error_label.pack(side="left", padx=(5,0))

        if file_picker:
            def pick_file():
                if font_only:
                    filepath = filedialog.askopenfilename(filetypes=[("TrueType Font", "*.ttf")])
                else:
                    filepath = filedialog.askopenfilename()
                if filepath:
                    entry.delete(0,"end")
                    entry.insert(0, filepath)
                validate_path(entry, error_label, accepted_ext)
            file_btn = ctk.CTkButton(row, text="📂", width=30, fg_color="#444444", hover_color="#666666", command=pick_file)
            file_btn.pack(side="left")

        def validate_path(entry_widget, label_widget, valid_ext=None, field_name=None):
            if valid_ext is None:
                label_widget.configure(text="")
                entry_widget.configure(fg_color="#444444")
                return

            path = entry_widget.get()

            if not path:
                label_widget.configure(text="")
                entry_widget.configure(fg_color="#444444")
            elif valid_ext and not any(path.endswith(ext) for ext in valid_ext):
                label_widget.configure(text=f"File must be {', '.join(valid_ext)}      ")
                entry_widget.configure(fg_color="#661111")
            elif not os.path.exists(path):
                label_widget.configure(text="File not found")
                entry_widget.configure(fg_color="#661111")
            else:
                label_widget.configure(text="")
                entry_widget.configure(fg_color="#444444")


        def validate_int(event=None):
            if int_only:
                val = entry.get()
                if val.strip() and not val.isdigit():
                    entry.configure(fg_color="#661111")
                    error_label.configure(text="Must be an integer")
                else:
                    entry.configure(fg_color="#444444")
                    error_label.configure(text="")

        entry.bind(
            "<FocusOut>",
            lambda e, field_name=label_text: (
                validate_path(entry, error_label, accepted_ext, field_name),
                validate_int()
            )
        )
        return entry

    def add_text_with_path(parent, label_text, tooltip_text=""):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=10, padx=20)

        label = ctk.CTkLabel(container, text=label_text, font=(custom_font_family, 14), anchor="w")
        label.pack(side="top", anchor="w")
        if tooltip_text:
            ToolTip(label, tooltip_text)

        top_frame = ctk.CTkFrame(container, fg_color="transparent")
        top_frame.pack(fill="x", pady=(5,0))

        path_var = tk.IntVar(value=1)
        text_var = tk.IntVar()
        path_chk = ctk.CTkCheckBox(top_frame, variable=path_var, text="")
        path_chk.pack(side="left", padx=(0,5))
        path_entry = ctk.CTkEntry(top_frame, font=(custom_font_family, 14), fg_color="#444444", text_color="white")
        path_entry.pack(side="left", fill="x", expand=True, padx=(0,10))
        ToolTip(path_entry, "Select a .txt file to use for this text section")
        file_btn = ctk.CTkButton(top_frame, text="📂", width=30, fg_color="#444444", hover_color="#666666",
                                 command=lambda: pick_txt_file(path_entry))
        file_btn.pack(side="left")

        err_path_lbl = ctk.CTkLabel(container, text="", font=(custom_font_family,10), text_color="red")
        err_path_lbl.pack(fill="x", pady=(2,0), padx=(35,0))

        bottom_frame = ctk.CTkFrame(container, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(5,0))
        text_chk = ctk.CTkCheckBox(bottom_frame, variable=text_var, text="")
        text_chk.pack(side="left", padx=(0,5))
        textbox = ctk.CTkTextbox(bottom_frame, font=(custom_font_family,14), height=100, fg_color="#444444", text_color="white")
        textbox.pack(side="left", fill="x", expand=True)
        ToolTip(textbox, "Type your text here")

        err_text_lbl = ctk.CTkLabel(container, text="", font=(custom_font_family,10), text_color="red")
        err_text_lbl.pack(fill="x", pady=(2,0), padx=(35,0))

        def toggle(var1,var2):
            if var1.get() == 1: var2.set(0)
        path_chk.configure(command=lambda: toggle(path_var,text_var))
        text_chk.configure(command=lambda: toggle(text_var,path_var))

        def validate_path(entry_widget, label_widget, valid_ext=None, field_name=None):
            if valid_ext is None:
                label_widget.configure(text="")
                entry_widget.configure(fg_color="#444444")
                return

            path = entry_widget.get()

            if not path:
                label_widget.configure(text="")
                entry_widget.configure(fg_color="#444444")
            elif valid_ext and not any(path.endswith(ext) for ext in valid_ext):
                label_widget.configure(text=f"File must be {', '.join(valid_ext)}")
                entry_widget.configure(fg_color="#661111")
            elif not os.path.exists(path):
                label_widget.configure(text="File not found")
                entry_widget.configure(fg_color="#661111")
            else:
                label_widget.configure(text="")
                entry_widget.configure(fg_color="#444444")

        path_entry.bind("<FocusOut>", lambda e: validate_path(path_entry, err_path_lbl, [".txt"]))

        return path_entry, textbox, path_var, text_var, err_path_lbl, err_text_lbl

    def pick_txt_file(entry_widget):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files","*.txt")])
        if filepath:
            entry_widget.delete(0,"end")
            entry_widget.insert(0, filepath)

    def add_section(frame, title):
        header = ctk.CTkLabel(frame, text=title, font=(custom_font_family,16,"bold"))
        header.pack(anchor="w", padx=10, pady=(10,5))
        divider = ctk.CTkFrame(frame, height=2, fg_color="#555555")
        divider.pack(fill="x", padx=10, pady=(0,10))

    # ---------- Sections ----------
    add_section(scroll_frame, "Basic")
    inputs["Title"] = add_input(scroll_frame,"Title:",tooltip_text="Game title")
    inputs["Font"] = add_input(scroll_frame,"Font:",file_picker=True,font_only=True,tooltip_text="Choose .ttf font",accepted_ext=[".ttf"])
    inputs["Title Font"] = add_input(scroll_frame,"Title Font:",file_picker=True,font_only=True,tooltip_text="Choose .ttf font for titles",accepted_ext=[".ttf"])
    inputs["Icon"] = add_input(scroll_frame,"Icon:",file_picker=True,tooltip_text="Game icon",accepted_ext=[".png",".jpg",".jpeg",".ico"])
    inputs["Music"] = add_input(scroll_frame,"Music:",file_picker=True,tooltip_text="Background music",accepted_ext=[".mp3",".wav",".ogg"])

    add_section(scroll_frame,"Text")
    inputs["Prolog Text"] = add_text_with_path(scroll_frame,"Prolog Text:",tooltip_text="Text shown at the beginning of the game - Select either file path or type into textbox")
    inputs["Cutscene Text"] = add_text_with_path(scroll_frame,"Cutscene Text:",tooltip_text="Text for transitioning from tutorial to gameplay - Select either file path or type into textbox")
    inputs["Game Over Text"] = add_text_with_path(scroll_frame,"Game Over Text:",tooltip_text="Text displayed when the player loses - Select either file path or type into textbox")
    inputs["Win Text"] = add_text_with_path(scroll_frame,"Win Text:",tooltip_text="Text displayed when the player wins - Select either file path or type into textbox")

    add_section(scroll_frame,"General Gameplay")
    inputs["Base Health"] = add_input(scroll_frame,"Base Health:",tooltip_text="Initial player health - Defaults to 1", int_only=True)
    inputs["Damage Chance"] = add_input(scroll_frame,"Damage Chance:",tooltip_text="Chance of taking damage each time the player enters a new room - In a fraction where the number entered is the denominator over 1 e.g. 1/x (Damage will not be taken during tutorial)", int_only=True)
    inputs["Win Location"] = add_input(scroll_frame,"Win Location:",tooltip_text="Room player must be in to win - Enter each coordinate with commas in between e.g. X,Y,Z")
    inputs["Win Items"] = add_input(scroll_frame,"Win Items:",tooltip_text="Items required to win - Enter each item with commas in between e.g. Item1,Item2")
    inputs["Tutorial Items"] = add_input(scroll_frame, "Tutorial Items:", tooltip_text="Tutorial will finish when these items are collected - Enter each item with commas in between e.g. Item1,Item2")

    # ========================= Save & Load Logic =========================
    # Hardcoded relative paths
    save_paths = {
        "Title": r"../Working_game/Text/Misc/Title.txt",
        "Font": r"../Working_game/Fonts/Font.ttf",
        "Title Font": r"../Working_game/Fonts/Title_Font.ttf",
        "Icon": r"../Working_game/Icons/Icon.png",
        "Music": r"../Working_game/Sounds/Background.wav",
        "Base Health": r"../Working_game/Finishing/Default_health.txt",
        "Damage Chance": r"../Working_game/Finishing/Damage_chance.txt",
        "Prolog Text": r"../Working_game/Text/Stories/Prolog/Prolog.txt",
        "Cutscene Text": r"../Working_game/Text/Stories/Tutorial/Tutorial_completed.txt",
        "Game Over Text": r"../Working_game/Text/Stories/Ending/Game_over.txt",
        "Win Text": r"../Working_game/Text/Stories/Ending/Win.txt",
        "Win Location": r"../Working_game/Finishing/Required_room.txt",
        "Win Items": r"../Working_game/Finishing/Required_items.txt",
        "Tutorial Items": r"../Working_game/Tutorial/Required_items.txt"
    }

    accepted_extensions = {
        "Font": [".ttf"],
        "Title Font": [".ttf"],
        "Icon": [".png", ".jpg", ".jpeg", ".ico"],
        "Music": [".mp3", ".wav", ".ogg"]
    }

    def load_and_highlight_existing():
        # """Checks for existing saved files and updates the UI accordingly."""
        LOADED_COLOR = "#006400" # A dark green color

        for key, rel_path in save_paths.items():
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)
            widget = inputs[key]

            # Check if file exists
            if os.path.exists(full_path):
                is_text_file = full_path.lower().endswith('.txt')
                file_has_content = os.path.getsize(full_path) > 0

                # Determine if the field should be marked as "loaded"
                should_highlight = False
                if is_text_file:
                    # For text files, check if the file has content
                    if file_has_content:
                        should_highlight = True
                else:
                    # For all other file types, just check if the file exists
                    should_highlight = True
                
                if should_highlight:
                    try:
                        # Handle standard text entry fields
                        if isinstance(widget, ctk.CTkEntry):
                            # For simple text fields, read content directly
                            if is_text_file:
                                with open(full_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    widget.delete(0, "end")
                                    widget.insert(0, content)
                            # Change the background color to green
                            widget.configure(fg_color=LOADED_COLOR)

                        # Handle the complex text-or-path widgets
                        elif isinstance(widget, tuple) and len(widget) == 6:
                            path_entry, textbox, path_var, text_var, _, _ = widget
                            
                            # Read content from the text file
                            with open(full_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Set to 'text' mode and load content into the textbox
                            text_var.set(1)
                            path_var.set(0)
                            textbox.delete("1.0", "end")
                            textbox.insert("1.0", content)
                            
                            # Set the background to green
                            textbox.configure(fg_color=LOADED_COLOR)
                            # Reset the path field color
                            path_entry.configure(fg_color="#444444")
                            
                    except Exception as e:
                        print(f"Error reading {key} file: {e}")
                else:
                    # File exists but is empty (only for text files), reset to default
                    if isinstance(widget, ctk.CTkEntry):
                        widget.configure(fg_color="#444444")
                        widget.delete(0, "end")
                    elif isinstance(widget, tuple) and len(widget) == 6:
                        path_entry, textbox, path_var, text_var, _, _ = widget
                        textbox.configure(fg_color="#444444")
                        textbox.delete("1.0", "end")
                        path_entry.configure(fg_color="#444444")
                        path_var.set(1)
                        text_var.set(0)
            else:
                # If the file doesn't exist, reset to default colors
                if isinstance(widget, ctk.CTkEntry):
                    widget.configure(fg_color="#444444")
                elif isinstance(widget, tuple) and len(widget) == 6:
                    path_entry, textbox, path_var, text_var, _, _ = widget
                    path_entry.configure(fg_color="#444444")
                    textbox.configure(fg_color="#444444")
                    # Set the default choice to path
                    path_var.set(1)
                    text_var.set(0)

    def validate_and_save():
        # Define which entry fields must always be filled
        required_text_fields = ["Title", "Base Health", "Damage Chance"]
        # **MODIFIED**: Fonts are now optional
        required_file_fields = []
        optional_file_fields = ["Font", "Title Font", "Music", "Icon"]

        errors = []
        for key, widget in inputs.items():
            path = os.path.join(os.path.dirname(__file__), save_paths[key])
            os.makedirs(os.path.dirname(path), exist_ok=True)  # Ensure folder exists

            # --- Entries ---
            if isinstance(widget, ctk.CTkEntry):
                value = widget.get().strip()

                # New logic for "Win Location", "Win Items", and "Tutorial Items"
                if key == "Win Location":
                    # Check for empty input
                    if not value:
                        errors.append(f"{key} is required.")
                        widget.configure(fg_color="#661111")
                        continue
                    
                    # Check for "double commas" or commas at start/end
                    if ",," in value or value.startswith(',') or value.endswith(','):
                        errors.append(f"{key}: Invalid format. Avoid adjacent commas.")
                        widget.configure(fg_color="#661111")
                        continue
                    
                    # Split by comma and clean up spaces
                    coords = [c.strip() for c in value.split(',')]
                    
                    # Check if there are exactly 3 parts and all are numbers
                    if len(coords) != 3 or not all(c.isdigit() or (c.startswith('-') and c[1:].isdigit()) for c in coords):
                        errors.append(f"{key}: Must have exactly three numbers (e.g., X,Y,Z).")
                        widget.configure(fg_color="#661111")
                        continue
                    
                    # If valid, format for saving (one per line)
                    save_value = "\n".join(coords)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(save_value)
                    widget.configure(fg_color="#444444")
                    continue

                elif key in ["Win Items", "Tutorial Items"]:
                    # Split by comma and save each item on a new line
                    items = [item.strip() for item in value.split(',')]
                    # Filter out any empty strings that might result from trailing commas or spaces
                    valid_items = [item for item in items if item]
                    save_value = "\n".join(valid_items)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(save_value)
                    widget.configure(fg_color="#444444")
                    continue

                # Old logic for other fields (no changes here)
                # ---------- Required Text ----------
                if key in required_text_fields:
                    if not value:
                        errors.append(f"{key} is required.")
                        widget.configure(fg_color="#661111")
                        continue
                    if key in ["Base Health", "Damage Chance"]:
                        if not value.isdigit() or int(value) <= 0:
                            errors.append(f"{key} must be a positive integer.")
                            widget.configure(fg_color="#661111")
                            continue
                    widget.configure(fg_color="#444444")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(value)

                # ---------- Required File ----------
                elif key in required_file_fields:
                    if not value:
                        errors.append(f"{key} is required.")
                        widget.configure(fg_color="#661111")
                        continue
                    if not os.path.exists(value):
                        errors.append(f"{key}: file not found.")
                        widget.configure(fg_color="#661111")
                        continue
                    if not any(value.lower().endswith(ext) for ext in accepted_extensions[key]):
                        errors.append(f"{key}: invalid file type. Must be {', '.join(accepted_extensions[key])}")
                        widget.configure(fg_color="#661111")
                        continue
                    widget.configure(fg_color="#444444")
                    shutil.copy(value, path)

                # ---------- Optional File ----------
                elif key in optional_file_fields:
                    if value:
                        if not os.path.exists(value):
                            errors.append(f"{key}: file not found.")
                            widget.configure(fg_color="#661111")
                            continue
                        if not any(value.lower().endswith(ext) for ext in accepted_extensions[key]):
                            errors.append(f"{key}: invalid file type. Must be {', '.join(accepted_extensions[key])}")
                            widget.configure(fg_color="#661111")
                            continue
                        widget.configure(fg_color="#444444")
                        if key == "Music":
                            if value.lower().endswith('.wav'):
                                shutil.copy(value, path)
                            else:
                                if shutil.which("ffmpeg") is not None:
                                    try:
                                        subprocess.run(
                                            ["ffmpeg", "-y", "-i", value, path],
                                            check=True,
                                            stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL
                                        )
                                    except Exception as e:
                                        errors.append(f"{key}: failed to convert music - {e}")
                                        widget.configure(fg_color="#661111")
                                else:
                                    errors.append(f"{key}: ffmpeg not found, cannot convert {os.path.splitext(value)[1]} to .wav. Please provide .wav file or install ffmpeg.")
                                    widget.configure(fg_color="#661111")
                        elif key == "Icon":
                            try:
                                img = Image.open(value)
                                img.save(path, "PNG")
                            except Exception as e:
                                errors.append(f"{key}: failed to convert icon - {e}")
                                widget.configure(fg_color="#661111")
                        else:
                            shutil.copy(value, path)
                    else:
                        if os.path.exists(path):
                            os.remove(path)
                        widget.configure(fg_color="#444444")

                # ---------- Default to plain text (optional) ----------
                else:
                    if value:
                        widget.configure(fg_color="#444444")
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(value)
                    else:
                        widget.configure(fg_color="#444444")

            # --- Text sections ---
            elif isinstance(widget, tuple) and len(widget) == 6:
                path_entry, textbox, path_var, text_var, err_path_lbl, err_text_lbl = widget
                if path_var.get():
                    src = path_entry.get().strip()
                    if not src:
                        errors.append(f"{key}: file path is required.")
                        path_entry.configure(fg_color="#661111")
                        err_path_lbl.configure(text="File required")
                        continue
                    if not os.path.exists(src):
                        errors.append(f"{key}: file not found.")
                        path_entry.configure(fg_color="#661111")
                        err_path_lbl.configure(text="File not found")
                        continue
                    if not src.lower().endswith(".txt"):
                        errors.append(f"{key}: file must be .txt")
                        path_entry.configure(fg_color="#661111")
                        err_path_lbl.configure(text="Invalid file type")
                        continue
                    # Instead of copying, read text and save it
                    with open(src, "r", encoding="utf-8") as f_in, open(path, "w", encoding="utf-8") as f_out:
                        f_out.write(f_in.read())
                    path_entry.configure(fg_color="#444444")
                    err_path_lbl.configure(text="")
                elif text_var.get():
                    txt = textbox.get("1.0","end").strip()
                    if not txt:
                        errors.append(f"{key}: text required.")
                        textbox.configure(fg_color="#661111")
                        err_text_lbl.configure(text="Text required")
                    else:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(txt)
                        textbox.configure(fg_color="#444444")
                        err_text_lbl.configure(text="")
                else:
                    errors.append(f"{key}: must provide either file or text.")
                    err_path_lbl.configure(text="Select file or text")
                    err_text_lbl.configure(text="")

        if errors:
            CTkMessagebox(title="Validation Error", message="\n".join(errors), icon="cancel")
        else:
            # On successful save, update the colors to green
            load_and_highlight_existing()
            CTkMessagebox(title="Success", message="All fields validated and saved!", icon="check")

    # ========================= Load existing data on startup =========================
    load_and_highlight_existing()

    # ========================= Save Button =========================
    save_button = ctk.CTkButton(game_setup_tab, text="Save", font=(custom_font_family,14),
                                 fg_color=SAVE_COLOR, hover_color=SAVE_HOVER, text_color="black",
                                 command=validate_and_save)
    save_button.place(relx=0.5, rely=1.0, anchor="s", y=-10)

    # ========================= Tutorial Tab =========================
    def setup_tutorial_tab(parent_tab, custom_font_family="Arial"):
        """
        Sets up the tutorial tab with a hover-and-click placement system
        and a dynamic room details panel, including room naming.
        """

        is_first_time = True

        # Store references for plus buttons and the grid state.
        # Each grid_state entry will now be a dictionary holding the room's frame and name.
        plus_buttons = {}
        grid_state = []
        GRID_SIZE = 40  # Size of each grid cell

        # Reference to the currently displayed room details frame.
        current_room_details_content_frame = None
        # Reference to the tutorial text label instance, allowing it to be shown/hidden.
        tutorial_text_label_instance = None


        def clear_info_display_frame():
            """Clears all widgets from the info_display_frame."""
            for widget in info_display_frame.winfo_children():
                widget.destroy()


        def update_room_name(entry_widget, grid_x, grid_y):
            """
            Updates the room's name in the grid_state and on the room's display label.
            """
            new_name = entry_widget.get()
            room_data = grid_state[grid_y][grid_x]
            room_data['name'] = new_name
            # Update the text on the room's label
            room_data['label'].configure(text=new_name)
            print(f"Room ({grid_x}, {grid_y}) named: {new_name}")


        def display_room_details(grid_x, grid_y):
            """
            Displays details for the clicked room in the info_display_frame,
            including a field to name the room.
            """
            nonlocal current_room_details_content_frame

            # Clear any content previously displayed in the info area
            clear_info_display_frame()

            # Get the current room data
            room_data = grid_state[grid_y][grid_x]
            current_name = room_data['name']

            # Create a new frame specifically for the room's details
            room_details_content_frame = ctk.CTkFrame(info_display_frame, fg_color="#333333", corner_radius=10)
            room_details_content_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # Store reference to this newly created frame
            current_room_details_content_frame = room_details_content_frame

            # Room title
            room_title = ctk.CTkLabel(room_details_content_frame,
                                    text=f"Details for Room ({grid_x}, {grid_y})",
                                    font=(custom_font_family, 18, "bold"),
                                    text_color="white")
            room_title.pack(pady=(10, 5))

            # Room Name Label
            name_label = ctk.CTkLabel(room_details_content_frame,
                                    text="Room Name:",
                                    font=(custom_font_family, 14),
                                    text_color="white")
            name_label.pack(anchor="w", padx=15, pady=(0, 2))

            # Room Name Entry Field
            name_entry = ctk.CTkEntry(room_details_content_frame,
                                    width=250,
                                    font=(custom_font_family, 14),
                                    placeholder_text="Enter room name")
            name_entry.insert(0, current_name) # Set current name as initial value
            name_entry.pack(padx=15, pady=(0, 10))
            # Bind the Enter key to update the name
            name_entry.bind("<Return>", lambda event: update_room_name(name_entry, grid_x, grid_y))
            # Bind focus lost to update the name
            name_entry.bind("<FocusOut>", lambda event: update_room_name(name_entry, grid_x, grid_y))


            # Placeholder for more room-specific content
            placeholder_text = ctk.CTkLabel(room_details_content_frame,
                                            text="This is where specific data for this room will go. \n"
                                                "You can add more labels, buttons, or entry fields here.",
                                            font=(custom_font_family, 14),
                                            text_color="#AAAAAA",
                                            wraplength=info_display_frame.winfo_width() - 30) # Ensures text wraps
            placeholder_text.pack(pady=(5, 10), padx=10)


        def show_tutorial_text():
            """Shows the default tutorial text in the info_display_frame."""
            nonlocal tutorial_text_label_instance
            clear_info_display_frame()
            tutorial_text_label_instance = ctk.CTkLabel(
                info_display_frame,
                text="""### How to Use the Room Grid
                    This is a tutorial for creating a level layout.

                    1.  **Hover over a room** to see where you can place a new one.
                    2.  **Click a '+' button** to add a new room in that spot.
                    3.  **Click an existing room** to view its specific details below and **name it!**
                    """,
                justify="left", font=(custom_font_family, 14),
                wraplength=info_display_frame.winfo_width() - 20 # Ensures text wraps
            )
            tutorial_text_label_instance.pack(fill="x", padx=10, pady=10)


        def add_room(grid_x, grid_y, is_immovable=False, initial_name="New Room", is_start_room=False):
            """Adds a room frame to the grid at the specified coordinates."""
            nonlocal grid_state

            # Create the room frame with white border
            room_frame = ctk.CTkFrame(grid_container, width=GRID_SIZE, height=GRID_SIZE,
                                    fg_color="#333333", border_width=2,
                                    border_color="white", corner_radius=0)
            room_frame.place(x=grid_x * GRID_SIZE + grid_canvas.winfo_x(),
                            y=grid_y * GRID_SIZE + grid_canvas.winfo_y())

            # Create a label inside the room frame to display the name and handle clicks/hovers
            room_label = ctk.CTkLabel(room_frame, text=initial_name, fg_color="transparent",
                                    width=GRID_SIZE, height=GRID_SIZE,
                                    font=(custom_font_family, 10), wraplength=GRID_SIZE-5,
                                    text_color="white") # Ensure text color is visible
            room_label.pack(fill="both", expand=True)

            # Store room object, its label, and name in grid_state
            grid_state[grid_y][grid_x] = {'frame': room_frame, 'label': room_label, 'name': initial_name}

            # Bind the click event to the internal label to open room details
            room_label.bind("<Button-1>", lambda event, x=grid_x, y=grid_y: display_room_details(x, y))

            # Bind hover event for showing adjacent placeholders
            if not is_immovable:
                room_label.bind("<Enter>", lambda event, x=grid_x, y=grid_y: show_adjacent_placeholders())
                
            if is_start_room:
                # We are using `is_first_time` global nonlocal in `setup_tutorial_tab` to handle
                # the single-time selection of the start room, instead of this parameter.
                pass


        def place_room(grid_x, grid_y):
            """Places a new room on the grid and updates the view."""
            add_room(grid_x, grid_y, initial_name=f"Room {grid_x}-{grid_y}") # Default name for new rooms
            show_adjacent_placeholders()  # Refresh available "+" buttons
            display_room_details(grid_x, grid_y) # Show details for the newly placed room


        def show_adjacent_placeholders():
            """Shows '+' buttons only adjacent to existing rooms."""
            nonlocal plus_buttons, grid_state
            global GRID_DIM_X, GRID_DIM_Y

            # Clear all existing plus buttons
            for btn in plus_buttons.values():
                btn.destroy()
            plus_buttons.clear()

            # Define directions for checking adjacent cells (right, left, down, up)
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for y in range(GRID_DIM_Y):
                for x in range(GRID_DIM_X):
                    if grid_state[y][x] is not None:  # Found an existing room
                        for dx, dy in directions:
                            adj_x, adj_y = x + dx, y + dy
                            # Check if adjacent cell is within grid boundaries
                            if 0 <= adj_x < GRID_DIM_X and 0 <= adj_y < GRID_DIM_Y:
                                # If the adjacent cell is empty, create a "+" button
                                if grid_state[adj_y][adj_x] is None:
                                    plus_button = ctk.CTkButton(
                                        grid_container, text="+", width=GRID_SIZE, height=GRID_SIZE,
                                        corner_radius=0, font=(custom_font_family, 24),
                                        fg_color="#444444", hover_color="#555555",
                                        command=lambda x=adj_x, y=adj_y: place_room(x, y)
                                    )
                                    plus_button.place(
                                        x=adj_x * GRID_SIZE + grid_canvas.winfo_x(),
                                        y=adj_y * GRID_SIZE + grid_canvas.winfo_y()
                                    )
                                    plus_buttons[(adj_x, adj_y)] = plus_button

        def setup_grid(event):
            """
            Initializes or re-initializes the grid when the grid_container is resized.
            """
            nonlocal grid_state
            global GRID_DIM_X, GRID_DIM_Y, _initial_grid_setup_done # Access the global flag

            # Clear canvas and existing rooms/buttons if resizing
            grid_canvas.delete("all")
            for btn in plus_buttons.values():
                btn.destroy()
            plus_buttons.clear()
            # Destroy existing room frames
            for row in grid_state:
                for cell in row:
                    if cell and 'frame' in cell and cell['frame'].winfo_exists():
                        cell['frame'].destroy()
            grid_state.clear()
            # selected_room_coords = None # This was commented out in original snippet, so kept it that way.


            # Get current dimensions of the container
            canvas_width = grid_container.winfo_width()
            canvas_height = grid_container.winfo_height()

            # Calculate grid dimensions based on container size and cell size
            GRID_DIM_X = canvas_width // GRID_SIZE
            GRID_DIM_Y = canvas_height // GRID_SIZE

            # Initialize grid_state with None for empty cells
            grid_state.extend([[None for _ in range(GRID_DIM_X)] for _ in range(GRID_DIM_Y)])

            # Calculate exact grid pixel dimensions
            grid_width = GRID_DIM_X * GRID_SIZE
            grid_height = GRID_DIM_Y * GRID_SIZE

            # Place the canvas at the top-left of its container
            grid_canvas.place(x=0, y=0, width=grid_width, height=grid_height)

            # Draw vertical grid lines
            for x in range(0, grid_width, GRID_SIZE):
                grid_canvas.create_line(x, 0, x, grid_height, fill="#555555")

            # Draw horizontal grid lines
            for y in range(0, grid_height, GRID_SIZE):
                grid_canvas.create_line(0, y, grid_width, y, fill="#555555")

            # Add the initial immovable room at (0,0) with a default name
            add_room(0, 0, is_immovable=True, initial_name="Start Room")
            
            # This is where the initial selection logic goes.
            # Only display the start room details if it's the very first time setup_grid is called.
            if not _initial_grid_setup_done:
                display_room_details(0, 0)
                _initial_grid_setup_done = True # Set the flag to True after initial selection

            # Show "+" buttons adjacent to the initial room
            show_adjacent_placeholders()

        # ========================= UI Layout =========================

        # Main frame for the tutorial tab
        tutorial_frame = ctk.CTkFrame(parent_tab, fg_color="#2b2b2b")
        tutorial_frame.pack(fill="both", expand=True, padx=20, pady=(20, 60))

        # Container for the interactive grid (top part of the tutorial_frame)
        grid_container = ctk.CTkFrame(tutorial_frame, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        # Canvas where grid lines are drawn
        grid_canvas = ctk.CTkCanvas(grid_container, bg="#333333", highlightthickness=0)
        grid_canvas.pack(fill="both", expand=True)

        # Frame for dynamic information display (either tutorial text or room details)
        info_display_frame = ctk.CTkFrame(tutorial_frame, fg_color="transparent")
        info_display_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Initially display the tutorial text
        show_tutorial_text()

        # Bind the setup_grid function to the grid_container's configure event,
        # so the grid adapts to resizing.
        grid_container.bind("<Configure>", setup_grid)

    setup_tutorial_tab(tutorial_tab, custom_font_family)

    # ========================= Main Level Tab =========================

    def setup_main_level_tab(parent_tab, custom_font_family="Arial"):
        """Sets up the main level editor with multiple floors and dynamic room placement."""

        GRID_SIZE = 40
        GRID_DIM_X, GRID_DIM_Y = 0, 0

        # Store all floors: floor_index -> (grid_state, rooms, plus_buttons)
        floors = {}
        current_floor = [0]  # using list so inner functions can modify by reference

        # ============ Floor Management ============
        def switch_floor(floor_index):
            current_floor[0] = floor_index
            if floor_index not in floors:
                # Initialize empty floor
                floors[floor_index] = {
                    "grid_state": [[None for _ in range(GRID_DIM_X)] for _ in range(GRID_DIM_Y)],
                    "plus_buttons": {},
                }
                # Add starting immovable square for new floor
                add_room(0, 0, is_immovable=True)

            redraw_floor()

        def add_new_floor():
            new_index = len(floors)
            switch_floor(new_index)
            refresh_floor_list()

        def refresh_floor_list():
            for widget in floor_list_frame.winfo_children():
                widget.destroy()

            for i in range(len(floors)):
                btn = ctk.CTkButton(
                    floor_list_frame, text=f"Floor {i+1}", width=80,
                    command=lambda idx=i: switch_floor(idx)
                )
                btn.pack(pady=5)

            add_btn = ctk.CTkButton(floor_list_frame, text="+ Add Floor",
                                    command=add_new_floor)
            add_btn.pack(pady=10)

        # ============ Grid System ============
        def add_room(grid_x, grid_y, is_immovable=False):
            floor = floors[current_floor[0]]
            grid_state = floor["grid_state"]

            room = ctk.CTkFrame(grid_container, width=GRID_SIZE, height=GRID_SIZE,
                                fg_color="#333333", border_width=2,
                                border_color="white", corner_radius=0)
            room.place(x=grid_x * GRID_SIZE + grid_canvas.winfo_x(),
                    y=grid_y * GRID_SIZE + grid_canvas.winfo_y())

            grid_state[grid_y][grid_x] = room

            if not is_immovable:
                room.bind("<Enter>", lambda event: show_adjacent_placeholders())

        def place_room(grid_x, grid_y):
            add_room(grid_x, grid_y)
            show_adjacent_placeholders()

        def show_adjacent_placeholders():
            floor = floors[current_floor[0]]
            grid_state = floor["grid_state"]
            plus_buttons = floor["plus_buttons"]

            # Clear old plus buttons
            for btn in plus_buttons.values():
                btn.destroy()
            plus_buttons.clear()

            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for y in range(GRID_DIM_Y):
                for x in range(GRID_DIM_X):
                    if grid_state[y][x] is not None:  # found a room
                        for dx, dy in directions:
                            adj_x, adj_y = x + dx, y + dy
                            if 0 <= adj_x < GRID_DIM_X and 0 <= adj_y < GRID_DIM_Y:
                                if grid_state[adj_y][adj_x] is None:
                                    plus_button = ctk.CTkButton(
                                        grid_container, text="+", width=GRID_SIZE, height=GRID_SIZE,
                                        corner_radius=0, font=(custom_font_family, 24),
                                        fg_color="#444444", hover_color="#555555",
                                        command=lambda x=adj_x, y=adj_y: place_room(x, y)
                                    )
                                    plus_button.place(
                                        x=adj_x * GRID_SIZE + grid_canvas.winfo_x(),
                                        y=adj_y * GRID_SIZE + grid_canvas.winfo_y()
                                    )
                                    plus_buttons[(adj_x, adj_y)] = plus_button

        def redraw_floor():
            # Clear everything in grid_container except grid_canvas
            for widget in grid_container.winfo_children():
                if widget != grid_canvas:
                    widget.destroy()

            floor = floors[current_floor[0]]
            grid_state = floor["grid_state"]

            # Redraw rooms
            for y in range(GRID_DIM_Y):
                for x in range(GRID_DIM_X):
                    if grid_state[y][x] is not None:
                        grid_state[y][x] = None
                        add_room(x, y)

            show_adjacent_placeholders()

        def setup_grid(event):
            nonlocal GRID_DIM_X, GRID_DIM_Y

            grid_canvas.delete("all")

            canvas_width = grid_container.winfo_width()
            canvas_height = grid_container.winfo_height()

            GRID_DIM_X = canvas_width // GRID_SIZE
            GRID_DIM_Y = canvas_height // GRID_SIZE

            grid_width = GRID_DIM_X * GRID_SIZE
            grid_height = GRID_DIM_Y * GRID_SIZE

            grid_canvas.place(x=0, y=0, width=grid_width, height=grid_height)

            # Draw vertical lines
            for x in range(0, grid_width, GRID_SIZE):
                grid_canvas.create_line(x, 0, x, grid_height, fill="#555555")

            # Draw horizontal lines
            for y in range(0, grid_height, GRID_SIZE):
                grid_canvas.create_line(0, y, grid_width, y, fill="#555555")

            # Initialize first floor if none exist
            if not floors:
                floors[0] = {
                    "grid_state": [[None for _ in range(GRID_DIM_X)] for _ in range(GRID_DIM_Y)],
                    "plus_buttons": {},
                }
                add_room(0, 0, is_immovable=True)

            show_adjacent_placeholders()
            refresh_floor_list()

        # ============ UI Layout ============
        main_frame = ctk.CTkFrame(parent_tab, fg_color="#2b2b2b")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(20, 60))

        # Left: Floor list
        floor_list_frame = ctk.CTkFrame(main_frame, fg_color="#1e1e1e", width=120)
        floor_list_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)

        # Right: Grid area
        grid_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        grid_container.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        grid_canvas = ctk.CTkCanvas(grid_container, bg="#333333", highlightthickness=0)
        grid_canvas.pack(fill="both", expand=True)

        grid_container.bind("<Configure>", setup_grid)

    setup_main_level_tab(main_level_tab, custom_font_family)

    # ========================= Return to Hub & Test App & Export =========================
    return_tab_button = tab_view._segmented_button._buttons_dict["Return to Hub"]
    return_tab_button.configure(fg_color=RETURN_COLOR, hover_color=RETURN_HOVER, text_color="black")

    test_tab_button = tab_view._segmented_button._buttons_dict["Test App"]
    test_tab_button.configure(fg_color=TEST_COLOR, hover_color=TEST_HOVER, text_color="black")

    export_tab_button = tab_view._segmented_button._buttons_dict["Export"]
    export_tab_button.configure(fg_color=SAVE_COLOR, hover_color=SAVE_HOVER, text_color="black")

    about_tab_button = tab_view._segmented_button._buttons_dict["About"]
    about_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")

    help_tab_button = tab_view._segmented_button._buttons_dict["Help"]
    help_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")

    previous_tab = [tab_view.get()]  # store previous tab in a mutable container

    def return_to_hub():
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.abspath(os.path.join(script_dir,".."))
            exe_path = os.path.join(parent_dir,"Echo_hub.exe")
            subprocess.Popen(exe_path)
            app.destroy()
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to launch Hub:\n{e}", icon="cancel")

    def launch_test_app():
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # The test app is inside the Working_game directory now
            exe_path = os.path.join(script_dir,"../Working_game/Echo_runner.exe")
            subprocess.Popen(exe_path)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to launch Test App:\n{e}", icon="cancel")

    def on_tab_change():
        current_tab = tab_view.get()
        about_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")
        help_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")
        if current_tab == "Return to Hub":
            return_to_hub()
        elif current_tab == "Test App":
            launch_test_app()
            # revert to previous tab
            tab_view.set(previous_tab[0])
            test_tab_button.configure(fg_color=TEST_COLOR, hover_color=TEST_HOVER, text_color="black")
            about_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")
        elif current_tab == "Export":
            tab_view.set(previous_tab[0])
            export_tab_button.configure(fg_color=SAVE_COLOR, hover_color=SAVE_HOVER, text_color="black")
            about_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")
        elif current_tab == "Help":
            os.startfile("Engine_editor\Docs\Help\Help.pdf")
            tab_view.set(previous_tab[0])
            help_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")
            about_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")
        else:
            # store the last active tab (not Test App)
            previous_tab[0] = current_tab

    tab_view._command = on_tab_change

    # ========================= About Tab =========================
    about_container = ctk.CTkScrollableFrame(about_tab, fg_color="#222222", corner_radius=10)
    about_container.pack(expand=True, fill="both", padx=20, pady=20)

    about_image_path1 = r"Engine_editor\Icons\Nova_foundry\Nova_foundry_wide_transparent.png"
    about_image_path2 = r"Engine_editor\Icons\Echo_engine\Echo_engine_transparent.png"
    display_image_scaled(about_image_path1, about_container, scale=0.2)
    display_image_scaled(about_image_path2, about_container, scale=0.2)

    version_label = ctk.CTkLabel(about_container,text="Echo Editor v1.0.6",font=(custom_font_family,16))
    version_label.pack(pady=(10,20))

    license_text = (
        "© Nova Foundry 2025. All rights reserved.\n\n"
        "This work is licensed under a Creative Commons Attribution-NoDerivatives 4.0 International License (CC BY-ND 4.0).\n\n"
        "You are free to:\n- Share: copy and redistribute the material in any medium or format.\n\n"
        "Under the following terms:\n- Attribution: You must give appropriate credit to Nova Foundry, provide a link to the license, and indicate if changes were made.\n"
        "- NoDerivatives: If you remix, transform, or build upon the material, you may not distribute the modified material.\n\n"
        "No additional restrictions:\n- You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.\n\n"
        "For full license text, see:"
    )
    license_label = ctk.CTkLabel(about_container,text=license_text,font=(custom_font_family,14),
                                  justify="left",wraplength=screen_w-100)
    license_label.pack(pady=(0,5), padx=10)

    license_link = ctk.CTkLabel(about_container,text="https://creativecommons.org/licenses/by-nd/4.0/",
                                 font=(custom_font_family,14,"underline"),
                                 text_color="#1E90FF", cursor="hand2", justify="left", wraplength=screen_w-100)
    license_link.pack(pady=(0,20), padx=10)
    license_link.bind("<Button-1>", lambda e: webbrowser.open("https://creativecommons.org/licenses/by-nd/4.0/"))

setup_main_ui()
app.mainloop()