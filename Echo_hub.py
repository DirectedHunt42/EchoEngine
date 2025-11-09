# Jack Murray
# Nova Foundry / Echo Hub
# v1.2.1

import os
import sys
import shutil
import webbrowser
import zipfile
import threading
import subprocess
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import urllib.request
import json
import tkinter as tk
import platform

# ---------- CONFIG ----------
IMPORT_DESTINATION = r"Working_game"
EXPORT_SOURCE = r"Working_game"
DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 750
PROGRESS_AREA_HEIGHT = 70
VERSION = "2.5.1"
GITURL = "https://github.com/DirectedHunt42/EchoEngine"
ASCII_ART_GENERATOR_PATH = r"Ascii_generator.exe"
WINDOWS_UPDATE_ASSET = "Echo_Editor_Setup.exe"
UBUNTU_UPDATE_ASSET = "Echo_Editor_Setup_ubuntu.deb"
OTHER_LINUX_UPDATE_ASSET = "Echo_Editor_Setup_linux.sh"
DARWIN_UPDATE_ASSET = "Echo_Editor_Setup_mac.dmg"

# ---------- Helper Functions ----------
def show_custom_message(title, message, is_error=False):
    dialog = ctk.CTkToplevel(app)
    dialog.title(title)
    dialog.geometry("320x160")
    dialog.resizable(False, False)
    dialog.transient(app)
    dialog.grab_set()
    dialog.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - 160
    y = app.winfo_y() + (app.winfo_height() // 2) - 80
    dialog.geometry(f"320x160+{x}+{y}")
    label = ctk.CTkLabel(dialog, text=message, wraplength=280,
                         text_color="red" if is_error else "white")
    label.pack(pady=20, padx=20)
    btn = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, width=100)
    btn.pack(pady=10)

def ask_confirmation(title, message):
    dialog = ctk.CTkToplevel(app)
    dialog.title(title)
    dialog.geometry("360x180")
    dialog.resizable(False, False)
    dialog.transient(app)
    dialog.grab_set()
    dialog.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - 180
    y = app.winfo_y() + (app.winfo_height() // 2) - 90
    dialog.geometry(f"360x180+{x}+{y}")
    label = ctk.CTkLabel(dialog, text=message, wraplength=320)
    label.pack(pady=20, padx=20)
    response = {"confirmed": False}
    def on_yes():
        response["confirmed"] = True
        dialog.destroy()
    def on_no():
        dialog.destroy()
    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=10)
    ctk.CTkButton(btn_frame, text="Yes", command=on_yes, width=100).pack(side="left", padx=10)
    ctk.CTkButton(btn_frame, text="No", command=on_no, width=100).pack(side="left", padx=10)
    dialog.wait_window()
    return response["confirmed"]

def load_resized_image(path, max_size=64):
    if os.path.exists(path):
        try:
            image = Image.open(path)
            ratio = min(max_size / image.width, max_size / image.height)
            resized_image = image.resize(
                (int(image.width * ratio), int(image.height * ratio)), Image.LANCZOS)
            return ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=resized_image.size)
        except Exception as e:
            print(f"Could not load image: {e}")
    return None

def version_tuple(v):
    return tuple(map(int, v.split('.')))

def get_game_title():
    title_path = os.path.join(IMPORT_DESTINATION, "Text", "Misc", "Title.txt")
    try:
        if os.path.exists(title_path):
            with open(title_path, 'r', encoding='utf-8') as f:
                title = f.read().strip()
                if title:  # If title is not empty
                    return title
                return "Untitled Project"
    except Exception:
        pass
    return "No Project Loaded"

def close_engine_processes():
    while subprocess.run(['tasklist'], capture_output=True, text=True).stdout.find('Engine_base.exe') != -1:
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'Engine_base.exe'], 
                        capture_output=True, check=False)
        except Exception:
            pass

