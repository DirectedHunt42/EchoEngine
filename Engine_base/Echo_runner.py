import os
import tkinter as tk
from tkinter import font as tkFont
import threading
import time
import random
import pygame
from PIL import Image, ImageTk
import traceback
import sys

class MainForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.output_buffer = ""
        self.user_input = None
        self.input_lock = threading.Lock()
        self.prompt_position = 0

        # Read the title from the text file
        window_title = ""
        try:
            title_path = os.path.join("Text", "Misc", "Title.txt")
            if os.path.exists(title_path):
                with open(title_path, 'r') as title_reader:
                    window_title = title_reader.readline().strip() or "Echo Engine"
        except Exception:
            window_title = "Echo Engine"

        self.title(window_title)

        # Start playing sound in the background
        threading.Thread(target=self.play_sound, daemon=True).start()

        # Set app icon
        try:
            icon_path = os.path.join("Icons", "Icon.ico")
            if not os.path.exists(icon_path):
                icon_path = os.path.join("Icons", "Default_icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon loading error: {e}")

        # Load custom fonts if available, else fallback
        main_font_family = "Consolas"
        title_font_family = "Consolas"
        try:
            font_path = os.path.join("Fonts", "Font.ttf")
            if os.path.exists(font_path):
                main_font_family = tkFont.nametofont(font_path).actual()['family']
        except:
            pass
        try:
            title_font_path = os.path.join("Fonts", "Title_font.ttf")
            if os.path.exists(title_font_path):
                title_font_family = tkFont.nametofont(title_font_path).actual()['family']
        except:
            pass
        # Fallback to Default.ttf if needed
        if main_font_family == "Consolas":
            try:
                default_font_path = os.path.join("Fonts", "Default.ttf")
                if os.path.exists(default_font_path):
                    main_font_family = tkFont.nametofont(default_font_path).actual()['family']
            except:
                pass
        if title_font_family == "Consolas":
            title_font_family = main_font_family

        main_font = tkFont.Font(family=main_font_family, size=13)
        title_font = tkFont.Font(family=title_font_family, size=13, weight="bold")

        self.attributes('-fullscreen', True)

        # Title bar simulation
        title_bar = tk.Frame(self, bg="black", height=30)
        title_bar.pack(fill="x")

        title_label = tk.Label(title_bar, text=" " + window_title, fg="#DCDCDC", bg="black", font=title_font)
        title_label.pack(side="left")

        button_panel = tk.Frame(title_bar, bg="black")
        button_panel.pack(side="right")

        min_btn = tk.Button(button_panel, text="-", fg="white", bg="black", relief="flat", command=self.iconify)
        min_btn.pack(side="right", padx=5)

        close_btn = tk.Button(button_panel, text="X", fg="white", bg="black", relief="flat", command=self.quit)
        close_btn.pack(side="right")

        # Separator
        separator = tk.Frame(self, height=1, bg="white")
        separator.pack(fill="x")

        # Output area
        self.output_area = tk.Text(self, wrap="word", bg="black", fg="#DCDCDC", font=main_font, borderwidth=0)
        self.output_area.pack(fill="both", expand=True)

        self.output_area.bind("<KeyPress>", self.output_area_key_press)
        self.output_area.bind("<Return>", self.output_area_key_down)

        # Drag title bar
        title_bar.bind("<Button-1>", self.start_move)
        title_bar.bind("<ButtonRelease-1>", self.stop_move)
        title_bar.bind("<B1-Motion>", self.do_move)

        self.mouse_down_comp_coords = None

        self.after(100, self.show_logo_and_start, window_title)

    def start_move(self, event):
        self.mouse_down_comp_coords = (event.x, event.y)

    def stop_move(self, event):
        self.mouse_down_comp_coords = None

    def do_move(self, event):
        if self.mouse_down_comp_coords:
            delta_x = event.x - self.mouse_down_comp_coords[0]
            delta_y = event.y - self.mouse_down_comp_coords[1]
            self.geometry(f"+{self.winfo_x() + delta_x}+{self.winfo_y() + delta_y}")

    def play_sound(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(os.path.join("Sounds", "Background.wav"))
            pygame.mixer.music.play(-1)
        except Exception as ex:
            print(str(ex))

    def scroll_to_end(self):
        self.output_area.see("end")

    def output_area_key_press(self, e):
        current_pos = self.output_area.index(tk.INSERT)
        prompt_pos = f"1.{self.prompt_position}"
        if self.output_area.compare(current_pos, "<", prompt_pos):
            self.output_area.mark_set(tk.INSERT, "end")
            return "break"

    def output_area_key_down(self, e):
        if self.output_area.compare(tk.INSERT, "<=", f"1.{self.prompt_position}"):
            return "break"
        text = self.output_area.get("1.0", "end")
        input_text = text[self.prompt_position:].strip()
        with self.input_lock:
            self.user_input = input_text
        self.output_area.mark_set(tk.INSERT, "end")
        return "break"

    def show_logo_and_start(self, window_title):
        logo = ""
        try:
            logo_path = os.path.join("Icons", "Echo_engine_logo.txt")
            if os.path.exists(logo_path):
                logo = open(logo_path, 'r').read()
            else:
                logo = "[Echo Engine Logo Not Found]"
        except:
            logo = "[Echo Engine Logo Error]"

        # Center logo
        self.output_area.delete("1.0", "end")
        logo_lines = logo.splitlines()
        area_width_px = self.output_area.winfo_width()
        char_width = self.output_area['font'].measure("W")
        area_width_chars = max(10, area_width_px // char_width)
        centered_logo = ""
        for line in logo_lines:
            trimmed = line[:area_width_chars]
            horizontal_padding = (area_width_chars - len(trimmed)) // 2
            centered_logo += ' ' * horizontal_padding + trimmed + '\n'
        area_height_px = self.output_area.winfo_height()
        font_height = self.output_area['font'].metrics()["linespace"]
        lines = len(logo_lines)
        pad_lines = max(0, (area_height_px // font_height - lines) // 2)
        vertical_pad = '\n' * pad_lines
        self.output_area.insert("1.0", vertical_pad + centered_logo)
        self.scroll_to_end()

        time.sleep(2)

        self.run_game(window_title)

    def get_user_input(self):
        self.print_prompt()
        with self.input_lock:
            while self.user_input is None:
                self.update()
                time.sleep(0.1)
            input_val = self.user_input
            self.user_input = None
            return input_val

    def print_prompt(self):
        self.output_area.insert("end", "")
        self.scroll_to_end()
        self.prompt_position = len(self.output_area.get("1.0", "end")) - 1  # adjust for newline

    def print_to_output(self, text, delay_ms=0):
        text = text.replace("\n", "\n")
        skip = [False]
        def skip_handler(e):
            if e.keysym == "space":
                skip[0] = True
        self.bind("<Key>", skip_handler)
        try:
            index = 0
            while index < len(text):
                if skip[0]:
                    self.output_area.insert("end", text[index:])
                    self.scroll_to_end()
                    self.prompt_position = len(self.output_area.get("1.0", "end")) - 1
                    break
                c = text[index]
                index += 1
                self.output_area.insert("end", c)
                self.scroll_to_end()
                self.prompt_position = len(self.output_area.get("1.0", "end")) - 1
                if delay_ms > 0:
                    time.sleep(delay_ms / 1000)
                self.update()
        finally:
            self.unbind("<Key>")

    def clear_output(self):
        self.output_area.delete("1.0", "end")
        self.prompt_position = 0
        self.scroll_to_end()

    def run_game(self, window_title):
        menu_text = window_title + "\n\n MAIN MENU\n\n PLAY    - [1]\n HELP    - [2]\n EXIT    - [3]\n CREDITS - [4]\n RESET   - [5]\n\n >> "
        help_text = "TO NAVIGATE THE WORLD, USE SIMPLE COMMANDS\n\nAVALABLE COMMANDS:\n north\n south\n east\n west\n up\n down\n inventory\n search\n use\n menu"
        menu_input = 0
        location = None
        menu_loop = True

        self.clear_output()
        self.print_to_output("PRESS ENTER TO START... ")
        self.get_user_input()
        self.clear_output()

        while menu_loop:
            self.print_to_output(menu_text, 10)
            input_str = self.get_user_input()
            try:
                menu_input = int(input_str.strip())
            except ValueError:
                menu_input = -1
            if menu_input == 1:
                try:
                    file_path = os.path.join("Save", "Location.txt")
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            location = f.readline().strip()
                            if not location:
                                location = "2"
                except:
                    location = "2"
                if location == "2":
                    self.prolog(None)
                elif len(location) >= 3 and location[0] == '0':
                    self.clear_output()
                    self.tutorial(int(location[1]), int(location[2]), None)
                elif len(location) >= 4 and location[0] == '1':
                    self.clear_output()
                    self.game(int(location[1]), int(location[2]), int(location[3]), None)
                else:
                    self.prolog(None)
            elif menu_input == 2:
                self.clear_output()
                self.print_to_output(help_text, 10)
                self.print_to_output("\n\nPRESS ENTER TO CONTINUE... ")
                self.get_user_input()
                self.clear_output()
            elif menu_input == 3:
                menu_loop = False
            elif menu_input == 4:
                credits_path = os.path.join("Text", "Misc", "Credits.txt")
                credits_text = ""
                try:
                    if os.path.exists(credits_path):
                        with open(credits_path, 'r') as f:
                            credits_text = f.read()
                except:
                    credits_text = "Credits not found."
                self.print_to_output("\n\n" + credits_text)
                self.print_to_output("\n\nPRESS ENTER TO CONTINUE... ")
                self.get_user_input()
                self.clear_output()
            elif menu_input == 5:
                self.reset()
                self.print_to_output("\n\nRESET\n\n PLEASE RESTART THE PROGRAM")
                self.get_user_input()
                self.quit()
            else:
                self.print_to_output("\n\nTHAT IS NOT A VAILD INPUT")
                time.sleep(2)
                self.clear_output()
        self.quit()

    def prolog(self, scanner):
        display_text = " "
        self.clear_output()
        self.reset()
        try:
            file_path = os.path.join("Text", "Stories", "Prolog", "Prolog.txt")
            with open(file_path, 'r') as f:
                display_text = f.read()
        except:
            display_text = "Prolog not found."
        self.print_to_output("\n\n" + display_text, 10)
        self.print_to_output("\n\nPRESS ENTER TO CONTINUE... ")
        self.get_user_input()
        self.clear_output()
        self.tutorial(1, 1, scanner)

    def tutorial(self, input_y, input_x, scanner):
        x = input_x
        y = input_y
        options_text = "\n\n INPUT >> "
        help_text = "\n\nAVALABLE COMMANDS:\n north\n south\n east\n west\n up\n down\n inventory\n search\n use\n menu"
        description = " "
        exits = " "
        items = " "
        input_str = " "
        tutorial_done = False

        try:
            with open(os.path.join("Save", "Location.txt"), 'w') as writer:
                writer.write("0" + str(y) + str(x) + "1")
        except Exception as ex:
            print(str(ex))

        first_loop = True
        while not tutorial_done:
            try:
                desc_path = os.path.join("Text", "Room_descriptions", "Tutorial", "y" + str(y) + "_x" + str(x), "Description.txt")
                with open(desc_path, 'r') as f:
                    description = f.read()
            except:
                description = "Room description not found."
            try:
                exits_path = os.path.join("Text", "Room_descriptions", "Tutorial", "y" + str(y) + "_x" + str(x), "Exits.txt")
                with open(exits_path, 'r') as reader:
                    exits = reader.readline().strip()
            except:
                exits = ""
            if not first_loop:
                self.clear_output()
            self.print_to_output(description, 10)
            self.print_to_output("\n\n Possible Exits: " + exits)
            self.print_to_output(help_text)
            self.print_to_output(options_text)
            first_loop = False
            if scanner is None:
                input_str = self.get_user_input()
            else:
                input_str = scanner.readline().strip() if scanner else ""
            if input_str in ["north", "south", "east", "west"]:
                returned = self.move(input_str, exits, x, y, 0, "cabin")
                x = returned[0]
                y = returned[1]
            elif input_str in ["up", "down"]:
                self.print_to_output("\n\nYou can't go that way.")
            elif input_str == "inventory":
                self.print_to_output(self.inventory())
            elif input_str == "search":
                found_msg = self.search(items, x, y, 0, "cabin")
                self.print_to_output("\n")
                self.print_to_output(found_msg)
                if found_msg.strip().lower() != "you found nothing":
                    self.print_to_output("\n")
            elif input_str == "use":
                self.print_to_output("\n You can't do that here")
            elif input_str == "menu":
                self.print_to_output("\n\nReturning to main menu...")
                self.run_game(self.title())
            else:
                self.print_to_output("\n\n THAT IS NOT A VALID INPUT")

            self.print_to_output("\n\nPRESS ENTER TO CONTINUE... ")
            if scanner is None:
                self.get_user_input()
            else:
                scanner.readline()

            if self.check_inventory_tutorial():
                tutorial_done = True

        self.clear_output()
        desc = ""
        try:
            file_path = os.path.join("Text", "Stories", "Tutorial", "Tutorial_completed.txt")
            with open(file_path, 'r') as f:
                desc = f.read()
        except:
            desc = "Leaving the cabin text not found."
        self.print_to_output(desc)
        self.print_to_output("\n\nPRESS ENTER TO CONTINUE... ")
        if scanner is None:
            self.get_user_input()
        else:
            scanner.readline()
        self.game(1, 1, 1, scanner)

    def game(self, input_y, input_x, input_z, scanner):
        rand = random.Random()
        damage_chance = 10
        try:
            file_path = os.path.join("Finishing", "Damage_chance.txt")
            if os.path.exists(file_path):
                with open(file_path, 'r') as reader:
                    line = reader.readline().strip()
                    if line:
                        damage_chance = int(line)
        except:
            pass
        to_haunt = rand.randint(1, damage_chance)
        sanity = 1
        x = input_x
        y = input_y
        z = input_z
        options_text = "\n\n INPUT >> "
        help_text = "\n\nAVALABLE COMMANDS:\n north\n south\n east\n west\n up\n down\n inventory\n search\n use\n menu"
        description = " "
        exits = " "
        items = " "
        haunting = " "
        input_str = " "
        used = " "
        game_done = False

        try:
            with open(os.path.join("Save", "Location.txt"), 'w') as writer:
                writer.write("1" + str(y) + str(x) + str(z))
        except Exception as ex:
            print(str(ex))
        try:
            health_path = os.path.join("Save", "Health.txt")
            if os.path.exists(health_path):
                line = open(health_path, 'r').read().strip()
                if line:
                    sanity = int(line)
        except:
            pass

        while not game_done:
            try:
                desc_path = os.path.join("Text", "Room_descriptions", "Main", "floor_" + str(z), "y" + str(y) + "_x" + str(x), "Description.txt")
                description = open(desc_path, 'r').read()
            except:
                description = "Room description not found."
            try:
                exits_path = os.path.join("Text", "Room_descriptions", "Main", "floor_" + str(z), "y" + str(y) + "_x" + str(x), "Exits.txt")
                with open(exits_path, 'r') as reader:
                    exits = reader.readline().strip()
            except:
                exits = ""
            to_haunt = rand.randint(1, 5)
            try:
                haunt_path = os.path.join("Text", "Room_descriptions", "Main", "floor_" + str(z), "y" + str(y) + "_x" + str(x), "Strange_occerance.txt")
                haunting = open(haunt_path, 'r').read()
            except:
                haunting = ""
            self.clear_output()
            self.print_to_output("HEALTH: " + "#" * sanity + "\n\n")
            self.print_to_output(description, 10)
            if to_haunt == 1:
                self.print_to_output("\n\n" + haunting)
                self.print_to_output("\n\nYour health has decreased")
                if sanity > 0:
                    sanity -= 1
                    try:
                        with open(os.path.join("Save", "Health.txt"), 'w') as writer:
                            writer.write(str(sanity))
                    except:
                        pass
            if sanity == 0:
                self.print_to_output("\n\nPRESS ENTER TO CONTINUE... ")
                if scanner is None:
                    self.get_user_input()
                else:
                    scanner.readline()
                self.game_over()
            self.print_to_output("\n\n Possible Exits: " + exits)
            self.print_to_output(help_text)
            self.print_to_output(options_text)
            if scanner is None:
                input_str = self.get_user_input()
            else:
                input_str = scanner.readline().strip() if scanner else ""
            if input_str in ["north", "south", "east", "west", "up", "down"]:
                returned = self.move(input_str, exits, x, y, z, "mansion")
                x = returned[0]
                y = returned[1]
                z = returned[2]
            elif input_str == "inventory":
                self.print_to_output(self.inventory())
            elif input_str == "search":
                found_msg = self.search(items, x, y, z, "mansion")
                self.print_to_output("\n")
                self.print_to_output(found_msg)
                if found_msg.strip().lower() != "you found nothing":
                    self.print_to_output("\n")
            elif input_str == "use":
                used = self.use_item(x, y, z)
                self.print_to_output(used)
            elif input_str == "menu":
                self.print_to_output("\n\nReturning to main menu...")
                self.run_game(self.title())
            else:
                self.print_to_output("\n\n THAT IS NOT A VALID INPUT")

            self.print_to_output("\n\nPRESS ENTER TO CONTINUE... ")
            if scanner is None:
                self.get_user_input()
            else:
                scanner.readline()

    def move(self, direction, exits, x, y, z, location):
        inventory_items = []
        try:
            inv_path = os.path.join("Save", "Inventory.txt")
            inventory_items = [line.strip() for line in open(inv_path, 'r')]
        except Exception as ex:
            print(str(ex))
        if direction in exits.split():
            if direction == "north":
                y -= 1
            elif direction == "south":
                y += 1
            elif direction == "east":
                x += 1
            elif direction == "west":
                x -= 1
            elif direction == "up":
                z += 1
            elif direction == "down":
                z -= 1
        else:
            self.print_to_output("\n\nYou can't go that way.")
        h = 0 if location == "cabin" else 1
        try:
            with open(os.path.join("Save", "Location.txt"), 'w') as writer:
                writer.write(str(h) + str(y) + str(x) + str(z))
        except Exception as ex:
            print(str(ex))
        return [x, y, z]

    def inventory(self):
        inventory_items = []
        try:
            inv_path = os.path.join("Save", "Inventory.txt")
            inventory_items = [line.strip() for line in open(inv_path, 'r')]
        except Exception as ex:
            print(str(ex))
        if not inventory_items:
            return "\n\nYour inventory is empty"
        else:
            return "\nYour inventory:\n" + "\n".join(inventory_items)

    def search(self, items, x, y, z, location):
        inventory_history = set()
        items_found = []
        entries = 0
        try:
            hist_path = os.path.join("Save", "Inventory_history.txt")
            inventory_history = set(line.strip() for line in open(hist_path, 'r'))
        except Exception as ex:
            print(str(ex))
        items_list = []
        if location == "cabin":
            try:
                items_path = os.path.join("Text", "Room_descriptions", "Tutorial", "y" + str(y) + "_x" + str(x), "Items.txt")
                items_list = [line.strip() for line in open(items_path, 'r')]
            except Exception as ex:
                print(str(ex))
        elif location == "mansion":
            try:
                items_path = os.path.join("Text", "Room_descriptions", "Main", "Floor_" + str(z), "y" + str(y) + "_x" + str(x), "Items.txt")
                items_list = [line.strip() for line in open(items_path, 'r')]
            except Exception as ex:
                print(str(ex))
        for item in items_list:
            if item not in inventory_history:
                if "Journal Entry" in item:
                    entries += 1
                try:
                    inv_path = os.path.join("Save", "Inventory.txt")
                    with open(inv_path, 'a') as f:
                        f.write(item + "\n")
                    hist_path = os.path.join("Save", "Inventory_history.txt")
                    with open(hist_path, 'a') as f:
                        f.write(item + "\n")
                    items_found.append(item)
                except Exception as ex:
                    print(str(ex))
        try:
            with open(os.path.join("Save", "Journal.txt"), 'w') as f:
                f.write(str(entries))
        except Exception as ex:
            print(str(ex))
        if not items_found:
            return "\n\nYou found nothing"
        else:
            return "\n\nYou found:\n" + "\n".join(items_found)

    def use_item(self, x, y, z):
        result = ""
        required_items = []
        try:
            req_path = os.path.join("Finishing", "Required_items.txt")
            if os.path.exists(req_path):
                required_items = [line.strip() for line in open(req_path, 'r') if line.strip()]
        except:
            pass
        required_x = -1
        required_y = -1
        required_z = -1
        try:
            loc_path = os.path.join("Finishing", "Required_room.txt")
            if os.path.exists(loc_path):
                lines = [line.strip() for line in open(loc_path, 'r')]
                if len(lines) > 0:
                    required_x = int(lines[0])
                if len(lines) > 1:
                    required_y = int(lines[1])
                if len(lines) > 2:
                    required_z = int(lines[2])
        except:
            pass
        inventory_items = []
        try:
            inv_path = os.path.join("Save", "Inventory.txt")
            inventory_items = [line.strip() for line in open(inv_path, 'r')]
        except Exception as ex:
            print(str(ex))
        if x == required_x and y == required_y and z == required_z:
            has_all = all(req in inventory_items for req in required_items)
            if has_all and required_items:
                self.win()
                return ""
            else:
                return "\n\nYou don't have all usable items for this room"
        else:
            try:
                usable_path = os.path.join("Text", "Room_descriptions", "Main", "floor_" + str(z), "y" + str(y) + "_x" + str(x), "Usable_Items.txt")
                if not os.path.exists(usable_path):
                    return "\n\nYou have no usable items for this room"
                lines = [line.strip() for line in open(usable_path, 'r')]
                if not lines:
                    return "\n\nYou have no usable items for this room"
                usable_items = [item.strip() for item in lines[0].split(',')]
                item_description = lines[1] if len(lines) > 1 else ""
                new_item = lines[2] if len(lines) > 2 else ""
                missing_items = [item for item in usable_items if item not in inventory_items]
                if not missing_items:
                    inventory_items = [item for item in inventory_items if item not in usable_items]
                    inv_path = os.path.join("Save", "Inventory.txt")
                    with open(inv_path, 'w') as f:
                        f.write("\n".join(inventory_items) + "\n" if inventory_items else "")
                    with open(inv_path, 'a') as f:
                        f.write(new_item + "\n")
                    hist_path = os.path.join("Save", "Inventory_history.txt")
                    with open(hist_path, 'a') as f:
                        f.write(new_item + "\n")
                    result = "Used " + ", ".join(usable_items) + ".\n\n " + item_description + "\n\nYou found:\n" + new_item
                else:
                    result = "You are missing one or more items"
            except Exception as ex:
                print(str(ex))
                result = "Error using items."
        return result

    def check_inventory_tutorial(self):
        required_items = []
        try:
            req_path = os.path.join("Tutorial", "Required_items.txt")
            if os.path.exists(req_path):
                required_items = [line.strip() for line in open(req_path, 'r') if line.strip()]
        except:
            pass
        inventory_items = []
        try:
            inv_path = os.path.join("Save", "Inventory.txt")
            if os.path.exists(inv_path):
                inventory_items = [line.strip() for line in open(inv_path, 'r')]
        except:
            pass
        return all(req in inventory_items for req in required_items)

    def game_over(self):
        self.clear_output()
        description = ""
        game_over_text = "GAME OVER"
        try:
            file_path = os.path.join("Text", "Stories", "Ending", "Game_over.txt")
            description = open(file_path, 'r').read()
        except:
            description = "Game over text not found."
        self.print_to_output(description)
        self.print_to_output("\n\n\n" + game_over_text)
        self.reset()
        self.print_to_output("\n\nPress ENTER to exit...")
        self.get_user_input()
        self.quit()

    def win(self):
        self.clear_output()
        description = ""
        win_text = "YOU WIN"
        try:
            file_path = os.path.join("Text", "Stories", "Ending", "Win.txt")
            description = open(file_path, 'r').read()
        except:
            description = "Win text not found."
        self.print_to_output(description)
        self.print_to_output("\n\n\n" + win_text)
        self.reset()
        self.print_to_output("\n\nPress ENTER to exit...")
        self.get_user_input()
        self.quit()

    def reset(self):
        try:
            with open(os.path.join("Save", "Location.txt"), 'w') as writer:
                writer.write("2")
        except Exception as ex:
            print(str(ex))
        try:
            with open(os.path.join("Save", "Inventory.txt"), 'w') as writer:
                writer.write("")
        except Exception as ex:
            print(str(ex))
        try:
            with open(os.path.join("Save", "Inventory_history.txt"), 'w') as writer:
                writer.write("")
        except Exception as ex:
            print(str(ex))
        default_health = "20"
        try:
            def_path = os.path.join("Finishing", "Default_health.txt")
            if os.path.exists(def_path):
                default_health = open(def_path, 'r').read().strip()
        except:
            pass
        try:
            with open(os.path.join("Save", "Health.txt"), 'w') as writer:
                writer.write(default_health)
        except Exception as ex:
            print(str(ex))

if __name__ == "__main__":
    app = MainForm()
    app.mainloop()