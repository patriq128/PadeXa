import serial
import serial.tools.list_ports
import json
import sys

def connect_device():
    global ser
    PICO_VID = "2E8A"

    def find_pico():
        for p in serial.tools.list_ports.comports():
            if p.vid is not None and hex(p.vid).upper().replace("0X", "") == PICO_VID:
                return p.device
        return None

    port = find_pico()

    if not port:
        print("\033[31mDevice not found\033[0m")
        exit()

    ser = serial.Serial(port, 115200)
    print("\033[32mConnected:", port, "\033[0m")

class Conf:
    def load_device(self):
        ser.write(b"send\n")

        data = []

        while True:
            line = ser.readline().decode().strip()

            if line == "FILE_START":
                continue

            if line == "FILE_END":
                break
            if line:
                data.append(line)

        config = json.loads("\n".join(data))

        with open("device_conf.json", "w") as f:
            json.dump(config, f, indent=4)

    def load(self):
        with open("device_conf.json", "r") as f:
            data = json.load(f)

        return data

    def save(self, data):
        with open("device_conf.json", "w") as f:
            json.dump(data, f, indent=4)

        with open("device_conf.json", "rb") as f:
            data = f.read()
        ser.write(b"get\n")
        ser.write(data)
        ser.write(b"\n<END>\n")


conf = Conf()
mode_now = False


def show(): 
    data = conf.load() 
    global mode_now 
    print("\033[2J\033[H", end="")
    if mode_now: 
        print(f"Mode: \033[32m{mode_now}\033[0m") 
    print("""
┌───────────┐
│[────]  ○  │
│           │
│[2] [1] [0]│
│[5] [4] [3]│
└───────────┘
""") 
    if mode_now: 
        print("Keys:")
        for i in range(6): 
            print(f"[{i}] {data['Modes'][mode_now][str(i)]}")
    else:
        print("Modes:")
        for i in list(data["Modes"].keys()):
            print("\033[32m", i, "\033[0m")


def commands(command):
    def sequence():
        sequence = []

        while True:
            action = input("sequence> ").strip()

            if action == "":
                break

            parts = action.split(" ", 1)

            if len(parts) < 2:
                continue

            key_type = parts[0]
            value = parts[1].strip()

            if key_type == "text":
                sequence.append({
                    "type": "text",
                    "main": value
                })

            elif key_type == "macro":
                value = [x.strip() for x in value.split(",")]

                sequence.append({
                    "type": "macro",
                    "main": value
                })

            elif key_type == "delay":
                try:
                    value = int(value)

                    sequence.append({
                        "type": "delay",
                        "main": value
                    })

                except ValueError:
                    print("\033[31mDelay must be a number.\033[0m")

            else:
                print(f"\033[31mUnknown sequence command: {key_type}\033[0m")

        return sequence

    global mode_now

    if command == "list modes":
        data = conf.load()

        for i in list(data["Modes"].keys()):
            print(i)

    elif command.startswith("go"):
        data = conf.load()
        mode = command.split()

        if len(mode) < 2:
            return

        mode = mode[1]

        if mode in data["Modes"]:
            mode_now = mode
            show()
        else:
            print(f"\033[31mMode {mode} doesn't exists\033[0m")

    elif command == "show":
        show()

    elif command.startswith("k"):
        data = conf.load()

        parts = command[1:].split(" ", 2)

        if len(parts) < 3:
            return

        try:
            number = int(parts[0])
        except ValueError:
            return

        key_type = parts[1]
        value = parts[2].strip()

        if key_type == "text":
            if value == "remove":
                value = ""

        elif key_type == "macro":
            if value == "remove":
                value = []
            else:
                value = [x.strip() for x in value.split(",")]

        elif key_type == "sequence":
            if value == "remove":
                value = []
            else:
                value = sequence()

        else:
            print(f"\033[31mUnknown key type: {key_type}\033[0m")
            return

        data["Modes"][mode_now][str(number)] = {
            "type": key_type,
            "main": value
        }

        conf.save(data)
        show()
        
    elif command.startswith("remove"):
        data = conf.load()
        mode = command.split()

        if len(mode) < 2:
            return
        mode = mode[1]

        if mode in data["Modes"]:
            del data["Modes"][mode]
        else:
            print(f"\033[31mMode {mode} doesn't exists\033[0m")

        conf.save(data)
        show()
    elif command.startswith("new"):
        data = conf.load()
        mode = command.split()

        if len(mode) < 2:
            return
        mode = mode[1]

        if not mode in data["Modes"]:
            data["Modes"][mode] = {
                "0": {},
                "1": {},
                "2": {},
                "3": {},
                "4": {},
                "5": {}
            }
        else:
            print(f"\033[31mMode {mode} already exists\033[0m")
            
        conf.save(data)
        show()

    elif command.startswith("rename"):
        data = conf.load()
        mode = command.split()

        if len(mode) < 3:
            return
        first = mode[1]
        second = mode[2]

        if first in data["Modes"]:
            data["Modes"][second] = data["Modes"][first]
            del data["Modes"][first]
        else:
            print(f"\033[31mMode {first} doesn't exists\033[0m")

        conf.save(data)
        show()

def main():
    global mode_now
    if "--dev" in sys.argv:
        print("\033[35mDev mode activated!\033[0m")
    connect_device()
    mode_now = False
    conf.load_device()
    show()
    while True:
        thing = input("\033[34m>> \033[0m")
        commands(thing)


if __name__ == "__main__":
    main()