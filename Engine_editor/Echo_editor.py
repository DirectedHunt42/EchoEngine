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
from collections import deque
import sys

# Base path for static resources (bundled in _MEIPASS for EXE, script dir otherwise)
resource_base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Base path for saving/loading dynamic files (EXE dir for bundled, script dir otherwise)
save_base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

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
icon_path = os.path.join(resource_base_path, "Engine_editor", "Icons", "App_icon", "Echo_editor.ico")
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
    LOADED_COLOR = "#006400"  # Dark green for loaded fields

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
            full_path = os.path.join(save_base_path, rel_path)
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
                                    content = f.read().strip()
                                    if key in ["Win Location", "Win Items", "Tutorial Items"]:
                                        content = content.replace('\n', ',')
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
    save_tutorial_button = ctk.CTkButton(tutorial_tab, text="Save", font=(custom_font_family,14),
                                 fg_color=SAVE_COLOR, hover_color=SAVE_HOVER, text_color="black",
                                 )
    save_tutorial_button.place(relx=0.5, rely=1.0, anchor="s", y=-10)
    save_main_level_button = ctk.CTkButton(main_level_tab, text="Save", font=(custom_font_family,14),
                                 fg_color=SAVE_COLOR, hover_color=SAVE_HOVER, text_color="black",
                                 )
    save_main_level_button.place(relx=0.5, rely=1.0, anchor="s", y=-10)

   # ========================= Tutorial Tab =========================
    def setup_tutorial_tab(parent_tab, custom_font_family="Arial"):
        # Single-floor grid editor (right: grid)
        GRID_SIZE = 40
        GRID_DIM_X, GRID_DIM_Y = 33, 20

        # Simplified data structure for a single floor
        grid_state = [[None for _ in range(GRID_DIM_X)] for _ in range(GRID_DIM_Y)]
        plus_buttons = {}

        # Info display on the right side of the editor
        info_display_frame = None
        
        # --- CONSTANT FOR BACKGROUND/ROOM COLOR ---
        BACKGROUND_COLOR = "#333333"

        current_room = [None, None]
        FILLED_COLOR = "green"
        directions_2d = [(0,1),(0,-1),(1,0),(-1,0)]

        # NEW: Track the current mode (True for Add Mode, False for Remove Mode)
        is_add_mode = [True]

        def can_remove_tutorial(rx, ry):
            if rx == 0 and ry == 0:
                return False
            total_rooms = sum(1 for row in grid_state for c in row if c is not None)
            if total_rooms <= 1:
                return False
            temp = grid_state[ry][rx]
            grid_state[ry][rx] = None
            visited = set()
            q = deque([(0,0)])
            visited.add((0,0))
            while q:
                x, y = q.popleft()
                for dx, dy in directions_2d:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_DIM_X and 0 <= ny < GRID_DIM_Y and grid_state[ny][nx] is not None and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        q.append((nx, ny))
            connected = len(visited)
            grid_state[ry][rx] = temp
            return connected == total_rooms - 1

        def remove_room_tutorial(grid_x, grid_y):
            if not can_remove_tutorial(grid_x, grid_y):
                return
            grid_state[grid_y][grid_x]['frame'].destroy()
            grid_state[grid_y][grid_x] = None
            show_adjacent_placeholders_tutorial()

        def clear_info_display_frame_tutorial():
            nonlocal info_display_frame
            if info_display_frame is None:
                return
            for w in info_display_frame.winfo_children():
                try:
                    w.destroy()
                except Exception:
                    pass

        def update_room_name_tutorial(entry_widget, grid_x, grid_y):
            nonlocal grid_state
            new_name = entry_widget.get()
            if not grid_state:
                return
            cell = grid_state[grid_y][grid_x]
            if cell is None:
                return
            cell['name'] = new_name
            if 'label' in cell and cell['label']:
                try:
                    cell['label'].configure(text=new_name)
                    all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items'])
                    cell['label'].configure(text_color=FILLED_COLOR if all_filled else "white")
                except Exception:
                    pass

        def display_room_details_tutorial(grid_x, grid_y):
            nonlocal info_display_frame
            nonlocal grid_state
            nonlocal current_room
            if info_display_frame is None:
                return
            clear_info_display_frame_tutorial()
            current_room[:] = [grid_x, grid_y]
            
            if not grid_state:
                return
                    
            cell = grid_state[grid_y][grid_x]
            if cell is None:
                return
            current_name = cell.get('name', '')
            room_details_content_frame = ctk.CTkFrame(info_display_frame, fg_color="#333333", corner_radius=10)
            room_details_content_frame.pack(fill="both", expand=True, padx=5, pady=5)
            room_title = ctk.CTkLabel(room_details_content_frame,
                                    text=f"Details for Room ({grid_x}, {grid_y})",
                                    font=(custom_font_family, 18, "bold"),
                                    text_color="white")
            room_title.pack(pady=(10, 5))
            name_label = ctk.CTkLabel(room_details_content_frame,
                                    text="Room Name:",
                                    font=(custom_font_family, 14),
                                    text_color="white")
            name_label.pack(anchor="w", padx=15, pady=(0, 2))
            name_entry = ctk.CTkEntry(room_details_content_frame,
                                    width=250,
                                    font=(custom_font_family, 14),
                                    placeholder_text="Enter room name")
            name_entry.insert(0, current_name)
            name_entry.pack(padx=15, pady=(0, 10))
            if current_name:
                name_entry.configure(fg_color=LOADED_COLOR)
            else:
                name_entry.configure(fg_color="#444444")
            desc_label = ctk.CTkLabel(room_details_content_frame,
                                    text="Room Description:",
                                    font=(custom_font_family, 14),
                                    text_color="white")
            desc_label.pack(anchor="w", padx=15, pady=(10, 2))
            desc_text = ctk.CTkTextbox(room_details_content_frame,
                                    width=250,
                                    height=100,
                                    font=(custom_font_family, 14),
                                    fg_color="#444444")
            desc = cell.get('desc', '')
            desc_text.insert("1.0", desc)
            desc_text.pack(padx=15, pady=(0, 10))
            if desc:
                desc_text.configure(fg_color=LOADED_COLOR)
            else:
                desc_text.configure(fg_color="#444444")
            items_label = ctk.CTkLabel(room_details_content_frame,
                                    text="Findable Items (comma-separated):",
                                    font=(custom_font_family, 14),
                                    text_color="white")
            items_label.pack(anchor="w", padx=15, pady=(0, 2))
            items_entry = ctk.CTkEntry(room_details_content_frame,
                                    width=250,
                                    font=(custom_font_family, 14),
                                    placeholder_text="Enter items, separated by commas")
            items = cell.get('findable_items', '')
            items_entry.insert(0, items)
            items_entry.pack(padx=15, pady=(0, 10))
            if items:
                items_entry.configure(fg_color=LOADED_COLOR)
            else:
                items_entry.configure(fg_color="#444444")
            name_entry.bind("<Return>", lambda event: update_room_name_tutorial(name_entry, grid_x, grid_y))
            name_entry.bind("<FocusOut>", lambda event: update_room_name_tutorial(name_entry, grid_x, grid_y))

            def update_desc(event=None):
                cell['desc'] = desc_text.get("1.0", "end").strip()
                all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items'])
                cell['label'].configure(text_color=FILLED_COLOR if all_filled else "white")

            def update_items(event=None):
                cell['findable_items'] = items_entry.get().strip()
                all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items'])
                cell['label'].configure(text_color=FILLED_COLOR if all_filled else "white")

            desc_text.bind("<FocusOut>", update_desc)
            items_entry.bind("<FocusOut>", update_items)
            placeholder_text = ctk.CTkLabel(room_details_content_frame,
                                            text="This is where specific data for this room will go.",
                                            font=(custom_font_family, 14),
                                            text_color="#AAAAAA",
                                            wraplength=info_display_frame.winfo_width() - 30)
            placeholder_text.pack(pady=(5, 10), padx=10)

        def add_room_tutorial(grid_x, grid_y, is_immovable=False, initial_name="Room"):
            nonlocal grid_state
            room = ctk.CTkFrame(grid_container, width=GRID_SIZE, height=GRID_SIZE,
                                fg_color=BACKGROUND_COLOR, border_width=2,
                                border_color="white", corner_radius=0)
            room.place(x=grid_x * GRID_SIZE + grid_canvas.winfo_x(),
                    y=grid_y * GRID_SIZE + grid_canvas.winfo_y())
            cell = grid_state[grid_y][grid_x] or {'name': initial_name}
            all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items'])
            text_color = FILLED_COLOR if all_filled else "white"
            lbl = ctk.CTkLabel(room, text=cell.get('name', initial_name), fg_color="transparent",
                            font=(custom_font_family, 10), wraplength=GRID_SIZE-5, text_color=text_color)
            lbl.pack(fill="both", expand=True)
            grid_state[grid_y][grid_x] = cell
            cell['frame'] = room
            cell['label'] = lbl
            try:
                lbl.bind("<Button-1>", lambda e, x=grid_x, y=grid_y: display_room_details_tutorial(x, y))
            except Exception:
                pass
            # MODIFIED: No remove button on the room itself; handled by Remove Mode
            if not is_immovable:
                room.bind("<Enter>", lambda e: show_adjacent_placeholders_tutorial())

        def place_room_tutorial(grid_x, grid_y):
            add_room_tutorial(grid_x, grid_y, initial_name=f"Room {grid_x}-{grid_y}")
            show_adjacent_placeholders_tutorial()

        def show_adjacent_placeholders_tutorial():
            nonlocal grid_state
            nonlocal plus_buttons
            # Clear old buttons
            for b in list(plus_buttons.values()):
                try:
                    b.destroy()
                except Exception:
                    pass
            plus_buttons.clear()
            
            # MODIFIED: Check mode and show appropriate buttons
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for y in range(GRID_DIM_Y):
                for x in range(GRID_DIM_X):
                    if grid_state[y][x] is not None:
                        if not is_add_mode[0]:  # Remove Mode
                            # Show red "−" buttons on removable exterior rooms
                            if can_remove_tutorial(x, y):
                                for dx, dy in directions:
                                    nx, ny = x + dx, y + dy
                                    if 0 <= nx < GRID_DIM_X and 0 <= ny < GRID_DIM_Y and grid_state[ny][nx] is None:
                                        key = (nx, ny)
                                        if key not in plus_buttons:
                                            btn = ctk.CTkButton(grid_container, text="−", width=GRID_SIZE, height=GRID_SIZE,
                                                                corner_radius=0, fg_color="#661111", hover_color="#881111",
                                                                border_width=2, border_color="white",
                                                                command=lambda gx=x, gy=y: remove_room_tutorial(gx, gy))
                                            btn.place(x=nx * GRID_SIZE + grid_canvas.winfo_x(),
                                                    y=ny * GRID_SIZE + grid_canvas.winfo_y())
                                            plus_buttons[key] = btn
                        else:  # Add Mode
                            # Show green "+" buttons around existing rooms
                            for dx, dy in directions:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < GRID_DIM_X and 0 <= ny < GRID_DIM_Y and grid_state[ny][nx] is None:
                                    key = (nx, ny)
                                    if key not in plus_buttons:
                                        btn = ctk.CTkButton(grid_container, text="+", width=GRID_SIZE, height=GRID_SIZE,
                                                            corner_radius=0, fg_color=BACKGROUND_COLOR, hover_color="#555555",
                                                            border_width=2, border_color="white",
                                                            command=lambda gx=nx, gy=ny: place_room_tutorial(gx, gy))
                                        btn.place(x=nx * GRID_SIZE + grid_canvas.winfo_x(),
                                                y=ny * GRID_SIZE + grid_canvas.winfo_y())
                                        plus_buttons[key] = btn

        def redraw_grid_tutorial():
            nonlocal grid_state
            for w in grid_container.winfo_children():
                if w != grid_canvas:
                    try:
                        w.destroy()
                    except Exception:
                        pass
            if not grid_state:
                return
            for y in range(GRID_DIM_Y):
                for x in range(GRID_DIM_X):
                    cell = grid_state[y][x]
                    if cell is not None:
                        add_room_tutorial(x, y, is_immovable=True, initial_name=cell.get('name', 'Room'))
            show_adjacent_placeholders_tutorial()

        def setup_grid_tutorial(event=None):
            nonlocal grid_canvas
            grid_canvas.delete("all")
            grid_width = GRID_DIM_X * GRID_SIZE
            grid_height = GRID_DIM_Y * GRID_SIZE
            grid_canvas.place(x=0, y=0, width=grid_width, height=grid_height)
            show_adjacent_placeholders_tutorial()

        # NEW: Toggle button for Add/Remove Mode
        def toggle_mode_tutorial():
            is_add_mode[0] = not is_add_mode[0]
            toggle_button.configure(text="Remove Mode" if is_add_mode[0] else "Add Mode",
                                fg_color="#444444" if is_add_mode[0] else "#661111",
                                hover_color="#666666" if is_add_mode[0] else "#881111")
            show_adjacent_placeholders_tutorial()

        # UI layout
        main_frame = ctk.CTkFrame(parent_tab, fg_color="#2b2b2b")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(20, 60))
        
        # NEW: Add toggle button above grid
        toggle_button = ctk.CTkButton(main_frame, text="Remove Mode", font=(custom_font_family, 14),
                                    fg_color="#444444", hover_color="#666666",
                                    command=toggle_mode_tutorial)
        toggle_button.pack(anchor="ne", padx=10, pady=(0, 5))
        
        info_display_frame = ctk.CTkFrame(main_frame, fg_color="transparent", width=300)
        info_display_frame.pack(side="right", fill="y", padx=(10, 0), pady=10)
        
        grid_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        grid_container.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        
        grid_canvas = ctk.CTkCanvas(grid_container, bg=BACKGROUND_COLOR, highlightthickness=0)
        grid_canvas.pack(fill="both", expand=True)
        grid_container.bind("<Configure>", setup_grid_tutorial)

        # Initialize
        setup_grid_tutorial()

        def save_tutorial():
            nonlocal current_room
            nonlocal info_display_frame
            nonlocal grid_state
            if current_room[0] is not None:
                x, y = current_room
                frame = info_display_frame.winfo_children()[0] if info_display_frame.winfo_children() else None
                if frame:
                    children = frame.winfo_children()
                    if len(children) >= 7:
                        name_entry = children[2]
                        desc_text = children[4]
                        items_entry = children[6]
                        cell = grid_state[y][x]
                        if cell:
                            cell['name'] = name_entry.get().strip()
                            cell['desc'] = desc_text.get("1.0", "end").strip()
                            cell['findable_items'] = items_entry.get().strip()

            script_dir = os.path.dirname(os.path.abspath(__file__))
            root_folder = os.path.join(script_dir, "../Working_game")
            tutorial_dir = os.path.join(root_folder, "Text/Room_descriptions/Tutorial")
            if os.path.exists(tutorial_dir):
                shutil.rmtree(tutorial_dir)
            os.makedirs(tutorial_dir)

            for y in range(GRID_DIM_Y):
                for x in range(GRID_DIM_X):
                    cell = grid_state[y][x]
                    if cell is not None:
                        room_dir = os.path.join(tutorial_dir, f"y{y+1}_x{x+1}")
                        os.makedirs(room_dir)
                        name = cell.get('name', '')
                        desc = cell.get('desc', '')
                        with open(os.path.join(room_dir, "Description.txt"), "w", encoding="utf-8") as f:
                            f.write(f"{name}\n-----\n{desc}")
                        items_str = cell.get('findable_items', '')
                        if items_str:
                            items = [item.strip() for item in items_str.split(',')]
                            with open(os.path.join(room_dir, "Items.txt"), "w", encoding="utf-8") as f:
                                f.write("\n".join(items))
                        exits = []
                        directions = {
                            "north": (x, y-1),
                            "south": (x, y+1),
                            "east": (x+1, y),
                            "west": (x-1, y),
                        }
                        for dir_name, (nx, ny) in directions.items():
                            if 0 <= nx < GRID_DIM_X and 0 <= ny < GRID_DIM_Y and grid_state[ny][nx] is not None:
                                exits.append(dir_name)
                        if exits:
                            with open(os.path.join(room_dir, "Exits.txt"), "w", encoding="utf-8") as f:
                                f.write("\n".join(exits))

            load_tutorial_data()
            if current_room[0] is not None:
                display_room_details_tutorial(current_room[0], current_room[1])
            CTkMessagebox(title="Success", message="Tutorial floors saved!", icon="check")

        def load_tutorial_data():
            nonlocal grid_state
            script_dir = os.path.dirname(os.path.abspath(__file__))
            tutorial_dir = os.path.join(script_dir, "../Working_game/Text/Room_descriptions/Tutorial")
            grid_state = [[None for _ in range(GRID_DIM_X)] for _ in range(GRID_DIM_Y)]
            if os.path.exists(tutorial_dir):
                for room_folder in os.listdir(tutorial_dir):
                    room_path = os.path.join(tutorial_dir, room_folder)
                    if os.path.isdir(room_path) and '_' in room_folder:
                        try:
                            y_str, x_str = room_folder.split('_')
                            y = int(y_str[1:]) - 1
                            x = int(x_str[1:]) - 1
                            if 0 <= y < GRID_DIM_Y and 0 <= x < GRID_DIM_X:
                                cell = {}
                                desc_path = os.path.join(room_path, "Description.txt")
                                if os.path.exists(desc_path):
                                    with open(desc_path, 'r', encoding='utf-8') as f:
                                        content = f.read().split('-----')
                                        if len(content) >= 2:
                                            cell['name'] = content[0].strip()
                                            cell['desc'] = '-----'.join(content[1:]).strip()
                                        else:
                                            cell['name'] = content[0].strip()
                                            cell['desc'] = ''
                                items_path = os.path.join(room_path, "Items.txt")
                                if os.path.exists(items_path):
                                    with open(items_path, 'r', encoding='utf-8') as f:
                                        items = f.read().splitlines()
                                        cell['findable_items'] = ','.join(items)
                                grid_state[y][x] = cell
                        except ValueError:
                            pass
            redraw_grid_tutorial()

        load_tutorial_data()
        return save_tutorial, load_tutorial_data

    def setup_main_level_tab(parent_tab, custom_font_family="Arial"):
        GRID_SIZE = 40
        GRID_DIM_X, GRID_DIM_Y = 33, 20
        BACKGROUND_COLOR = "#333333"
        BORDER_WIDTH = 2
        BORDER_COLOR = "white"

        floors = {}
        current_floor = [0]
        info_display_frame = None
        current_room = [None, None]
        FILLED_COLOR = "green"
        directions_3d = [(0,0,1),(0,0,-1),(0,1,0),(0,-1,0),(1,0,0),(-1,0,0)]

        # NEW: Track the current mode (True for Add Mode, False for Remove Mode)
        is_add_mode = [True]

        def can_remove_main(rfloor, rx, ry):
            if rfloor == 0 and rx == 0 and ry == 0:
                return False
            total = sum(sum(1 for row in floors[f]["grid_state"] for c in row if c is not None) for f in floors)
            if total <= 1:
                return False
            temp = floors[rfloor]["grid_state"][ry][rx]
            floors[rfloor]["grid_state"][ry][rx] = None
            visited = set()
            q = deque([(0,0,0)])
            visited.add((0,0,0))
            while q:
                f, y, x = q.popleft()
                for df, dy, dx in directions_3d:
                    nf, ny, nx = f + df, y + dy, x + dx
                    if nf in floors and 0 <= ny < GRID_DIM_Y and 0 <= nx < GRID_DIM_X and floors[nf]["grid_state"][ny][nx] is not None and (nf, ny, nx) not in visited:
                        visited.add((nf, ny, nx))
                        q.append((nf, ny, nx))
            connected = len(visited)
            floors[rfloor]["grid_state"][ry][rx] = temp
            return connected == total - 1

        def remove_room_main(grid_x, grid_y):
            if not can_remove_main(current_floor[0], grid_x, grid_y):
                return
            floor = floors[current_floor[0]]
            floor["grid_state"][grid_y][grid_x]['frame'].destroy()
            floor["grid_state"][grid_y][grid_x] = None
            show_adjacent_placeholders()

        def clear_info_display_frame_main():
            nonlocal info_display_frame
            if info_display_frame is None:
                return
            for w in info_display_frame.winfo_children():
                try:
                    w.destroy()
                except Exception:
                    pass

        def update_room_name_main(entry_widget, grid_x, grid_y):
            new_name = entry_widget.get()
            floor = floors.get(current_floor[0])
            if not floor:
                return
            grid_state = floor["grid_state"]
            cell = grid_state[grid_y][grid_x]
            if cell is None:
                return
            cell['name'] = new_name
            if 'label' in cell and cell['label']:
                try:
                    cell['label'].configure(text=new_name)
                    all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items', 'usable_item', 'item_used_text', 'item_found', 'damage_text'])
                    cell['label'].configure(text_color=FILLED_COLOR if all_filled else "white")
                except Exception:
                    pass

        def display_room_details_main(grid_x, grid_y):
            nonlocal info_display_frame
            if info_display_frame is None:
                return
            clear_info_display_frame_main()
            nonlocal current_room
            current_room[:] = [grid_x, grid_y]
            floor = floors.get(current_floor[0])
            if not floor:
                return
            grid_state = floor["grid_state"]
            cell = grid_state[grid_y][grid_x]
            if cell is None:
                return
            current_name = cell.get('name', '')
            room_details_content_frame = ctk.CTkFrame(info_display_frame, fg_color="#333333", corner_radius=10)
            room_details_content_frame.pack(fill="both", expand=True, padx=5, pady=5)
            room_title = ctk.CTkLabel(room_details_content_frame,
                                    text=f"Details for Room ({grid_x}, {grid_y})",
                                    font=(custom_font_family, 18, "bold"),
                                    text_color="white")
            room_title.pack(pady=(10, 5))
            name_label = ctk.CTkLabel(room_details_content_frame,
                                    text="Room Name:",
                                    font=(custom_font_family, 14),
                                    text_color="white")
            name_label.pack(anchor="w", padx=15, pady=(0, 2))
            name_entry = ctk.CTkEntry(room_details_content_frame,
                                    width=250,
                                    font=(custom_font_family, 14),
                                    placeholder_text="Enter room name")
            name_entry.insert(0, current_name)
            name_entry.pack(padx=15, pady=(0, 10))
            if current_name:
                name_entry.configure(fg_color=LOADED_COLOR)
            else:
                name_entry.configure(fg_color="#444444")
            desc_label = ctk.CTkLabel(room_details_content_frame,
                                    text="Room Description:",
                                    font=(custom_font_family, 14),
                                    text_color="white")
            desc_label.pack(anchor="w", padx=15, pady=(10, 2))
            desc_text = ctk.CTkTextbox(room_details_content_frame,
                                    width=250,
                                    height=100,
                                    font=(custom_font_family, 14),
                                    fg_color="#444444")
            desc = cell.get('desc', '')
            desc_text.insert("1.0", desc)
            desc_text.pack(padx=15, pady=(0, 10))
            if desc:
                desc_text.configure(fg_color=LOADED_COLOR)
            else:
                desc_text.configure(fg_color="#444444")
            items_label = ctk.CTkLabel(room_details_content_frame,
                                    text="Findable Items (comma-separated):",
                                    font=(custom_font_family, 14),
                                    text_color="white")
            items_label.pack(anchor="w", padx=15, pady=(0, 2))
            items_entry = ctk.CTkEntry(room_details_content_frame,
                                    width=250,
                                    font=(custom_font_family, 14),
                                    placeholder_text="Enter items, separated by commas")
            findable_items = cell.get('findable_items', '')
            items_entry.insert(0, findable_items)
            items_entry.pack(padx=15, pady=(0, 10))
            if findable_items:
                items_entry.configure(fg_color=LOADED_COLOR)
            else:
                items_entry.configure(fg_color="#444444")
            usable_items_label = ctk.CTkLabel(room_details_content_frame,
                                            text="Usable Items (one per room):",
                                            font=(custom_font_family, 14),
                                            text_color="white")
            usable_items_label.pack(anchor="w", padx=15, pady=(0, 2))
            usable_items_entry = ctk.CTkEntry(room_details_content_frame,
                                            width=250,
                                            font=(custom_font_family, 14),
                                            placeholder_text="Enter item")
            usable_item = cell.get('usable_item', '')
            usable_items_entry.insert(0, usable_item)
            usable_items_entry.pack(padx=15, pady=(0, 10))
            if usable_item:
                usable_items_entry.configure(fg_color=LOADED_COLOR)
            else:
                usable_items_entry.configure(fg_color="#444444")
            item_used_text_label = ctk.CTkLabel(room_details_content_frame,
                                            text="Text When Item Used:",
                                            font=(custom_font_family, 14),
                                            text_color="white")
            item_used_text_label.pack(anchor="w", padx=15, pady=(0, 2))
            item_used_text_entry = ctk.CTkTextbox(room_details_content_frame,
                                            width=250,
                                            height=100,
                                            font=(custom_font_family, 14),
                                            fg_color="#444444")
            item_used_text = cell.get('item_used_text', '')
            item_used_text_entry.insert("1.0", item_used_text)
            item_used_text_entry.pack(padx=15, pady=(0, 10))
            if item_used_text:
                item_used_text_entry.configure(fg_color=LOADED_COLOR)
            else:
                item_used_text_entry.configure(fg_color="#444444")
            items_found_label = ctk.CTkLabel(room_details_content_frame,
                                            text="Items Found If Used (one per room):",
                                            font=(custom_font_family, 14),
                                            text_color="white")
            items_found_label.pack(anchor="w", padx=15, pady=(0, 2))
            items_found_entry = ctk.CTkEntry(room_details_content_frame,
                                            width=250,
                                            font=(custom_font_family, 14),
                                            placeholder_text="Enter item")
            item_found = cell.get('item_found', '')
            items_found_entry.insert(0, item_found)
            items_found_entry.pack(padx=15, pady=(0, 10))
            if item_found:
                items_found_entry.configure(fg_color=LOADED_COLOR)
            else:
                items_found_entry.configure(fg_color="#444444")
            damage_text_label = ctk.CTkLabel(room_details_content_frame,
                                            text="Damage Text:",
                                            font=(custom_font_family, 14),
                                            text_color="white")
            damage_text_label.pack(anchor="w", padx=15, pady=(0, 2))
            damage_text_entry = ctk.CTkTextbox(room_details_content_frame,
                                            width=250,
                                            height=100,
                                            font=(custom_font_family, 14),
                                            fg_color="#444444")
            damage_text = cell.get('damage_text', '')
            damage_text_entry.insert("1.0", damage_text)
            damage_text_entry.pack(padx=15, pady=(0, 10))
            if damage_text:
                damage_text_entry.configure(fg_color=LOADED_COLOR)
            else:
                damage_text_entry.configure(fg_color="#444444")
            name_entry.bind("<Return>", lambda event: update_room_name_main(name_entry, grid_x, grid_y))
            name_entry.bind("<FocusOut>", lambda event: update_room_name_main(name_entry, grid_x, grid_y))

            def update_desc(event=None):
                cell['desc'] = desc_text.get("1.0", "end").strip()
                all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items', 'usable_item', 'item_used_text', 'item_found', 'damage_text'])
                cell['label'].configure(text_color=FILLED_COLOR if all_filled else "white")

            def update_items(event=None):
                cell['findable_items'] = items_entry.get().strip()
                all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items', 'usable_item', 'item_used_text', 'item_found', 'damage_text'])
                cell['label'].configure(text_color=FILLED_COLOR if all_filled else "white")

            def update_usable(event=None):
                cell['usable_item'] = usable_items_entry.get().strip()
                all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items', 'usable_item', 'item_used_text', 'item_found', 'damage_text'])
                cell['label'].configure(text_color=FILLED_COLOR if all_filled else "white")

            def update_used_text(event=None):
                cell['item_used_text'] = item_used_text_entry.get("1.0", "end").strip()
                all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items', 'usable_item', 'item_used_text', 'item_found', 'damage_text'])
                cell['label'].configure(text_color=FILLED_COLOR if all_filled else "white")

            def update_found(event=None):
                cell['item_found'] = items_found_entry.get().strip()
                all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items', 'usable_item', 'item_used_text', 'item_found', 'damage_text'])
                cell['label'].configure(text_color=FILLED_COLOR if all_filled else "white")

            def update_damage(event=None):
                cell['damage_text'] = damage_text_entry.get("1.0", "end").strip()
                all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items', 'usable_item', 'item_used_text', 'item_found', 'damage_text'])
                cell['label'].configure(text_color=FILLED_COLOR if all_filled else "white")

            desc_text.bind("<FocusOut>", update_desc)
            items_entry.bind("<FocusOut>", update_items)
            usable_items_entry.bind("<FocusOut>", update_usable)
            item_used_text_entry.bind("<FocusOut>", update_used_text)
            items_found_entry.bind("<FocusOut>", update_found)
            damage_text_entry.bind("<FocusOut>", update_damage)
            placeholder_text = ctk.CTkLabel(room_details_content_frame,
                                            text="This is where specific data for this room will go.",
                                            font=(custom_font_family, 14),
                                            text_color="#AAAAAA",
                                            wraplength=info_display_frame.winfo_width() - 30)
            placeholder_text.pack(pady=(5, 10), padx=10)

        def refresh_floor_list():
            for widget in floor_list_frame.winfo_children():
                widget.destroy()
            header = ctk.CTkLabel(floor_list_frame, text="Floors", font=(custom_font_family,16,"bold"))
            header.pack(pady=(10,5))
            for i in range(len(floors)):
                floor_frame = ctk.CTkFrame(floor_list_frame, fg_color="transparent")
                floor_frame.pack(fill="x", pady=2, padx=5)
                floor_btn = ctk.CTkButton(floor_frame, 
                                        text=f"Floor {i}",
                                        command=lambda idx=i: switch_floor(idx),
                                        fg_color="#2638DB" if i == current_floor[0] else "#333333",
                                        hover_color="#321FDD" if i == current_floor[0] else "#444444",
                                        text_color="white")
                floor_btn.pack(side="left", expand=True, fill="x", padx=(5,5))
                if len(floors) > 1:
                    tooltip_text = "Warning: Removing this floor will also remove all floors above it!" if i < len(floors) - 1 else None
                    try:
                        remove_btn = ctk.CTkButton(floor_frame,
                                                text="×",
                                                width=30,
                                                command=lambda idx=i: remove_floor(idx),
                                                fg_color="#661111",
                                                hover_color="#881111")
                        remove_btn.pack(side="right", padx=5)
                        if tooltip_text:
                            ToolTip(remove_btn, tooltip_text)
                    except NameError:
                        remove_btn = ctk.CTkButton(floor_frame,
                                                text="×",
                                                width=30,
                                                command=lambda idx=i: remove_floor(idx),
                                                fg_color="#661111",
                                                hover_color="#881111")
                        remove_btn.pack(side="right", padx=5)
            add_btn = ctk.CTkButton(floor_list_frame, text="+ Add Floor", command=add_new_floor,
                                    fg_color="#444444", hover_color="#666666")
            add_btn.pack(pady=10)

        def switch_floor(floor_index):
            current_floor[0] = floor_index
            if floor_index not in floors:
                floors[floor_index] = {
                    "grid_state": [[None for _ in range(GRID_DIM_X)] for _ in range(GRID_DIM_Y)],
                    "plus_buttons": {},
                }
            refresh_floor_list()
            redraw_floor()

        drag_data = {"start_y": 0, "source_idx": None}

        def start_drag(event, floor_idx):
            drag_data["start_y"] = event.y_root
            drag_data["source_idx"] = floor_idx
            
        def handle_drag(event, floor_idx):
            if drag_data["source_idx"] is None:
                return
            for widget in floor_list_frame.winfo_children()[:-1]:
                if isinstance(widget, ctk.CTkFrame):
                    widget_y = widget.winfo_rooty()
                    widget_height = widget.winfo_height()
                    if widget_y <= event.y_root <= widget_y + widget_height:
                        try:
                            target_idx = floor_list_frame.winfo_children().index(widget) - 1
                        except ValueError:
                            continue
                        if target_idx != drag_data["source_idx"] and target_idx >= 0:
                            reorder_floors(drag_data["source_idx"], target_idx)
                            drag_data["source_idx"] = target_idx
                            break

        def end_drag(event, floor_idx):
            drag_data["source_idx"] = None

        def reorder_floors(old_idx, new_idx):
            if old_idx == new_idx:
                return
            floors_list = [(i, data) for i, data in sorted(floors.items())]
            floor_to_move = floors_list.pop(old_idx)
            floors_list.insert(new_idx, floor_to_move)
            floors.clear()
            for new_idx_key, (_, data) in enumerate(floors_list):
                floors[new_idx_key] = data
            if current_floor[0] == old_idx:
                current_floor[0] = new_idx
            elif old_idx < new_idx:
                if current_floor[0] > old_idx and current_floor[0] <= new_idx:
                    current_floor[0] -= 1
            else:
                if current_floor[0] >= new_idx and current_floor[0] < old_idx:
                    current_floor[0] += 1
            refresh_floor_list()

        def remove_floor(floor_idx):
            if len(floors) <= 1:
                return
            floors_to_keep = {}
            for idx, data in sorted(floors.items()):
                if idx < floor_idx:
                    floors_to_keep[idx] = data
            floors.clear()
            floors.update(floors_to_keep)
            new_floors = {}
            for new_idx, (_, data) in enumerate(sorted(floors.items())):
                new_floors[new_idx] = data
            floors.clear()
            floors.update(new_floors)
            if current_floor[0] >= floor_idx:
                current_floor[0] = max(0, len(floors) - 1)
            refresh_floor_list()
            redraw_floor()

        def add_new_floor():
            new_index = len(floors)
            floors[new_index] = {
                "grid_state": [[None for _ in range(GRID_DIM_X)] for _ in range(GRID_DIM_Y)],
                "plus_buttons": {},
            }
            refresh_floor_list()
            switch_floor(new_index)

        def add_room_to_floor(grid_x, grid_y, is_immovable=False, initial_name="Room"):
            floor = floors[current_floor[0]]
            grid_state = floor["grid_state"]
            room = ctk.CTkFrame(grid_container, width=GRID_SIZE, height=GRID_SIZE,
                                fg_color=BACKGROUND_COLOR, border_width=BORDER_WIDTH,
                                border_color=BORDER_COLOR, corner_radius=0)
            room.place(x=grid_x * GRID_SIZE + grid_canvas.winfo_x(),
                    y=grid_y * GRID_SIZE + grid_canvas.winfo_y())
            cell = grid_state[grid_y][grid_x] or {'name': initial_name}
            all_filled = all(cell.get(k, '').strip() for k in ['name', 'desc', 'findable_items', 'usable_item', 'item_used_text', 'item_found', 'damage_text'])
            text_color = FILLED_COLOR if all_filled else "white"
            lbl = ctk.CTkLabel(room, text=cell.get('name', initial_name), fg_color="transparent",
                            font=(custom_font_family, 10), wraplength=GRID_SIZE-5, text_color=text_color)
            lbl.pack(fill="both", expand=True)
            grid_state[grid_y][grid_x] = cell
            cell['frame'] = room
            cell['label'] = lbl
            try:
                lbl.bind("<Button-1>", lambda e, x=grid_x, y=grid_y: display_room_details_main(x, y))
            except Exception:
                pass
            # MODIFIED: No remove button on the room itself; handled by Remove Mode
            if not is_immovable:
                room.bind("<Enter>", lambda e: show_adjacent_placeholders())

        def place_room_on_floor(grid_x, grid_y):
            add_room_to_floor(grid_x, grid_y, initial_name=f"Room {grid_x}-{grid_y}")
            show_adjacent_placeholders()

        def show_adjacent_placeholders():
            floor = floors[current_floor[0]]
            grid_state = floor["grid_state"]
            plus_buttons = floor["plus_buttons"]
            for b in list(plus_buttons.values()):
                try:
                    b.destroy()
                except Exception:
                    pass
            plus_buttons.clear()
            
            # MODIFIED: Check mode and show appropriate buttons
            if is_add_mode[0]:  # Add Mode
                # Add based on floor below
                floor_below_idx = current_floor[0] - 1
                if floor_below_idx in floors:
                    floor_below = floors[floor_below_idx]["grid_state"]
                    for y in range(GRID_DIM_Y):
                        for x in range(GRID_DIM_X):
                            if floor_below[y][x] is not None:
                                if grid_state[y][x] is None:
                                    btn = ctk.CTkButton(grid_container, text="+", width=20, height=20,
                                                        corner_radius=0, fg_color=BACKGROUND_COLOR, hover_color="#666666",
                                                        border_width=BORDER_WIDTH, border_color=BORDER_COLOR,
                                                        command=lambda gx=x, gy=y: place_room_on_floor(gx, gy))
                                    btn.place(x=x * GRID_SIZE + grid_canvas.winfo_x() + GRID_SIZE//2 - 10,
                                            y=y * GRID_SIZE + grid_canvas.winfo_y() + GRID_SIZE//2 - 10)
                                    plus_buttons[f"below_{x}_{y}"] = btn
                # Add based on floor above
                floor_above_idx = current_floor[0] + 1
                if floor_above_idx in floors:
                    floor_above = floors[floor_above_idx]["grid_state"]
                    for y in range(GRID_DIM_Y):
                        for x in range(GRID_DIM_X):
                            if floor_above[y][x] is not None:
                                if grid_state[y][x] is None:
                                    btn = ctk.CTkButton(grid_container, text="+", width=20, height=20,
                                                        corner_radius=0, fg_color=BACKGROUND_COLOR, hover_color="#666666",
                                                        border_width=BORDER_WIDTH, border_color=BORDER_COLOR,
                                                        command=lambda gx=x, gy=y: place_room_on_floor(gx, gy))
                                    btn.place(x=x * GRID_SIZE + grid_canvas.winfo_x() + GRID_SIZE//2 - 10,
                                            y=y * GRID_SIZE + grid_canvas.winfo_y() + GRID_SIZE//2 - 10)
                                    plus_buttons[f"above_{x}_{y}"] = btn
                # Add plus buttons around existing rooms on current floor
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                for y in range(GRID_DIM_Y):
                    for x in range(GRID_DIM_X):
                        if grid_state[y][x] is not None:
                            for dx, dy in directions:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < GRID_DIM_X and 0 <= ny < GRID_DIM_Y and grid_state[ny][nx] is None:
                                    key = (nx, ny)
                                    if key not in plus_buttons:
                                        btn = ctk.CTkButton(grid_container, text="+", width=GRID_SIZE, height=GRID_SIZE,
                                                            corner_radius=0, fg_color=BACKGROUND_COLOR, hover_color="#555555",
                                                            border_width=BORDER_WIDTH, border_color=BORDER_COLOR,
                                                            command=lambda gx=nx, gy=ny: place_room_on_floor(gx, gy))
                                        btn.place(x=nx * GRID_SIZE + grid_canvas.winfo_x(),
                                                y=ny * GRID_SIZE + grid_canvas.winfo_y())
                                        plus_buttons[key] = btn
            else:  # Remove Mode
                # Show red "−" buttons for removable rooms
                floor_below_idx = current_floor[0] - 1
                floor_above_idx = current_floor[0] + 1
                for y in range(GRID_DIM_Y):
                    for x in range(GRID_DIM_X):
                        if grid_state[y][x] is not None and can_remove_main(current_floor[0], x, y):
                            # Horizontal connections
                            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                            for dx, dy in directions:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < GRID_DIM_X and 0 <= ny < GRID_DIM_Y and grid_state[ny][nx] is None:
                                    key = (nx, ny)
                                    if key not in plus_buttons:
                                        btn = ctk.CTkButton(grid_container, text="−", width=GRID_SIZE, height=GRID_SIZE,
                                                            corner_radius=0, fg_color="#661111", hover_color="#881111",
                                                            border_width=BORDER_WIDTH, border_color=BORDER_COLOR,
                                                            command=lambda gx=x, gy=y: remove_room_main(gx, gy))
                                        btn.place(x=nx * GRID_SIZE + grid_canvas.winfo_x(),
                                                y=ny * GRID_SIZE + grid_canvas.winfo_y())
                                        plus_buttons[key] = btn
                            # Vertical connections (below)
                            if floor_below_idx in floors:
                                floor_below = floors[floor_below_idx]["grid_state"]
                                if floor_below[y][x] is not None and grid_state[y][x] is not None:
                                    key = f"below_{x}_{y}"
                                    if key not in plus_buttons:
                                        btn = ctk.CTkButton(grid_container, text="−", width=20, height=20,
                                                            corner_radius=0, fg_color="#661111", hover_color="#881111",
                                                            border_width=BORDER_WIDTH, border_color=BORDER_COLOR,
                                                            command=lambda gx=x, gy=y: remove_room_main(gx, gy))
                                        btn.place(x=x * GRID_SIZE + grid_canvas.winfo_x() + GRID_SIZE//2 - 10,
                                                y=y * GRID_SIZE + grid_canvas.winfo_y() + GRID_SIZE//2 - 10)
                                        plus_buttons[key] = btn
                            # Vertical connections (above)
                            if floor_above_idx in floors:
                                floor_above = floors[floor_above_idx]["grid_state"]
                                if floor_above[y][x] is not None and grid_state[y][x] is not None:
                                    key = f"above_{x}_{y}"
                                    if key not in plus_buttons:
                                        btn = ctk.CTkButton(grid_container, text="−", width=20, height=20,
                                                            corner_radius=0, fg_color="#661111", hover_color="#881111",
                                                            border_width=BORDER_WIDTH, border_color=BORDER_COLOR,
                                                            command=lambda gx=x, gy=y: remove_room_main(gx, gy))
                                        btn.place(x=x * GRID_SIZE + grid_canvas.winfo_x() + GRID_SIZE//2 - 10,
                                                y=y * GRID_SIZE + grid_canvas.winfo_y() + GRID_SIZE//2 - 10)
                                        plus_buttons[key] = btn

        def redraw_floor():
            for w in grid_container.winfo_children():
                if w != grid_canvas:
                    try:
                        w.destroy()
                    except Exception:
                        pass
            floor = floors.get(current_floor[0], None)
            if not floor:
                return
            grid_state = floor["grid_state"]
            for y in range(GRID_DIM_Y):
                for x in range(GRID_DIM_X):
                    cell = grid_state[y][x]
                    if cell is not None:
                        add_room_to_floor(x, y, is_immovable=True, initial_name=cell.get('name', 'Room'))
            show_adjacent_placeholders()

        def setup_grid_main(event=None):
            grid_canvas.delete("all")
            grid_width = GRID_DIM_X * GRID_SIZE
            grid_height = GRID_DIM_Y * GRID_SIZE
            grid_canvas.place(x=0, y=0, width=grid_width, height=grid_height)
            if not floors:
                floors[0] = {"grid_state": [[None for _ in range(GRID_DIM_X)] for _ in range(GRID_DIM_Y)],
                            "plus_buttons": {}}
            if 0 in floors:
                original_floor = current_floor[0]
                current_floor[0] = 0
                if floors[0]["grid_state"][0][0] is None:
                    add_room_to_floor(0, 0, is_immovable=True, initial_name="Start Room")
                current_floor[0] = original_floor
            for idx in list(floors.keys()):
                if len(floors[idx]["grid_state"]) != GRID_DIM_Y or len(floors[idx]["grid_state"][0]) != GRID_DIM_X:
                    floors[idx]["grid_state"] = [[None for _ in range(GRID_DIM_X)] for _ in range(GRID_DIM_Y)]
                    floors[idx]["plus_buttons"] = {}
                    if idx == 0 and floors[0]["grid_state"][0][0] is None:
                        add_room_to_floor(0, 0, is_immovable=True, initial_name="Start Room")
            redraw_floor()
            refresh_floor_list()

        # NEW: Toggle button for Add/Remove Mode
        def toggle_mode_main():
            is_add_mode[0] = not is_add_mode[0]
            toggle_button.configure(text="Remove Mode" if is_add_mode[0] else "Add Mode",
                                fg_color="#444444" if is_add_mode[0] else "#661111",
                                hover_color="#666666" if is_add_mode[0] else "#881111")
            show_adjacent_placeholders()

        # UI layout
        main_frame = ctk.CTkFrame(parent_tab, fg_color="#2b2b2b")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(20, 60))
        # NEW: Add toggle button above grid
        toggle_button = ctk.CTkButton(main_frame, text="Remove Mode", font=(custom_font_family, 14),
                                    fg_color="#444444", hover_color="#666666",
                                    command=toggle_mode_main)
        toggle_button.pack(anchor="ne", padx=10, pady=(0, 5))
        floor_list_frame = ctk.CTkFrame(main_frame, fg_color="#1e1e1e", width=120)
        floor_list_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)
        info_display_frame = ctk.CTkFrame(main_frame, fg_color="transparent", width=300)
        info_display_frame.pack(side="right", fill="y", padx=(10, 0), pady=10)
        grid_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        grid_container.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        grid_canvas = ctk.CTkCanvas(grid_container, bg=BACKGROUND_COLOR, highlightthickness=0)
        grid_canvas.pack(fill="both", expand=True)
        grid_container.bind("<Configure>", setup_grid_main)

        # Initialize
        setup_grid_main()

        def save_main_level():
            nonlocal current_room
            nonlocal info_display_frame
            if current_room[0] is not None:
                floor = floors[current_floor[0]]
                grid_state = floor["grid_state"]
                x, y = current_room
                frame = info_display_frame.winfo_children()[0] if info_display_frame.winfo_children() else None
                if frame:
                    children = frame.winfo_children()
                    if len(children) >= 15:
                        name_entry = children[2]
                        desc_text = children[4]
                        items_entry = children[6]
                        usable_items_entry = children[8]
                        item_used_text_entry = children[10]
                        items_found_entry = children[12]
                        damage_text_entry = children[14]
                        cell = grid_state[y][x]
                        if cell:
                            cell['name'] = name_entry.get().strip()
                            cell['desc'] = desc_text.get("1.0", "end").strip()
                            cell['findable_items'] = items_entry.get().strip()
                            cell['usable_item'] = usable_items_entry.get().strip()
                            cell['item_used_text'] = item_used_text_entry.get("1.0", "end").strip()
                            cell['item_found'] = items_found_entry.get().strip()
                            cell['damage_text'] = damage_text_entry.get("1.0", "end").strip()

            script_dir = os.path.dirname(os.path.abspath(__file__))
            root_folder = os.path.join(script_dir, "../Working_game")
            main_dir = os.path.join(root_folder, "Text/Room_descriptions/Main")
            if os.path.exists(main_dir):
                shutil.rmtree(main_dir)
            os.makedirs(main_dir)

            for floor_idx in sorted(floors.keys()):
                floor_num = floor_idx + 1
                floor_dir = os.path.join(main_dir, f"Floor_{floor_num}")
                os.makedirs(floor_dir)
                grid_state = floors[floor_idx]["grid_state"]

                for y in range(GRID_DIM_Y):
                    for x in range(GRID_DIM_X):
                        cell = grid_state[y][x]
                        if cell is not None:
                            room_dir = os.path.join(floor_dir, f"y{y+1}_x{x+1}")
                            os.makedirs(room_dir)
                            name = cell.get('name', '')
                            desc = cell.get('desc', '')
                            with open(os.path.join(room_dir, "Description.txt"), "w", encoding="utf-8") as f:
                                f.write(f"{name}\n-----\n{desc}")
                            items_str = cell.get('findable_items', '')
                            if items_str:
                                items = [item.strip() for item in items_str.split(',')]
                                with open(os.path.join(room_dir, "Items.txt"), "w", encoding="utf-8") as f:
                                    f.write("\n".join(items))
                            damage_text = cell.get('damage_text', '')
                            if damage_text:
                                with open(os.path.join(room_dir, "Strange_occerance.txt"), "w", encoding="utf-8") as f:
                                    f.write(damage_text)
                            usable_item = cell.get('usable_item', '')
                            item_used_text = cell.get('item_used_text', '')
                            item_found = cell.get('item_found', '')
                            if usable_item or item_used_text or item_found:
                                with open(os.path.join(room_dir, "Usable_Items.txt"), "w", encoding="utf-8") as f:
                                    f.write(f"{usable_item}\n{item_used_text}\n{item_found}")
                            exits = []
                            directions = {
                                "north": (x, y-1, floor_idx),
                                "south": (x, y+1, floor_idx),
                                "east": (x+1, y, floor_idx),
                                "west": (x-1, y, floor_idx),
                                "up": (x, y, floor_idx + 1),
                                "down": (x, y, floor_idx - 1),
                            }
                            for dir_name, (nx, ny, nf) in directions.items():
                                if nf in floors:
                                    gs = floors[nf]["grid_state"]
                                    if 0 <= nx < GRID_DIM_X and 0 <= ny < GRID_DIM_Y and gs[ny][nx] is not None:
                                        exits.append(dir_name)
                            if exits:
                                with open(os.path.join(room_dir, "Exits.txt"), "w", encoding="utf-8") as f:
                                    f.write("\n".join(exits))

            load_main_level_data()
            if current_room[0] is not None:
                display_room_details_main(current_room[0], current_room[1])
            CTkMessagebox(title="Success", message="Main levels saved!", icon="check")

        def load_main_level_data():
            script_dir = os.path.dirname(os.path.abspath(__file__))
            main_dir = os.path.join(script_dir, "../Working_game/Text/Room_descriptions/Main")
            floors.clear()
            if os.path.exists(main_dir):
                floor_folders = sorted(os.listdir(main_dir))
                for floor_folder in floor_folders:
                    if floor_folder.startswith("Floor_"):
                        try:
                            floor_idx = int(floor_folder.split('_')[1]) - 1
                            floor_path = os.path.join(main_dir, floor_folder)
                            grid_state = [[None for _ in range(GRID_DIM_X)] for _ in range(GRID_DIM_Y)]
                            for room_folder in os.listdir(floor_path):
                                room_path = os.path.join(floor_path, room_folder)
                                if os.path.isdir(room_path) and '_' in room_folder:
                                    try:
                                        y_str, x_str = room_folder.split('_')
                                        y = int(y_str[1:]) - 1
                                        x = int(x_str[1:]) - 1
                                        if 0 <= y < GRID_DIM_Y and 0 <= x < GRID_DIM_X:
                                            cell = {}
                                            desc_path = os.path.join(room_path, "Description.txt")
                                            if os.path.exists(desc_path):
                                                with open(desc_path, 'r', encoding='utf-8') as f:
                                                    content = f.read().split('-----')
                                                    if len(content) >= 2:
                                                        cell['name'] = content[0].strip()
                                                        cell['desc'] = '-----'.join(content[1:]).strip()
                                                    else:
                                                        cell['name'] = content[0].strip()
                                                        cell['desc'] = ''
                                            items_path = os.path.join(room_path, "Items.txt")
                                            if os.path.exists(items_path):
                                                with open(items_path, 'r', encoding='utf-8') as f:
                                                    items = f.read().splitlines()
                                                    cell['findable_items'] = ','.join(items)
                                            damage_path = os.path.join(room_path, "Strange_occerance.txt")
                                            if os.path.exists(damage_path):
                                                with open(damage_path, 'r', encoding='utf-8') as f:
                                                    cell['damage_text'] = f.read().strip()
                                            usable_path = os.path.join(room_path, "Usable_Items.txt")
                                            if os.path.exists(usable_path):
                                                with open(usable_path, 'r', encoding='utf-8') as f:
                                                    lines = f.read().splitlines()
                                                    if len(lines) >= 3:
                                                        cell['usable_item'] = lines[0]
                                                        cell['item_used_text'] = lines[1]
                                                        cell['item_found'] = lines[2]
                                            grid_state[y][x] = cell
                                    except ValueError:
                                        pass
                            floors[floor_idx] = {"grid_state": grid_state, "plus_buttons": {}}
                        except ValueError:
                            pass
            if 0 not in floors:
                floors[0] = {"grid_state": [[None for _ in range(GRID_DIM_X)] for _ in range(GRID_DIM_Y)], "plus_buttons": {}}
                floors[0]["grid_state"][0][0] = {'name': 'Start Room', 'desc': '', 'findable_items': '', 'usable_item': '', 'item_used_text': '', 'item_found': '', 'damage_text': ''}
            refresh_floor_list()
            redraw_floor()

        load_main_level_data()
        return save_main_level

    # Initialize the Tutorial tab (single-layer grid) so it shows content
    save_tutorial, load_tutorial_data = setup_tutorial_tab(tutorial_tab, custom_font_family)

    # Initialize the Main Level tab (multi-floor editor)
    save_main_level = setup_main_level_tab(main_level_tab, custom_font_family)

    save_tutorial_button.configure(command=save_tutorial)
    save_main_level_button.configure(command=save_main_level)

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
        export_tab_button.configure(fg_color=SAVE_COLOR, hover_color=SAVE_HOVER, text_color="black")
        if current_tab == "Return to Hub":
            return_to_hub()
        elif current_tab == "Test App":
            launch_test_app()
            # revert to previous tab
            tab_view.set(previous_tab[0])
            test_tab_button.configure(fg_color=TEST_COLOR, hover_color=TEST_HOVER, text_color="black")
            about_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")
        elif current_tab == "Export":
            export_tab_button.configure(fg_color=SAVE_COLOR, hover_color=SAVE_HOVER, text_color="black")
            about_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")
        elif current_tab == "Help":
            help_path = os.path.join(resource_base_path, "Docs", "Help", "Help.pdf")
            os.startfile(help_path)
            tab_view.set(previous_tab[0])
            help_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")
            about_tab_button.configure(fg_color=ABOUT_COLOR, hover_color=ABOUT_HOVER, text_color="black")
        else:
            # store the last active tab (not Test App)
            previous_tab[0] = current_tab

    tab_view._command = on_tab_change

    # ========================= Export Tab =========================
    export_container = ctk.CTkScrollableFrame(export_tab, fg_color="#222222", corner_radius=10)
    export_container.pack(expand=True, fill="both", padx=20, pady=20)

    export_path_label = ctk.CTkLabel(export_container, text="Export Path:", font=(custom_font_family, 16))
    export_path_label.pack(pady=(10,5))

    # Frame to hold entry + button side by side
    path_frame = ctk.CTkFrame(export_container, fg_color="transparent")
    path_frame.pack(fill="x", pady=(0,10))

    export_path_entry = ctk.CTkEntry(path_frame, width=screen_w-200, font=(custom_font_family, 14))
    export_path_entry.pack(side="left", fill="x", expand=True, padx=(0,10))

    def browse_export_path():
        selected_dir = filedialog.askdirectory(title="Select Export Folder")
        if selected_dir:
            export_path_entry.delete(0, "end")
            export_path_entry.insert(0, selected_dir)

    browse_button = ctk.CTkButton(path_frame, text="📂", width=30, fg_color="#444444", hover_color="#666666", command=browse_export_path)
    browse_button.pack(side="right")

    def export_game():
        export_path = export_path_entry.get().strip()
        if not export_path:
            CTkMessagebox(title="Error", message="Please specify an export path.", icon="cancel")
            return
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            working_game_dir = os.path.join(script_dir, "../Working_game")
            if not os.path.exists(working_game_dir):
                CTkMessagebox(title="Error", message="Working_game directory not found. Please save your work first.", icon="cancel")
                return
            dest_dir = os.path.join(export_path, "Echo_Game_Export")
            if os.path.exists(dest_dir):
                progress_bar = ctk.CTkProgressBar(export_container, mode="indeterminate", width=300)
                progress_bar.pack(pady=(10,10))
                shutil.rmtree(dest_dir)
            shutil.copytree(working_game_dir, dest_dir)
            CTkMessagebox(title="Success", message=f"Game exported successfully to:\n{dest_dir}", icon="check")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to export game:\n{e}", icon="cancel")

    export_button = ctk.CTkButton(export_container, text="Export Game", font=(custom_font_family, 16),
                                  fg_color=SAVE_COLOR, hover_color=SAVE_HOVER, text_color="black", command=export_game)
    export_button.pack(pady=(20,10))

    export_instructions = (
        "To export your game, specify the folder where you want the game to be exported.\n"
        "Click the '📂' button to browse for a folder.\n"
        "Then click the 'Export Game' button to start the export process.\n"
        "Once the game has been exported, you will find it in a folder named 'Echo_Game_Export' inside the selected directory.\n"
        "To run the game, run the 'Echo_runner.exe' file located in the exported folder.\n"
        "You can then safely rename the exported folder to your desired game name, as well as create a custom shortcut to the 'Echo_runner.exe' file for easy access."
    )
    export_instructions_label = ctk.CTkLabel(export_container, text=export_instructions, font=(custom_font_family, 14),
                                             justify="left", wraplength=screen_w-100)
    export_instructions_label.pack(pady=(10,10), padx=10)

    # ========================= About Tab =========================
    about_container = ctk.CTkScrollableFrame(about_tab, fg_color="#222222", corner_radius=10)
    about_container.pack(expand=True, fill="both", padx=20, pady=20)

    nova_path = os.path.join(resource_base_path, "Icons", "Nova_foundry", "Nova_foundry_wide_transparent.png")
    echo_path = os.path.join(resource_base_path, "Icons", "Echo_engine", "Echo_engine_transparent.png")

    display_image_scaled(nova_path, about_container, scale=0.2)
    display_image_scaled(echo_path, about_container, scale=0.2)

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