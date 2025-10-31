# Jack Murray
# Nova Foundry / Echo Hub
# v1.0.4

import os
import sys
import shutil
import zipfile
import threading
import subprocess
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

# ---------- CONFIG ----------
IMPORT_DESTINATION = r"Working_game"
EXPORT_SOURCE = r"Working_game"
DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 640   # taller window to fit new button
PROGRESS_AREA_HEIGHT = 70

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

def update_progress_indicators(current, total, progress):
    progress_bar.set(progress)
    file_status_label.configure(text=f"File {current} of {total}")
    app.update_idletasks()

def run_with_progress(task_name, actions):
    def task():
        total_files = len(actions)
        for i, action in enumerate(actions, start=1):
            action()
            progress = i / total_files if total_files else 1
            app.after(0, lambda c=i, t=total_files, p=progress: update_progress_indicators(c, t, p))
        app.after(0, task_done)
    def task_done():
        hide_progress_indicators()
        for btn in (copy_btn, import_btn, export_btn, open_btn, clear_btn):
            btn.configure(state='normal')
        show_custom_message("Success", f"{task_name} completed successfully!")
    for btn in (copy_btn, import_btn, export_btn, open_btn, clear_btn):
        btn.configure(state='disabled')
    status_label.configure(text=f"{task_name}...")
    show_progress_indicators()
    threading.Thread(target=task, daemon=True).start()

# ---------- Folder Utilities ----------
def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        show_custom_message("Info", f"'{folder_path}' does not exist.")
        return
    if not ask_confirmation("Confirm Deletion",
                            f"The contents of '{folder_path}' will be permanently deleted.\nProceed?"):
        return
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def copy_folder_with_progress(src, dest):
    if os.path.exists(dest):
        if not ask_confirmation("Overwrite Project",
                                f"The working directory '{dest}' contains project files.\nOverwrite its contents?"):
            return []
        clear_folder(dest)
    os.makedirs(dest, exist_ok=True)
    actions = []
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            actions.append(lambda s=s, d=d: shutil.copytree(s, d, dirs_exist_ok=True))
        else:
            actions.append(lambda s=s, d=d: shutil.copy2(s, d))
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
    import_project_from_path(zip_path)

def import_project_from_path(zip_path):
    if os.path.exists(IMPORT_DESTINATION):
        if not ask_confirmation("Overwrite Project",
                                f"The working directory '{IMPORT_DESTINATION}' contains project files.\nOverwrite its contents?"):
            return
        clear_folder(IMPORT_DESTINATION)
    os.makedirs(IMPORT_DESTINATION, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = [info for info in zip_ref.infolist() if not info.is_dir()]
            actions = [lambda info=info, z=zip_ref: z.extract(info.filename, IMPORT_DESTINATION) for info in file_list]
            if actions:
                run_with_progress("Importing project", actions)
            else:
                show_custom_message("Success", "Project imported successfully!")
    except Exception as e:
        show_custom_message("Error", str(e), is_error=True)

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
            if not file_paths:
                app.after(0, task_done, True, "No project found")
                return
            total_files = len(file_paths)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for i, (full_path, arcname) in enumerate(file_paths, start=1):
                    zip_ref.write(full_path, arcname)
                    progress = i / total_files
                    app.after(0, lambda c=i, t=total_files, p=progress: update_progress_indicators(c, t, p))
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

# ---------- Startup File Handling ----------
def check_startup_file():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if file_path.lower().endswith(".echo") and os.path.exists(file_path):
            import_project_from_path(file_path)

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

ctk.CTkLabel(frame, text="Echo Hub", font=("Segoe UI", 20, "bold")).pack(pady=(5, 20))

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

ctk.CTkLabel(frame, text="v1.0.4", font=("Segoe UI", 10), text_color="gray").pack(pady=(0, 10))

# ---------- Start ----------
hide_progress_indicators()
check_startup_file()
app.mainloop()