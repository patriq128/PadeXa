import storage #type: ignore
import usb_cdc #type: ignore
import json

with open("/conf.json") as f:
    data = json.load(f)

if not data["storage"]:
    storage.disable_usb_drive()

usb_cdc.enable()
