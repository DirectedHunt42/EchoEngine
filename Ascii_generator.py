# Jack Murray
# Nova Foundry / ASCII Art Converter
# v1.0.0

import os
import subprocess
import threading
import webbrowser
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageEnhance
import tkinter as tk

# ---------- CONFIG ----------
DEFAULT_WIDTH = 700
DEFAULT_HEIGHT = 1000
# Removed PREVIEW_MAX_WIDTH and PREVIEW_MAX_HEIGHT
VERSION = "1.0.0"

# --- ❗ UPDATE THESE PATHS ---
# Add the path to your default preview image (e.g., r"C:\MyImages\default.png")
DEFAULT_PREVIEW_IMAGE_PATH = r"Engine_editor\Icons\Echo_engine\Echo_engine_transparent.png"  
# Add the path to your window icon file (e.g., r"C:\MyImages\icon.ico")
ICON_FILE_PATH = r"Engine_editor\Icons\App_icon\Ascii.ico"             
# --- ❗ ---

# Define ASCII character sets for different styles (reversed for dark-to-light mapping)
ASCII_STYLES = {
    "Standard": "@%#*+=-:. "[::-1],
    "Blocks": "█▓▒░ "[::-1],
    "Complex": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "[::-1],
    "Simple": " .:-=+*#%@",
}
# ---------- Helper Functions ----------

def show_custom_message(title, message, is_error=False):
    """Displays a modal dialog box."""
    dialog = ctk.CTkToplevel(app)
    dialog.title(title)
    dialog.geometry("320x160")
    dialog.resizable(False, False)
    dialog.transient(app)
    dialog.grab_set()
    dialog.update_idletasks()
    
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
        # 1. Resize the image, maintaining aspect ratio
        # We adjust height by 0.55 to correct for non-square character aspect ratio
        width, height = image.size
        aspect_ratio = height / float(width)
        new_height = int(aspect_ratio * new_width * 0.55)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # 2. Convert to grayscale
        grayscale_image = resized_image.convert("L")
        
        # 3. Apply Contrast Enhancement
        if contrast_factor != 1.0:
            enhancer = ImageEnhance.Contrast(grayscale_image)
            grayscale_image = enhancer.enhance(contrast_factor)
            
        # 4. Apply Inversion
        if invert:
            # Invert the grayscale image (0 becomes 255, 255 becomes 0)
            grayscale_image = Image.eval(grayscale_image, lambda x: 255 - x)
            
        # 5. Map pixels to ASCII characters
        pixels = grayscale_image.getdata()
        num_chars = len(style_chars)
        
        ascii_str = ""
        for pixel_value in pixels:
            # Map the 0-255 pixel value to the character list index
            index = int((pixel_value / 255) * (num_chars - 1))
            ascii_str += style_chars[index]
        
        # 6. Format the string with newlines
        ascii_lines = []
        for i in range(0, len(ascii_str), new_width):
            ascii_lines.append(ascii_str[i:i + new_width])
            
        return "\n".join(ascii_lines)
        
    except Exception as e:
        print(f"Error in conversion: {e}")
        return None

# ---------- Main Actions ----------