# ---------- Progress Bar Logic ----------
def show_progress_indicators():
    new_height = DEFAULT_HEIGHT + PROGRESS_AREA_HEIGHT
    # Lock width to DEFAULT_WIDTH, only change height
    app.geometry(f"{DEFAULT_WIDTH}x{new_height}")
    app.minsize(DEFAULT_WIDTH, new_height)
    progress_bar.pack(pady=5, fill="x", padx=30)
    file_status_label.pack()
    progress_bar.set(0)

def hide_progress_indicators():
    status_label.configure(text="")
    file_status_label.configure(text="")
    progress_bar.pack_forget()
    file_status_label.pack_forget()
    # Lock width to DEFAULT_WIDTH, restore height
    app.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
    app.minsize(DEFAULT_WIDTH, DEFAULT_HEIGHT)

def run_with_progress(task_name, actions):
    def task():
        total_files = len(actions)
        for i, item in enumerate(actions, start=1):
            if isinstance(item, tuple):
                action, desc = item
            else:
                action = item
                desc = "Processing"
            app.after(0, lambda d=desc, c=i, t=total_files: file_status_label.configure(text=f"{d} ({c}/{t})"))
            action()
            progress = i / total_files if total_files else 1
            app.after(0, lambda p=progress: progress_bar.set(p))
        app.after(0, task_done)
    def task_done():
        hide_progress_indicators()
        for btn in (copy_btn, import_btn, export_btn, open_btn, clear_btn):
            btn.configure(state='normal')
        update_project_title()
        show_custom_message("Success", f"{task_name} completed successfully!")
    for btn in (copy_btn, import_btn, export_btn, open_btn, clear_btn):
        btn.configure(state='disabled')
    status_label.configure(text=f"{task_name}...")
    show_progress_indicators()
    threading.Thread(target=task, daemon=True).start()

# ---------- Folder Utilities ----------
def get_clear_actions(folder_path):
    actions = []
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for filename in files:
            file_path = os.path.join(root, filename)
            actions.append((lambda p=file_path: os.unlink(p), f"Deleting {os.path.relpath(file_path, folder_path)}"))
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            actions.append((lambda p=dir_path: os.rmdir(p), f"Removing directory {os.path.relpath(dir_path, folder_path)}"))
    return actions

def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        show_custom_message("Info", f"'{folder_path}' does not exist.")
        return
    if not ask_confirmation("Confirm Deletion",
                            f"The contents of '{folder_path}' will be permanently deleted.\nProceed?"):
        return
    close_engine_processes()
    actions = get_clear_actions(folder_path)
    if actions:
        run_with_progress("Clearing working directory", actions)
    else:
        show_custom_message("Info", "Directory is already empty.")

def copy_folder_with_progress(src, dest):
    actions = []
    if os.path.exists(dest):
        if not ask_confirmation("Overwrite Project",
                                f"The working directory '{dest}' contains project files.\nOverwrite its contents?"):
            return []
        actions.extend(get_clear_actions(dest))
    # Collect directory creation actions
    for root, dirs, _ in os.walk(src):
        rel_root = os.path.relpath(root, src)
        dest_root = os.path.join(dest, rel_root)
        for dir_name in dirs:
            dir_path = os.path.join(dest_root, dir_name)
            rel_dir = os.path.join(rel_root, dir_name)
            actions.append((lambda p=dir_path: os.makedirs(p, exist_ok=True), f"Creating directory {rel_dir}"))
    # Collect file copy actions
    for root, _, files in os.walk(src):
        rel_root = os.path.relpath(root, src)
        dest_root = os.path.join(dest, rel_root)
        for filename in files:
            src_path = os.path.join(root, filename)
            dest_path = os.path.join(dest_root, filename)
            rel_path = os.path.join(rel_root, filename)
            actions.append((lambda s=src_path, d=dest_path: shutil.copy2(s, d), f"Copying {rel_path}"))
    return actions

