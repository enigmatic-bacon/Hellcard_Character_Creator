import pyautogui
import click_positions
import time
import tkinter as tk
from tkinter import ttk
from image_processing import process_image, match_template, ocr
from dataclasses import dataclass
from click_positions import init_click_locations, init_global_positions

from pynput import keyboard
from mage import mage_commons, mage_rares, mage_starters
from rogue import rogue_commons, rogue_rares, rogue_starters
from warrior import warrior_commons, warrior_rares, warrior_starters


def on_press(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False


acceptable_rares = [
    "Chilly Blow",
    "Equilibrium",
    "Mend Wounds",
    "Rune of Ice",
    "Sweep",
    "Ascendance",
]
acceptable_commons = ["Cold Arm", "Swell", "Teleport"]


@dataclass
class CaptureArea:
    x: int
    y: int
    width: int
    height: int


def click(position, delay=0.0):
    pyautogui.moveTo(position.x, position.y)
    time.sleep(0.15)
    pyautogui.click()
    time.sleep(delay)


def capture(x, y, width, height, filename="screenshot.png"):
    """
    Captures a portion of the screen and saves it to a file.

    Parameters:
    x, y (int): Coordinates for the top-left corner of the capture area.
    width, height (int): Dimensions of the capture area.
    filename (str): Name of the file to save the screenshot.

    Returns:
    str: Path to the saved screenshot file.
    """
    try:
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot.save(filename)
        return filename
    except Exception as e:
        print(f"Error during screen capture: {e}")
        return None


def create_character(character):
    click_positions.set_character(character)
    for position, delay in click_positions.create_char_positions:
        click(position, delay)


def retire_character():
    for position, delay in click_positions.retire_char_positions:
        click(position, delay)


def get_cards():
    card_area = CaptureArea(x=3810, y=400, width=300, height=550)
    capture(card_area.x, card_area.y, card_area.width, card_area.height, "cards.png")
    process_image("cards.png")
    extracted_text = ocr("result.png")
    cards = [line.strip() for line in extracted_text.split("\n") if line.strip()]
    return cards


def get_amounts():
    amount_area = CaptureArea(x=4290, y=410, width=50, height=420)
    capture(
        amount_area.x,
        amount_area.y,
        amount_area.width,
        amount_area.height,
        "amount.png",
    )
    process_image("amount.png", "result_amount.png")
    extracted_text = ocr("result_amount.png")
    extracted_text = extracted_text.replace("l", "1")
    amounts = [
        int("".join(filter(str.isdigit, line)))
        for line in extracted_text.split("\n")
        if line.strip()
    ]
    return amounts


def get_num_artifacts():
    capture(x=2870, y=160, width=655, height=1130, filename="map.png")
    return len(match_template("map.png", "icons/treasure_icon.png"))


def validate_cards(cards_dict, acceptable_rares, acceptable_commons):
    """
    Validates a dictionary of cards based on given criteria.

    Parameters:
    cards_dict (dict): Dictionary with card names as keys and their counts as values.
    acceptable_rares (list): List of strings representing acceptable rare cards.
    acceptable_commons (list): List of strings representing acceptable common cards.

    Returns:
    bool: True if the list contains at least one acceptable rare and at least two acceptable commons, False otherwise.
    """
    # Check for at least one acceptable rare
    has_acceptable_rare = any(cards_dict.get(card, 0) > 0 for card in acceptable_rares)

    # Sum the counts of acceptable commons
    common_count = sum(cards_dict.get(card, 0) for card in acceptable_commons)

    # Special case for "Whirlwind"
    if "Wind Blast" in cards_dict and int(cards_dict["Wind Blast"]) >= 3:
        return True

    # Check if there are at least two acceptable commons
    has_two_acceptable_commons = common_count >= 2

    return has_acceptable_rare and has_two_acceptable_commons


def main():
    def start_script():
        try:
            num_iterations = int(iterations_entry.get())
        except ValueError:
            print("Please enter a valid number")
            return

        for _ in range(num_iterations):
            create_character(char_to_create)
            click(click_positions.cards_and_details, 0.4)
            cards = get_cards()
            amounts = get_amounts()
            cards_with_amounts = dict(zip(cards, amounts))
            num_artifact = get_num_artifacts()
            click(click_positions.back_cards_and_detail, 0.4)
            print(cards_with_amounts)
            print(num_artifact)
            cards_are_good = validate_cards(
                cards_with_amounts, acceptable_rares, acceptable_commons
            )
            if not cards_are_good and num_artifact < 6:
                retire_character()

    char_to_create = "warrior"

    def select_icon(selected_icon):
        global char_to_create
        char_to_create = selected_icon
        for icon in icons_color.keys():
            if icon == selected_icon:
                buttons[icon]["image"] = icons_color[icon]  # Set to color
                buttons[icon].config(relief="sunken")  # Indicate selection
            else:
                buttons[icon]["image"] = icons_grey[icon]  # Set to grayscale
                buttons[icon].config(relief="raised")  # Reset other buttons

        commons_box.delete(0, tk.END)
        rares_box.delete(0, tk.END)
        starter_box.delete(0, tk.END)
        if selected_icon == "warrior":
            for i, card in enumerate(warrior_commons):
                commons_box.insert(i, card)
            for i, card in enumerate(warrior_rares):
                rares_box.insert(i, card)
            for i, card in enumerate(warrior_starters):
                starter_box.insert(i, card)
        elif selected_icon == "rogue":
            for i, card in enumerate(rogue_commons):
                commons_box.insert(i, card)
            for i, card in enumerate(rogue_rares):
                rares_box.insert(i, card)
            for i, card in enumerate(rogue_starters):
                starter_box.insert(i, card)
        elif selected_icon == "mage":
            for i, card in enumerate(mage_commons):
                commons_box.insert(i, card)
            for i, card in enumerate(mage_rares):
                rares_box.insert(i, card)
            for i, card in enumerate(mage_starters):
                starter_box.insert(i, card)
        text_box.delete("1.0", tk.END)  # Clear the textbox
        text_box.insert(
            tk.END, f"Selected icon: {selected_icon}"
        )  # Insert the selected icon name

    def on_validate(P):
        # Allow only numeric input
        return P.isdigit() or P == ""

    def calibrate():
        init_click_locations()
        init_global_positions()
        click(click_positions.back_cards_and_detail)

    # Create the main window
    root = tk.Tk()
    root.title("Automation Control")
    # Create a start button
    calibrate_button = tk.Button(root, text="Calibrate", command=calibrate)
    calibrate_button.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

    # Register the validation command
    validate_command = (root.register(on_validate), "%P")

    # Create a label for the text entry
    label = tk.Label(root, text="# of Characters")
    label.grid(row=1, column=0, padx=10, pady=10)

    # Create a text entry for iterations
    iterations_entry = tk.Entry(root, validate="key", validatecommand=validate_command)
    iterations_entry.grid(row=1, column=1, padx=10, pady=10)

    def initialize_buttons(root):
        icons_color = {
            "warrior": tk.PhotoImage(file="icons/warrior.png"),
            "rogue": tk.PhotoImage(file="icons/rogue.png"),
            "mage": tk.PhotoImage(file="icons/mage.png"),
        }
        icons_grey = {
            "warrior": tk.PhotoImage(file="icons/warrior_grayscale.png"),
            "rogue": tk.PhotoImage(file="icons/rogue_grayscale.png"),
            "mage": tk.PhotoImage(file="icons/mage_grayscale.png"),
        }

        buttons = {}
        for icon_key in icons_color.keys():
            button = tk.Button(
                root,
                image=icons_color[icon_key],
                command=lambda key=icon_key: select_icon(key),
            )
            button.grid(row=2, column=len(buttons), padx=10, pady=10)
            buttons[icon_key] = button

        return buttons, icons_color, icons_grey

    buttons, icons_color, icons_grey = initialize_buttons(root)

    # Create a start button
    start_button = tk.Button(root, text="Start", command=start_script)
    start_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    # Create a text box for displaying text
    text_box = tk.Text(root, height=10, width=50)
    text_box.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
    text_box.insert(tk.END, char_to_create)

    # Card selection
    notebook = ttk.Notebook(root)
    notebook.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    # Function to create Listbox inside a frame
    def create_listbox(frame):
        listbox = tk.Listbox(frame, selectmode="multiple", font=("Segoe UI", 13))
        listbox.pack(expand=True, fill="both")
        return listbox

    # Create a frame for commons and add it as a tab
    commons_frame = ttk.Frame(notebook)
    notebook.add(commons_frame, text="Commons")
    commons_box = create_listbox(commons_frame)
    # Create a frame for rares and add it as a tab
    rares_frame = ttk.Frame(notebook)
    notebook.add(rares_frame, text="Rares")
    rares_box = create_listbox(rares_frame)
    # Create a frame for starters and add it as a tab
    starter_frames = ttk.Frame(notebook)
    notebook.add(starter_frames, text="Starters")
    starter_box = create_listbox(starter_frames)

    def include():
        selected = []
        for i in commons_box.curselection():
            selected.append(commons_box.get(i))
            commons_box.selection_clear(i)
        for i in rares_box.curselection():
            selected.append(rares_box.get(i))
            rares_box.selection_clear(i)
        for i in starter_box.curselection():
            selected.append(starter_box.get(i))
            starter_box.selection_clear(i)
        text_box.delete("1.0", tk.END)
        for card in selected:
            text_box.insert(tk.END, card)
        pass

    # TODO allow for exclusions of specific cards
    def exclude():
        pass

    # Create the 'Include' button (green) and position it next to the notebook
    include_button = tk.Button(
        root,
        text="Include",
        font=("Segoe UI", 13),
        width=15,
        command=include,
        bg="green",
    )
    include_button.grid(
        row=8, column=2, padx=10, pady=120, sticky="N"
    )  # Aligned to the top

    # Create the 'Exclude' button (red) and position it below the 'Include' button
    exclude_button = tk.Button(
        root, text="Exclude", font=("Segoe UI", 13), width=15, command=exclude, bg="red"
    )
    exclude_button.grid(
        row=8, column=2, padx=10, pady=160, sticky="N"
    )  # Below 'Include', aligned to the top

    # Default to warrior
    select_icon("warrior")

    # Update idletasks before setting the window size
    root.update_idletasks()

    # Set the window size to the minimum required to display all widgets
    root.geometry(f"{root.winfo_reqwidth()}x{root.winfo_reqheight()}")

    # Disable resizing
    root.resizable(False, False)

    # Run the application
    root.mainloop()


if __name__ == "__main__":
    main()
