import board #type: ignore
import keypad #type: ignore
import json #type: ignore
import digitalio #type: ignore
import time
import usb_hid #type: ignore
from adafruit_hid.keyboard import Keyboard #type: ignore
from adafruit_hid.keycode import Keycode #type: ignore

import busio #type: ignore
import displayio #type: ignore
import adafruit_ssd1306 #type: ignore


displayio.release_displays()

i2c = busio.I2C(board.GP5, board.GP4)

display = adafruit_ssd1306.SSD1306_I2C(
    128,
    32,
    i2c,
    addr=0x3C
)

keyboard = Keyboard(usb_hid.devices)

matrix = keypad.KeyMatrix(
    row_pins=(board.GP3, board.GP6),
    column_pins=(board.GP0, board.GP1, board.GP2)
)

mode_button = digitalio.DigitalInOut(board.GP8)
mode_button.direction = digitalio.Direction.INPUT
mode_button.pull = digitalio.Pull.UP

def get():
    global data
    global modes
    global current_mode
    with open("/conf.json") as f:
        data = json.load(f)
    modes = list(data["Modes"].keys())
    if current_mode >= len(modes):
        current_mode = 0

current_mode = 0
get()

def display_mode():
    global current_mode

    display.fill(0)
    text = f"Mode: {modes[current_mode]}"
    x = (128 - len(text) * 6) // 2
    y = (32 - 8) // 2
    display.text(text, x, y, 1)
    display.show()

def switch_mode():
    global current_mode

    current_mode += 1

    if current_mode >= len(modes):
        current_mode = 0
    display_mode()


def send_key(key):
    KEY_ALIASES = {
        "CTRL": Keycode.CONTROL,
        "CONTROL": Keycode.CONTROL,
        "SHIFT": Keycode.SHIFT,
        "ALT": Keycode.ALT,
        "GUI": Keycode.GUI,
        "WINDOWS": Keycode.GUI,
        "WIN": Keycode.GUI,
        "ENTER": Keycode.ENTER,
        "RETURN": Keycode.RETURN,
        "ESC": Keycode.ESCAPE,
        "ESCAPE": Keycode.ESCAPE,
        "TAB": Keycode.TAB,
        "SPACE": Keycode.SPACE,
        "BACKSPACE": Keycode.BACKSPACE,
        "DELETE": Keycode.DELETE,
        "UP": Keycode.UP_ARROW,
        "DOWN": Keycode.DOWN_ARROW,
        "LEFT": Keycode.LEFT_ARROW,
        "RIGHT": Keycode.RIGHT_ARROW,
    }

    CHAR_KEYCODES = {
        "0": Keycode.ZERO, "1": Keycode.ONE, "2": Keycode.TWO, "3": Keycode.THREE,
        "4": Keycode.FOUR, "5": Keycode.FIVE, "6": Keycode.SIX, "7": Keycode.SEVEN,
        "8": Keycode.EIGHT, "9": Keycode.NINE, " ": Keycode.SPACE,
        "-": Keycode.MINUS, "=": Keycode.EQUALS, "[": Keycode.LEFT_BRACKET,
        "]": Keycode.RIGHT_BRACKET, "\\": Keycode.BACKSLASH, ";": Keycode.SEMICOLON,
        "'": Keycode.QUOTE, "`": Keycode.GRAVE_ACCENT, ",": Keycode.COMMA,
        ".": Keycode.PERIOD, "/": Keycode.FORWARD_SLASH,
    }

    SHIFT_SYMBOLS = {
        "!": Keycode.ONE, "@": Keycode.TWO, "#": Keycode.THREE, "$": Keycode.FOUR,
        "%": Keycode.FIVE, "^": Keycode.SIX, "&": Keycode.SEVEN, "*": Keycode.EIGHT,
        "(": Keycode.NINE, ")": Keycode.ZERO, "_": Keycode.MINUS, "+": Keycode.EQUALS,
        "{": Keycode.LEFT_BRACKET, "}": Keycode.RIGHT_BRACKET, "|": Keycode.BACKSLASH,
        ":": Keycode.SEMICOLON, "\"": Keycode.QUOTE, "~": Keycode.GRAVE_ACCENT,
        "<": Keycode.COMMA, ">": Keycode.PERIOD, "?": Keycode.FORWARD_SLASH,
    }

    def get_keycode(name):
        name = name.upper()

        if name in KEY_ALIASES:
            return KEY_ALIASES[name]

        return getattr(Keycode, name, None)

    def execute(info):
        key_type = info.get("type")
        main = info.get("main")

        if key_type == "macro":
            keycodes = []

            for key_name in main:
                keycode = get_keycode(key_name)

                if keycode is not None:
                    keycodes.append(keycode)

            if keycodes:
                keyboard.press(*keycodes)
                keyboard.release_all()

        elif key_type == "text":
            for char in main:
                if char in SHIFT_SYMBOLS:
                    keycode = SHIFT_SYMBOLS[char]
                    keyboard.press(Keycode.SHIFT)
                    keyboard.press(keycode)
                    keyboard.release(keycode)
                    keyboard.release(Keycode.SHIFT)
                elif char.isupper():
                    keycode = get_keycode(char)

                    if keycode is not None:
                        keyboard.press(Keycode.SHIFT)
                        keyboard.press(keycode)
                        keyboard.release(keycode)
                        keyboard.release(Keycode.SHIFT)
                elif char == "&":
                    keyboard.press(Keycode.SHIFT, Keycode.SIX)
                    keyboard.release_all()
                elif char in CHAR_KEYCODES:
                    keycode = CHAR_KEYCODES[char]
                    keyboard.press(keycode)
                    keyboard.release(keycode)
                else:
                    keycode = get_keycode(char)

                    if keycode is not None:
                        keyboard.press(keycode)
                        keyboard.release(keycode)

        elif key_type == "delay":
            time.sleep(main / 1000)

        elif key_type == "sequence":
            for action in main:
                execute(action)

    mode = modes[current_mode]
    info = data["Modes"][mode][str(key)]

    execute(info)

def recive_serial():
    import usb_cdc  # type: ignore

    if usb_cdc.data is None:
        return

    if usb_cdc.data.in_waiting:
        command = usb_cdc.data.readline().decode().strip()

        if command == "storage":
            with open("/conf.json", "r") as f:
                config = json.load(f)

            config["storage"] = True

            with open("/conf.json", "w") as f:
                json.dump(config, f)

        if command == "send":
            with open("/conf.json", "r") as f:
                data = f.read()

            usb_cdc.data.write(b"FILE_START\n")
            usb_cdc.data.write(data.encode())
            usb_cdc.data.write(b"\nFILE_END\n")

        if command == "get":
            new_config = ""

            while True:
                if usb_cdc.data.in_waiting:
                    line = usb_cdc.data.readline().decode()

                    if line.strip() == "<END>":
                        break

                    new_config += line

            with open("/conf.json", "w") as f:
                f.write(new_config)

            get()

display_mode()


last_button = True

while True:
    recive_serial()
    button = mode_button.value

    if last_button and not button:
        switch_mode()

    last_button = button

    event = matrix.events.get()

    if event and event.pressed:
        send_key(event.key_number)