# ---------- Main Actions ----------
def copy_folder_contents():
    try:
        actions = copy_folder_with_progress(r"Engine_base", IMPORT_DESTINATION)
        if actions:
            run_with_progress("Creating new project", actions)
        else:
            show_custom_message("Cancelled", "Project creation cancelled.")
    except Exception as e:
        show_custom_message("Error", str(e), is_error=True)

def import_zip():
    zip_path = filedialog.askopenfilename(filetypes=[("Echo Project", "*.echo")])
    if not zip_path:
        return
    import_project(zip_path)

def import_project(zip_path):
    if os.path.exists(IMPORT_DESTINATION):
        if not ask_confirmation("Overwrite Project",
                                f"The working directory '{IMPORT_DESTINATION}' contains project files.\nOverwrite its contents?"):
            return
    close_engine_processes()
    for btn in (copy_btn, import_btn, export_btn, open_btn, clear_btn):
        btn.configure(state='disabled')
    status_label.configure(text="Importing project...")
    show_progress_indicators()
    def task_done(success=True, message="Project imported successfully!"):
        hide_progress_indicators()
        for btn in (copy_btn, import_btn, export_btn, open_btn, clear_btn):
            btn.configure(state='normal')
        if success:
            update_project_title()
            show_custom_message("Success", message)
        else:
            show_custom_message("Error", message, is_error=True)
    def import_task():
        try:
            os.makedirs(IMPORT_DESTINATION, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = [info for info in zip_ref.infolist() if not info.is_dir()]
                total_files = len(file_list)
                if not total_files:
                    app.after(0, task_done, True, "Empty project")
                    return
                for i, info in enumerate(file_list, start=1):
                    app.after(0, lambda f=info.filename, c=i, t=total_files: file_status_label.configure(text=f"Extracting {f} ({c}/{t})"))
                    zip_ref.extract(info, IMPORT_DESTINATION)
                    progress = i / total_files
                    app.after(0, lambda p=progress: progress_bar.set(p))
            app.after(0, task_done)
        except Exception as e:
            app.after(0, task_done, False, str(e))
    threading.Thread(target=import_task, daemon=True).start()

def export_zip():
    zip_path = filedialog.asksaveasfilename(defaultextension=".echo",
                                            filetypes=[("Echo Project", "*.echo")])
    if not zip_path:
        return
    for btn in (copy_btn, import_btn, export_btn, open_btn, clear_btn):
        btn.configure(state='disabled')
    status_label.configure(text="Exporting project...")
    show_progress_indicators()
    def task_done(success=True, message="Project exported successfully!"):
        hide_progress_indicators()
        for btn in (copy_btn, import_btn, export_btn, open_btn, clear_btn):
            btn.configure(state='normal')
        if success:
            show_custom_message("Success", message)
        else:
            show_custom_message("Error", message, is_error=True)
    def export_task():
        try:
            file_paths = []
            for root, _, files in os.walk(EXPORT_SOURCE):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, EXPORT_SOURCE)
                    file_paths.append((full_path, arcname))
            total_files = len(file_paths)
            if not total_files:
                app.after(0, task_done, True, "No project found")
                return
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for i, (full_path, arcname) in enumerate(file_paths, start=1):
                    app.after(0, lambda a=arcname, c=i, t=total_files: file_status_label.configure(text=f"Adding {a} ({c}/{t})"))
                    zip_ref.write(full_path, arcname)
                    progress = i / total_files
                    app.after(0, lambda p=progress: progress_bar.set(p))
            app.after(0, task_done)
        except Exception as e:
            app.after(0, task_done, False, str(e))
    threading.Thread(target=export_task, daemon=True).start()

def open_project():
    try:
        subprocess.Popen("Engine_editor/Echo_editor.exe")
        app.destroy()
    except Exception as e:
        show_custom_message("Error", str(e), is_error=True)

