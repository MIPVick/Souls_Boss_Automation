import subprocess
from PIL import Image
import pytesseract
import time
from plyer import notification
import winsound, requests
from config import *

# need to download Tesseract-OCR and paste the file location here
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
LAST_UPDATE_ID = 0

# variables
run_counter = 1

def connect_adb():
    subprocess.run([
        ADB_PATH,
        "connect",
        DEVICE
    ])
    print("ADB Connected")

#sending message to telegram

# packages your message such as dmg, round and screenshot and sends it to your bot
def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

# sends the captrued screenshot to the telegram
def send_telegram_photo(photo_path, caption=""):

    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    with open(photo_path, "rb") as photo:

        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": caption
            },
            files={
                "photo": photo
            }
        )


# simple stuff, gets the latest message from telegram 
def get_latest_message():

    global LAST_UPDATE_ID

    url = (
        f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        f"?offset={LAST_UPDATE_ID + 1}"
    )

    response = requests.get(url)

    data = response.json()

    results = data["result"]

    if not results:
        return None

    latest = results[-1]

    LAST_UPDATE_ID = latest["update_id"]

    try:
        return latest["message"]["text"].lower()

    except:
        return None

def clear_old_updates():
    global LAST_UPDATE_ID
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url)
    data = response.json()
    results = data["result"]

    if results:
        LAST_UPDATE_ID = results[-1]["update_id"]
        print("Old Telegram updates cleared")

# fucntion used to accept commands send from telegram ( base level for now)
def wait_for_command():

    print("Waiting for command...")

    while True:

        command = get_latest_message()

        if command in ["continue", "restart", "stop"]:

            print(f"Received: {command}")

            return command

        time.sleep(2)

# Saves screenshot inside emulator (ADB stuff)
def capture_screenshot():

    subprocess.run([
        ADB_PATH,
        "-s",
        DEVICE,
        "shell",
        "screencap",
        "-p",
        "/sdcard/screen.png"
    ])

    subprocess.run([
        ADB_PATH,
        "-s",
        DEVICE,
        "pull",
        "/sdcard/screen.png",
        "screen.png"
    ])
    print("Screenshot Captured")


# you can directly tap using ADB, you can get the respective coordinates easily by opening the captured scrrenshot in paint and hovering -
# - over where you want the tap to happen 
def tap(x, y):

    subprocess.run([
        ADB_PATH,
        "-s",
        DEVICE,
        "shell",
        "input",
        "tap",
        str(x),
        str(y)
    ])

# positions of the respective buttons for my resolution ( might be different for you)
def restart_run():

    # Restart
    tap(*RESTART_BUTTON)
    time.sleep(1)

    # Start
    tap(*START_BUTTON)
    time.sleep(1)

    print("Run restarted!")

def pause_run():
    # Pause
    tap(*PAUSE_BUTTON)
    print("Run Paused")

def start_run():
    #starting the run
    tap(*START_BUTTON)
    print("Run started")

def continue_run():

    tap(*CONTINUE_BUTTON)

    time.sleep(1)

    print("Run continued!")

# captures part of the screenshot where I have my round and dmg values and use OCR to read them ( it gets fucked up when reading round values over 10)
def read_values():

    img = Image.open("screen.png")

    round_crop = img.crop(ROUND_CROP)
    damage_crop = img.crop(DAMAGE_CROP)

    round_crop.save("round_crop.png")
    damage_crop.save("damage_crop.png")

    round_config = '--psm 10 -c tessedit_char_whitelist=0123456789'
    damage_config = '--psm 7 -c tessedit_char_whitelist=0123456789,/'

    round_text = pytesseract.image_to_string(
        round_crop,
        config=round_config
    )

    damage_text = pytesseract.image_to_string(
        damage_crop,
        config=damage_config
    )

    round_text = round_text.strip()
    # Fixing common OCR mistakes (fuck me)
    CORRECTIONS = {
        "70": "10",
        "71": "11",
        "72": "12",
        "73": "13",
        "74": "14",
        "75": "15",
    }

    round_text = CORRECTIONS.get(round_text, round_text)

    damage_text = damage_text.strip()

    # making sure we only keep values before slash
    damage_text = damage_text.split("/")[0]

    # Remove commas
    damage_text = damage_text.replace(",", "")

    # Convert safely
    try:
        round_number = int(round_text)
    except:
        round_number = -1

    try:
        damage_number = int(damage_text)
    except:
        damage_number = -1

    #print("Detected Round:", round_number)
    #print("Detected Damage:", damage_number)
    return round_number, damage_number

# Connecting to Bluestacks through ADB
connect_adb()
clear_old_updates()

tap(*START_BUTTON)
time.sleep(1)

tap(*START_BUTTON)

while True:

    restart_run()

    time.sleep(25)

    pause_run()
    time.sleep(0.25)

    capture_screenshot()

    round_number, damage_number = read_values()

    print("Round:", round_number)
    print(f"Damage: {damage_number:,}")
    print("Run Number = ", run_counter)

    if round_number == -1:
        message = message = (
            f"Run Ruined\n"
            f"Round: {round_number}\n"
            f"Damage: {damage_number:,}\n"
            f"Run Number: {run_counter} ",
        )
        send_telegram_message(message)
        break

    if damage_number >= THRESHOLD:

        message = (
            f"GOOD RUN FOUND\n"
            f"Round: {round_number}\n"
            f"Damage: {damage_number:,}\n"
            f"Run Number: {run_counter} ",
        )

        send_telegram_message(message)

        send_telegram_photo(
            "screen.png",
            caption="Current paused run"
        )

        command = wait_for_command()

        if command == "continue":

            continue_run()

            break

        elif command == "restart":

            restart_run()

            continue

        elif command == "stop":

            print("Bot stopped by user.")

            break
    else:
        run_counter += 1