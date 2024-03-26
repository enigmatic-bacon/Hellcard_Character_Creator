import pyautogui
from dataclasses import dataclass
from image_processing import match_template
from PIL import Image


@dataclass
class Rectangle:
    width: int
    height: int
    x: int
    y: int

    def center(self):
        # Calculate and return the center coordinates
        return self.x + self.width // 2, self.y + self.height // 2


click_locations = {}


def init_click_locations():
    screenshot = pyautogui.screenshot()
    screenshot.save("debug/screenshot.png")
    icon_size = WidthHeight(*Image.open("icons/warrior.png").size)

    # Get the location of the warrior icon with respects to the whole screen
    warrior_loc = match_template("debug/screenshot.png", "icons/warrior.png", True, 0.9)
    click_locations["warrior"] = Rectangle(
        icon_size.w, icon_size.h, warrior_loc[0][0], warrior_loc[0][1]
    )

    # Searching the whole screen takes time, so limit the search space using the location of warrior as a guide
    img = Image.open("debug/screenshot.png")
    # Define the coordinates and size of the desired region
    x, y = warrior_loc[0][0], warrior_loc[0][1]
    # Crop the image
    cropped_img = img.crop((x, y, x + icon_size.w * 4, y + icon_size.h))
    # Save the cropped image
    cropped_img.save("debug/class_select.png")

    # Search the cropped image for the rogue
    rogue_loc = match_template("debug/class_select.png", "icons/rogue.png", True, 0.9)
    click_locations["rogue"] = Rectangle(
        icon_size.w,
        icon_size.h,
        click_locations["warrior"].x + rogue_loc[0][0],
        click_locations["warrior"].y + rogue_loc[0][1],
    )

    # Distance between warrior and rogue will be the same as mage to rogue
    distance = click_locations["rogue"].x - click_locations["warrior"].x
    click_locations["mage"] = Rectangle(
        icon_size.w,
        icon_size.h,
        click_locations["rogue"].x + distance,
        click_locations["rogue"].y,
    )


def set_character(char_name):
    create_char_positions[1] = (
        ClickPosition(*click_locations[char_name].center()),
        0.2,
    )


def init_global_positions():
    global new_char, char_icon, torment, preset_torment, confirm_torment, veteran_pin, create
    global create_char_positions, retire, confirm_retire, cards_and_details, back_cards_and_detail
    global retire_char_positions
    new_char = ClickPosition(2350, 1290)
    char_icon = ClickPosition(*click_locations["mage"].center())
    torment = ClickPosition(4071, 864)
    preset_torment = ClickPosition(2292, 621)
    confirm_torment = ClickPosition(3432, 1305)
    veteran_pin = ClickPosition(3908, 1217)
    create = ClickPosition(3193, 1493)
    create_char_positions = [
        (new_char, 0.5),
        (char_icon, 0.2),
        (veteran_pin, 0.2),
        (torment, 0.5),
        (preset_torment, 0.2),
        (confirm_torment, 0.8),
        (create, 0.5),
    ]

    retire = ClickPosition(4060, 1290)
    confirm_retire = ClickPosition(3379, 921)
    retire_char_positions = [
        (retire, 0.5),
        (confirm_retire, 0.5),
    ]

    cards_and_details = ClickPosition(4060, 1130)
    back_cards_and_detail = ClickPosition(2100, 70)

    # Initialize global positions based on click_locations
    # Example (update according to your actual logic and keys in click_locations):
    # mage_center = click_locations["mage"].center()
    # mage = ClickPosition(*mage_center)


@dataclass
class ClickPosition:
    x: int
    y: int


@dataclass
class WidthHeight:
    w: int
    h: int