def open_ascii_generator():
    if not os.path.exists(ASCII_ART_GENERATOR_PATH):
        show_custom_message("Error", f"ASCII Art Generator not found at:\n{ASCII_ART_GENERATOR_PATH}", is_error=True)
        return
    try:
        # Launch the executable without waiting for it to finish
        subprocess.Popen(ASCII_ART_GENERATOR_PATH)
        app.destroy()
    except Exception as e:
        show_custom_message("Error", f"Failed to open ASCII Art Generator: {str(e)}", is_error=True)

# ---------- Auto Update ----------
def check_for_update():
    def check_task():
        try:
            url = "https://api.github.com/repos/DirectedHunt42/EchoEngine/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'EchoHub', 'Accept': 'application/vnd.github.v3+json'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
            app.after(0, lambda d=data: do_update_confirm(d))
        except:
            pass
    threading.Thread(target=check_task, daemon=True).start()

def do_update_confirm(data):
    try:
        title = data.get('name', '')
        if title.startswith("Release "):
            new_ver = title[len("Release "):].strip()
        else:
            return
        current_ver = VERSION
        current_t = version_tuple(current_ver)
        new_t = version_tuple(new_ver)
        if new_t > current_t:
            if ask_confirmation("Update Available", f"New version {new_ver} available (current {current_ver}).\nDownload and install?"):
                export_zip()  # Auto-export current project before updating
                download_and_install(data)
    except:
        pass

def download_and_install(data):
    os_name = platform.system().lower()
    asset_name = None
    run_command = None
    needs_chmod = False

    if os_name == 'windows':
        asset_name = WINDOWS_UPDATE_ASSET
        run_command = [setup_file]
    elif os_name == 'darwin':
        asset_name = DARWIN_UPDATE_ASSET
        run_command = ['open', setup_file]
    elif os_name == 'linux':
        if shutil.which('dpkg'):
            asset_name = UBUNTU_UPDATE_ASSET
            run_command = ['xdg-open', setup_file]  # Opens .deb with installer
        else:
            asset_name = OTHER_LINUX_UPDATE_ASSET
            run_command = ['sh', setup_file]
            needs_chmod = True
    else:
        show_custom_message("Error", "Unsupported operating system.", is_error=True)
        return

    assets = data.get('assets', [])
    download_url = None
    for asset in assets:
        if asset['name'] == asset_name:
            download_url = asset['browser_download_url']
            break
    if not download_url:
        show_custom_message("Error", f"Update file '{asset_name}' not found for your OS.", is_error=True)
        return

    setup_file = os.path.join(os.path.dirname(sys.argv[0]), asset_name)
    for btn in (copy_btn, import_btn, export_btn, open_btn, clear_btn):
        btn.configure(state='disabled')
    status_label.configure(text="Downloading update...")
    show_progress_indicators()
    def download_task():
        try:
            def reporthook(count, block_size, total_size):
                if total_size <= 0:
                    app.after(0, file_status_label.configure(text="Downloading..."))
                    return
                progress = min(1.0, float(count * block_size) / total_size)
                mb_done = (count * block_size) / (1024 ** 2)
                mb_total = total_size / (1024 ** 2)
                app.after(0, file_status_label.configure(text=f"Downloading ({mb_done:.2f}/{mb_total:.2f} MB)"))
                app.after(0, lambda p=progress: progress_bar.set(p))
            urllib.request.urlretrieve(download_url, setup_file, reporthook)
            if needs_chmod:
                os.chmod(setup_file, 0o755)
            app.after(0, hide_progress_indicators)
            app.after(0, lambda: show_custom_message("Update Ready", "Update downloaded. Installing..."))
            subprocess.Popen(run_command)
            app.after(100, app.destroy)
        except Exception as e:
            app.after(0, hide_progress_indicators)
            app.after(0, lambda: show_custom_message("Error", str(e), is_error=True))
            for btn in (copy_btn, import_btn, export_btn, open_btn, clear_btn):
                btn.configure(state='normal')
    threading.Thread(target=download_task, daemon=True).start()

# ---------- Startup File Handling ----------
def check_startup_file():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if file_path.lower().endswith(".echo") and os.path.exists(file_path):
            # Use the same UI logic as the import button
            def do_import():
                import_project(file_path)
            app.after(100, do_import)

