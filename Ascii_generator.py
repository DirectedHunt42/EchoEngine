# Jack Murray
# Nova Foundry / ASCII Art Converter
# v1.1.0

import os
import subprocess
import threading
import webbrowser
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageEnhance
import tkinter as tk
import platform

# ---------- CONFIG ----------
DEFAULT_WIDTH = 700
DEFAULT_HEIGHT = 1000

# --- UPDATE THESE PATHS ---
DEFAULT_PREVIEW_IMAGE_PATH = os.path.join("Engine_editor", "Icons", "Echo_engine", "Echo_engine_transparent.png")
ICON_FILE_PATH = os.path.join("Engine_editor", "Icons", "App_icon", "Ascii.ico")

# Define ASCII character sets for different styles (reversed for dark-to-light mapping)
ASCII_STYLES = {
    "Standard": "@%#*+=-:. "[::-1],
    "Blocks": "█▓▒░ "[::-1],
    "Complex": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "[::-1],
    "Simple": " .:-=+*#%@",
}

os_name = platform.system().lower()
HUB_PATH = "Echo_hub.exe" if os_name == "windows" else "Echo_hub"

# ---------- Helper Functions ----------

def show_custom_message(title, message, is_error=False):
    """Displays a modal dialog box."""
    dialog = ctk.CTkToplevel(app)
    dialog.title(title)
    dialog.geometry("320x160")
    dialog.resizable(False, False)
    dialog.transient(app)
    dialog.update_idletasks()

    # Wait for dialog to be visible before grab
    dialog.wait_visibility()
    dialog.grab_set()

    # Center the dialog on the app window
    x = app.winfo_x() + (app.winfo_width() // 2) - 160
    y = app.winfo_y() + (app.winfo_height() // 2) - 80
    dialog.geometry(f"320x160+{x}+{y}")

    label = ctk.CTkLabel(dialog, text=message, wraplength=280,
                         text_color="red" if is_error else "white")
    label.pack(pady=20, padx=20)

    btn = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, width=100)
    btn.pack(pady=10)

def convert_to_ascii(image, style_chars, new_width=100, contrast_factor=1.0, invert=False):
    """Core logic to convert a PIL Image to an ASCII string."""
    try:
        width, height = image.size
        aspect_ratio = height / float(width)
        new_height = int(aspect_ratio * new_width * 0.55)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        grayscale_image = resized_image.convert("L")

        if contrast_factor != 1.0:
            enhancer = ImageEnhance.Contrast(grayscale_image)
            grayscale_image = enhancer.enhance(contrast_factor)

        if invert:
            grayscale_image = Image.eval(grayscale_image, lambda x: 255 - x)

        pixels = grayscale_image.getdata()
        num_chars = len(style_chars)
        ascii_str = "".join(style_chars[int((pixel_value / 255) * (num_chars - 1))] for pixel_value in pixels)

        ascii_lines = [ascii_str[i:i + new_width] for i in range(0, len(ascii_str), new_width)]
        return "\n".join(ascii_lines)

    except Exception as e:
        print(f"Error in conversion: {e}")
        return None

# ---------- Main Actions ----------

def select_image_file():
    file_path = filedialog.askopenfilename(
        title="Select an Image File",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    if file_path:
        file_entry.configure(state='normal')
        file_entry.delete(0, 'end')
        file_entry.insert(0, file_path)
        file_entry.configure(state='disabled')

def start_conversion():
    image_path = file_entry.get().strip()

    # Use default if no valid selection
    if not image_path or image_path in ("[Initial Default Image Loaded]", "[Using Default Image]"):
        if not DEFAULT_PREVIEW_IMAGE_PATH or not os.path.exists(DEFAULT_PREVIEW_IMAGE_PATH):
            show_custom_message("Error", "Default image not found. Please select an image.", is_error=True)
            return
        image_path = DEFAULT_PREVIEW_IMAGE_PATH
        file_entry.configure(state='normal')
        file_entry.delete(0, 'end')
        file_entry.insert(0, "[Using Default Image]")
        file_entry.configure(state='disabled')

    if not os.path.exists(image_path):
        show_custom_message("Error", "The image file does not exist.", is_error=True)
        return

    try:
        style_name = style_menu.get()
        style_chars = ASCII_STYLES[style_name]
        width = int(width_slider.get())
        contrast_factor = float(contrast_slider.get())
        invert = bool(invert_switch.get())

        select_btn.configure(state='disabled')
        convert_btn.configure(state='disabled', text="Converting...")
        save_btn.configure(state='disabled')

        threading.Thread(
            target=run_conversion_thread,
            args=(image_path, style_chars, width, contrast_factor, invert),
            daemon=True
        ).start()

    except Exception as e:
        show_custom_message("Error", f"Failed to start conversion:\n{e}", is_error=True)
        reset_buttons()

def run_conversion_thread(image_path, style_chars, width, contrast_factor, invert):
    try:
        image = Image.open(image_path)
        ascii_art = convert_to_ascii(image, style_chars, width, contrast_factor, invert)
        if ascii_art:
            app.after(0, update_ui_with_result, ascii_art)
        else:
            raise Exception("Conversion failed.")
    except Exception as e:
        app.after(0, update_ui_with_error, str(e))

def update_ui_with_result(ascii_art):
    output_textbox.configure(state='normal')
    output_textbox.delete("1.0", "end")
    output_textbox.insert("1.0", ascii_art)
    output_textbox.configure(state='disabled')
    reset_buttons()

def update_ui_with_error(error_message):
    show_custom_message("Conversion Error", f"Failed to convert image:\n{error_message}", is_error=True)
    reset_buttons()

def reset_buttons():
    select_btn.configure(state='normal')
    convert_btn.configure(state='normal', text="Convert to ASCII")
    save_btn.configure(state='normal')

def save_art():
    ascii_art = output_textbox.get("1.0", "end-1c")
    if not ascii_art.strip():
        show_custom_message("Error", "No ASCII art to save!", is_error=True)
        return

    file_path = filedialog.asksaveasfilename(
        title="Save ASCII Art",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(ascii_art)
            show_custom_message("Success", f"Art saved to:\n{file_path}")
        except Exception as e:
            show_custom_message("Error", f"Failed to save:\n{e}", is_error=True)

def return_to_hub():
    global HUB_PATH
    if not os.path.exists(HUB_PATH):
        show_custom_message("Error", f"Hub not found:\n{HUB_PATH}", is_error=True)
        return
    try:
        if os_name == "windows":
            subprocess.Popen(HUB_PATH)
        else:
            # On Linux, use shell to resolve PATH or relative scripts
            subprocess.Popen(['./' + HUB_PATH], cwd=os.path.dirname(HUB_PATH) or '.')
        app.destroy()
    except Exception as e:
        show_custom_message("Error", f"Failed to launch Hub:\n{e}", is_error=True)

# ---------- Initial Conversion ----------
def initial_conversion_if_default_exists():
    if DEFAULT_PREVIEW_IMAGE_PATH and os.path.exists(DEFAULT_PREVIEW_IMAGE_PATH):
        try:
            image = Image.open(DEFAULT_PREVIEW_IMAGE_PATH)
            ascii_art = convert_to_ascii(
                image,
                ASCII_STYLES["Standard"],
                int(width_slider.get()),
                float(contrast_slider.get()),
                bool(invert_switch.get())
            )
            if ascii_art:
                output_textbox.configure(state='normal')
                output_textbox.delete("1.0", "end")
                output_textbox.insert("1.0", ascii_art)
                output_textbox.configure(state='disabled')

                file_entry.configure(state='normal')
                file_entry.delete(0, 'end')
                file_entry.insert(0, "[Initial Default Image Loaded]")
                file_entry.configure(state='disabled')
        except Exception as e:
            print(f"Initial load failed: {e}")

# ---------- App Setup ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("ASCII Art Converter")
app.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
app.resizable(False, False)

# --- Icon (Windows only) ---
if os_name == "windows" and ICON_FILE_PATH and os.path.exists(ICON_FILE_PATH):
    try:
        app.iconbitmap(ICON_FILE_PATH)
    except Exception as e:
        print(f"Could not set icon: {e}")

# Center window
app.update_idletasks()
x = (app.winfo_screenwidth() // 2) - (app.winfo_width() // 2)
y = (app.winfo_screenheight() // 2) - (app.winfo_height() // 2)
app.geometry(f"{app.winfo_width()}x{app.winfo_height()}+{x}+{y}")

# ---------- Widgets ----------
frame = ctk.CTkFrame(app, corner_radius=15)
frame.pack(expand=True, fill="both", padx=20, pady=20)

ctk.CTkLabel(frame, text="ASCII Art Converter", font=("Segoe UI", 24, "bold")).pack(pady=(10, 15))

# --- Input Frame ---
input_frame = ctk.CTkFrame(frame, fg_color="transparent")
input_frame.pack(fill="x", padx=30)

ctk.CTkLabel(input_frame, text="1. Select Image File:").pack(anchor="w")
select_btn = ctk.CTkButton(input_frame, text="Browse...", command=select_image_file, width=100)
select_btn.pack(side="left", pady=10)
file_entry = ctk.CTkEntry(input_frame, placeholder_text="No file selected...", state="disabled", width=400)
file_entry.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=10)

# --- Settings Frame ---
settings_frame = ctk.CTkFrame(frame, fg_color="transparent")
settings_frame.pack(fill="x", padx=30, pady=10)

ctk.CTkLabel(settings_frame, text="2. Choose Settings:").pack(anchor="w", pady=(0, 5))

# Style Menu
style_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
style_container.pack(fill="x", pady=5)
ctk.CTkLabel(style_container, text="Art Style:").pack(side="left", padx=(0, 10))
style_menu = ctk.CTkOptionMenu(style_container, values=list(ASCII_STYLES.keys()))
style_menu.pack(side="left", padx=(0, 20))
style_menu.set("Standard")

# Width Slider
width_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
width_container.pack(fill="x", pady=5)
ctk.CTkLabel(width_container, text="Width (Chars):").pack(side="left", padx=(0, 10))

def update_width_label(value):
    width_value_label.configure(text=f"{int(value)}")

width_slider = ctk.CTkSlider(width_container, from_=50, to=250, number_of_steps=200, command=update_width_label)
width_slider.set(100)
width_slider.pack(side="left", fill="x", expand=True)
width_value_label = ctk.CTkLabel(width_container, text="100", width=30)
width_value_label.pack(side="left", padx=(10, 0))

# Contrast Slider
contrast_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
contrast_container.pack(fill="x", pady=5)
ctk.CTkLabel(contrast_container, text="Contrast Multiplier:").pack(side="left", padx=(0, 10))

def update_contrast_label(value):
    contrast_value_label.configure(text=f"{value:.2f}")

contrast_slider = ctk.CTkSlider(contrast_container, from_=0.0, to=3.0, number_of_steps=30, command=update_contrast_label)
contrast_slider.set(1.0)
contrast_slider.pack(side="left", fill="x", expand=True)
contrast_value_label = ctk.CTkLabel(contrast_container, text="1.00", width=30)
contrast_value_label.pack(side="left", padx=(10, 0))

# Invert Switch
invert_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
invert_container.pack(fill="x", pady=5, anchor="w")
invert_switch = ctk.CTkSwitch(invert_container, text="Invert Light/Dark Mapping", onvalue=1, offvalue=0)
invert_switch.pack(side="left", padx=(0, 10), pady=5)

# --- Action Button ---
convert_btn = ctk.CTkButton(frame, text="Convert to ASCII", command=start_conversion,
                            height=40, font=("Segoe UI", 14, "bold"))
convert_btn.pack(pady=(15, 10), fill="x", padx=30)

# --- Output Area ---
ctk.CTkLabel(frame, text="3. Result:").pack(anchor="w", padx=30, pady=(10, 0))
output_textbox = ctk.CTkTextbox(frame, state="disabled", font=("Courier New", 8))
output_textbox.pack(expand=True, fill="both", padx=30, pady=(5, 15))

# Save & Return Buttons
button_frame = ctk.CTkFrame(frame, fg_color="transparent")
button_frame.pack(fill="x", padx=30, pady=(0, 10))
save_btn = ctk.CTkButton(button_frame, text="Save as .txt", command=save_art)
save_btn.pack(side="right")
return_btn = ctk.CTkButton(button_frame, text="Return to Hub", command=return_to_hub)
return_btn.pack(side="right", padx=(10, 0))

# --- HYPERLINK SETUP ---
LINK_URL = "https://buymeacoffee.com/novafoundry"

def open_link(event):
    webbrowser.open_new_tab(LINK_URL)

bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")
bottom_frame.pack(pady=(0, 10))

ctk.CTkLabel(bottom_frame, text="v1.1.0, © Nova Foundry 2025, ", font=("Segoe UI", 10), text_color="gray")\
    .pack(side=tk.LEFT)
link_label = ctk.CTkLabel(bottom_frame, text="Support Nova Foundry", font=("Segoe UI", 10, "underline"),
                          text_color="#90caf9", cursor="hand2")
link_label.pack(side=tk.LEFT)
link_label.bind("<Button-1>", open_link)

# ---------- Start ----------
app.after(100, initial_conversion_if_default_exists)
app.mainloop()