def select_image_file():
    """Opens a file dialog to select an image and show a preview."""
    file_path = filedialog.askopenfilename(
        title="Select an Image File",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    if file_path:
        # Update the entry box to show the selected file
        file_entry.configure(state='normal')
        file_entry.delete(0, 'end')
        file_entry.insert(0, file_path)
        file_entry.configure(state='disabled')
        
        # ⭐ REMOVED: Preview update logic is gone

def start_conversion():
    """Starts the ASCII conversion in a separate thread, using default if none selected."""
    image_path = file_entry.get()
    
    # 1. Check if an image is selected
    if not image_path or image_path == "[Initial Default Image Loaded]" or image_path == "[Using Default Image]":
        # If no image is selected or it's just the indicator text, use the default path
        fallback_path = DEFAULT_PREVIEW_IMAGE_PATH
        
        # 2. Check if the default path is valid before using it
        if not fallback_path or not os.path.exists(fallback_path):
            show_custom_message(
                "Error", 
                "Please select a valid image file, or ensure the default image path is correct.", 
                is_error=True
            )
            return
        
        # Use the fallback path for conversion
        image_path = fallback_path
        # Update the file_entry to show the default path is being used
        file_entry.configure(state='normal')
        file_entry.delete(0, 'end')
        file_entry.insert(0, "[Using Default Image]") # A visual indicator
        file_entry.configure(state='disabled')

    # 3. If a path was provided (or is now the fallback), ensure it exists on disk
    if not os.path.exists(image_path):
        show_custom_message("Error", "The image file does not exist.", is_error=True)
        return
        
    try:
        # Get settings from the UI
        style_name = style_menu.get()
        style_chars = ASCII_STYLES[style_name]
        width = int(width_slider.get())
        contrast_factor = float(contrast_slider.get())
        invert = bool(invert_switch.get())
        
        # Disable buttons to prevent multiple clicks
        select_btn.configure(state='disabled')
        convert_btn.configure(state='disabled', text="Converting...")
        save_btn.configure(state='disabled')
        
        # Run the heavy lifting in a thread
        threading.Thread(
            target=run_conversion_thread, 
            args=(image_path, style_chars, width, contrast_factor, invert), 
            daemon=True
        ).start()
        
    except Exception as e:
        show_custom_message("Error", f"Failed to start conversion:\n{e}", is_error=True)
        # Re-enable buttons on failure
        select_btn.configure(state='normal')
        convert_btn.configure(state='normal', text="Convert to ASCII")
        save_btn.configure(state='normal')

def run_conversion_thread(image_path, style_chars, width, contrast_factor, invert):
    """The function that runs in the background thread."""
    try:
        image = Image.open(image_path)
        ascii_art = convert_to_ascii(image, style_chars, width, contrast_factor, invert)
        
        if ascii_art:
            # Send the result back to the main thread
            app.after(0, update_ui_with_result, ascii_art)
        else:
            raise Exception("Conversion returned no data.")
            
    except Exception as e:
        error_message = f"Failed to convert image:\n{e}"
        app.after(0, update_ui_with_error, error_message)

def update_ui_with_result(ascii_art):
    """Updates the textbox with the result (runs on main thread)."""
    output_textbox.configure(state='normal')
    output_textbox.delete("1.0", "end")
    output_textbox.insert("1.0", ascii_art)
    output_textbox.configure(state='disabled')
    
    # Re-enable buttons
    select_btn.configure(state='normal')
    convert_btn.configure(state='normal', text="Convert to ASCII")
    save_btn.configure(state='normal')

def update_ui_with_error(error_message):
    """Shows an error message (runs on main thread)."""
    show_custom_message("Conversion Error", error_message, is_error=True)
    
    # Re-enable buttons
    select_btn.configure(state='normal')
    convert_btn.configure(state='normal', text="Convert to ASCII")
    save_btn.configure(state='normal')

def save_art():
    """Saves the content of the textbox to a .txt file."""
    ascii_art = output_textbox.get("1.0", "end-1c") # Get all text except last newline
    if not ascii_art:
        show_custom_message("Error", "There is no art to save!", is_error=True)
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
            show_custom_message("Success", f"Art saved successfully to:\n{file_path}")
        except Exception as e:
            show_custom_message("Save Error", f"Failed to save file:\n{e}", is_error=True)

def return_to_hub():
    try:
        subprocess.Popen("Echo_hub.exe")
        app.destroy()
    except Exception as e:
        show_custom_message("Error", str(e), is_error=True)

# ----------------------------------------------------
# Function to run initial conversion on startup
# ----------------------------------------------------
def initial_conversion_if_default_exists():
    """Performs an initial conversion using the default image and style."""
    
    # Check if a valid default image path exists
    if DEFAULT_PREVIEW_IMAGE_PATH and os.path.exists(DEFAULT_PREVIEW_IMAGE_PATH):
        try:
            # Get initial settings
            default_style_chars = ASCII_STYLES["Standard"]
            default_width = int(width_slider.get())
            default_contrast = float(contrast_slider.get())
            default_invert = bool(invert_switch.get()) 

            # Use the image directly, no need for UI path checks
            image = Image.open(DEFAULT_PREVIEW_IMAGE_PATH)
            
            # Pass initial settings to convert_to_ascii
            ascii_art = convert_to_ascii(
                image, 
                default_style_chars, 
                default_width, 
                default_contrast, 
                default_invert
            )
            
            if ascii_art:
                # Update the UI with the result
                output_textbox.configure(state='normal')
                output_textbox.delete("1.0", "end")
                output_textbox.insert("1.0", ascii_art)
                output_textbox.configure(state='disabled')
                
                # Update file_entry to show what was converted
                file_entry.configure(state='normal')
                file_entry.delete(0, 'end')
                file_entry.insert(0, "[Initial Default Image Loaded]") 
                file_entry.configure(state='disabled')
            
        except Exception as e:
            print(f"Initial conversion failed: {e}")
            pass # Fail silently on startup conversion errors
            
# ---------- App Setup ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("🎨 ASCII Art Converter")
# ⭐ CHANGED: Use the smaller width
app.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
app.resizable(False, False)

# --- Icon ---
if ICON_FILE_PATH and os.path.exists(ICON_FILE_PATH):
    try:
        app.iconbitmap(ICON_FILE_PATH)
    except Exception as e:
        print(f"Could not set window icon: {e}")

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

# Row 1: Style Menu
style_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
style_container.pack(fill="x", pady=5)
style_label = ctk.CTkLabel(style_container, text="Art Style:")
style_label.pack(side="left", padx=(0, 10))
style_menu = ctk.CTkOptionMenu(style_container, values=list(ASCII_STYLES.keys()))
style_menu.pack(side="left", padx=(0, 20))

# Row 2: Width Slider
width_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
width_container.pack(fill="x", pady=5)

width_label = ctk.CTkLabel(width_container, text="Width (Chars):")
width_label.pack(side="left", padx=(0, 10))

def update_width_label(value):
    width_value_label.configure(text=f"{int(value)}")

width_slider = ctk.CTkSlider(width_container, from_=50, to=250, number_of_steps=200, command=update_width_label)
width_slider.set(100)
width_slider.pack(side="left", fill="x", expand=True)

width_value_label = ctk.CTkLabel(width_container, text="100", width=30)
width_value_label.pack(side="left", padx=(10, 0))


# Row 3: Contrast Slider
contrast_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
contrast_container.pack(fill="x", pady=5)

contrast_label = ctk.CTkLabel(contrast_container, text="Contrast Multiplier:")
contrast_label.pack(side="left", padx=(0, 10))

def update_contrast_label(value):
    contrast_value_label.configure(text=f"{value:.2f}")

# Contrast slider goes from 0.0 (no contrast/gray) to 3.0 (high contrast), with default 1.0
contrast_slider = ctk.CTkSlider(contrast_container, from_=0.0, to=3.0, number_of_steps=30, command=update_contrast_label)
contrast_slider.set(1.0)
contrast_slider.pack(side="left", fill="x", expand=True)

contrast_value_label = ctk.CTkLabel(contrast_container, text="1.00", width=30)
contrast_value_label.pack(side="left", padx=(10, 0))

# Row 4: Invert Switch
invert_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
invert_container.pack(fill="x", pady=5, anchor="w")

invert_switch = ctk.CTkSwitch(invert_container, text="Invert Light/Dark Mapping", onvalue=1, offvalue=0)
invert_switch.pack(side="left", padx=(0, 10), pady=5)

# --- Action Button ---
convert_btn = ctk.CTkButton(frame, text="Convert to ASCII",
                            command=start_conversion,
                            height=40, font=("Segoe UI", 14, "bold"))
convert_btn.pack(pady=(15, 10), fill="x", padx=30) 

# --- Output Area ---
ctk.CTkLabel(frame, text="3. Result:").pack(anchor="w", padx=30, pady=(10, 0))

output_textbox = ctk.CTkTextbox(frame, state="disabled", font=("Courier New", 8))
output_textbox.pack(expand=True, fill="both", padx=30, pady=(5, 15))

save_btn = ctk.CTkButton(frame, text="Save as .txt", command=save_art)
return_btn = ctk.CTkButton(frame, text="Return to Hub", command=return_to_hub)
save_btn.pack(pady=(0, 10), anchor="e", padx=30)
return_btn.pack(pady=(0, 10), anchor="e", padx=30)

# --- HYPERLINK SETUP ---
LINK_URL = "https://buymeacoffee.com/novafoundry"

def open_link(event):
    # This function uses the imported `webbrowser` module from earlier
    webbrowser.open_new_tab(LINK_URL)

bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")
bottom_frame.pack(pady=(0, 10))

ctk.CTkLabel(
    bottom_frame, 
    text=f"v1.0.0, © Nova Foundry 2025, ", 
    font=("Segoe UI", 10), 
    text_color="gray"
).pack(side=tk.LEFT, padx=(0, 0))

link_label = ctk.CTkLabel(
    bottom_frame, 
    text="Support Nova Foundry", # The text you want to display for the link
    font=("Segoe UI", 10, "underline"), # Added 'underline' for link appearance
    text_color="#90caf9", # A light blue color for links
    cursor="hand2" # Changes the mouse cursor on hover
)
link_label.pack(side=tk.LEFT, padx=(0, 0))

link_label.bind("<Button-1>", open_link)

# Run initial conversion after widgets are set up
app.after(100, initial_conversion_if_default_exists) 

# ---------- Start ----------
app.mainloop()