# ---------- App Setup ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("📂 Echo Hub")
app.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
app.resizable(False, True)  # width fixed, height adjustable
app.minsize(DEFAULT_WIDTH, DEFAULT_HEIGHT)

# Icon
icon_path = r"Engine_editor\Icons\Echo_hub.ico"
if os.path.exists(icon_path):
    try:
        app.iconbitmap(icon_path)
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

icon_ctk = load_resized_image(icon_path)
if icon_ctk:
    ctk.CTkLabel(frame, image=icon_ctk, text="").pack(pady=(10, 5))

ctk.CTkLabel(frame, text="Echo Hub", font=("Segoe UI", 20, "bold")).pack(pady=(5, 5))
project_title_label = ctk.CTkLabel(frame, text=get_game_title(), font=("Segoe UI", 14), text_color="#90caf9")  # Light blue color
project_title_label.pack(pady=(0, 20))

def update_project_title():
    project_title_label.configure(text=get_game_title())

btn_width, btn_height = 250, 40
btn_color = ("#666666", "#555555")

copy_btn = ctk.CTkButton(frame, text="New Project", command=copy_folder_contents,
                         width=btn_width, height=btn_height, corner_radius=10, fg_color=btn_color)
copy_btn.pack(pady=10)

import_btn = ctk.CTkButton(frame, text="Import Project", command=import_zip,
                           width=btn_width, height=btn_height, corner_radius=10, fg_color=btn_color)
import_btn.pack(pady=10)

open_btn = ctk.CTkButton(frame, text="Open Project in Editor", command=open_project,
                         width=btn_width, height=btn_height, corner_radius=10, fg_color=btn_color)
open_btn.pack(pady=10)

export_btn = ctk.CTkButton(frame, text="Export Project", command=export_zip,
                           width=btn_width, height=btn_height, corner_radius=10, fg_color=btn_color)
export_btn.pack(pady=10)

clear_btn = ctk.CTkButton(frame, text="Clear Working Directory",
                          command=lambda: clear_folder(IMPORT_DESTINATION),
                          width=btn_width, height=btn_height, corner_radius=10, fg_color=btn_color)
clear_btn.pack(pady=10)

ascii_btn = ctk.CTkButton(frame, text="ASCII Art Generator", command=open_ascii_generator,
                          width=btn_width - 50,  # Smaller width
                          height=btn_height - 10, # Smaller height
                          corner_radius=8)
ascii_btn.pack(pady=(15, 20)) # Added a bit more padding for separation

progress_frame = ctk.CTkFrame(frame, fg_color="transparent")
status_label = ctk.CTkLabel(progress_frame, text="", font=("Segoe UI", 12))
status_label.pack(pady=(0, 2))
progress_bar = ctk.CTkProgressBar(progress_frame, height=15)
file_status_label = ctk.CTkLabel(progress_frame, text="", font=("Segoe UI", 10), text_color="gray")

bottom_logo_path = r"Engine_editor\Icons\Nova_foundry\Nova_foundry_wide_transparent.png"
logo_ctk = load_resized_image(bottom_logo_path, max_size=128)
if logo_ctk:
    progress_frame.pack(pady=10, fill="x")
    logo_label = ctk.CTkLabel(frame, image=logo_ctk, text="")
    logo_label.pack(pady=10)

# --- HYPERLINK SETUP ---
LINK_URL = "https://buymeacoffee.com/novafoundry"

def open_link(event):
    # This function uses the imported `webbrowser` module from earlier
    webbrowser.open_new_tab(LINK_URL)

bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")
bottom_frame.pack(pady=(0, 10))

ctk.CTkLabel(
    bottom_frame, 
    text=f"v1.2.1, © Nova Foundry 2025, Git Release: {VERSION}, ", 
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

# ---------- Start ----------
hide_progress_indicators()
check_for_update()
check_startup_file()
app.mainloop()