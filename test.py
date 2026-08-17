import tkinter as tk

root = tk.Tk()
root.title("Hackpad Key Recorder")
root.geometry("500x250")

pressed = set()
recorded = []


# Prevod názvov klávesov
KEY_NAMES = {
    "Control_L": "Ctrl",
    "Control_R": "Ctrl",
    "Shift_L": "Shift",
    "Shift_R": "Shift",
    "Alt_L": "Alt",
    "Alt_R": "Alt",
    "Super_L": "Win",
    "Super_R": "Win",
    "Return": "Enter",
    "Escape": "Esc",
    "space": "Space",
    "BackSpace": "Backspace",
    "Tab": "Tab",
}


def get_key_name(event):
    return KEY_NAMES.get(event.keysym, event.keysym)


def key_pressed(event):
    key = get_key_name(event)

    # Ignoruj opakované eventy pri držaní klávesu
    if key not in pressed:
        pressed.add(key)

        if key not in recorded:
            recorded.append(key)

        update_label()


def key_released(event):
    key = get_key_name(event)

    pressed.discard(key)

    # Všetky klávesy boli pustene
    if not pressed and recorded:
        combination = " + ".join(recorded)

        print("Detected:", combination)

        result_label.config(
            text=combination
        )

        recorded.clear()


def update_label():
    if recorded:
        result_label.config(
            text=" + ".join(recorded)
        )


# Nadpis
title = tk.Label(
    root,
    text="Press a key combination",
    font=("Arial", 18)
)

title.pack(pady=30)


# Aktuálna kombinácia
result_label = tk.Label(
    root,
    text="Waiting...",
    font=("Arial", 20)
)

result_label.pack(pady=20)


# Bind kláves
root.bind("<KeyPress>", key_pressed)
root.bind("<KeyRelease>", key_released)

root.mainloop()