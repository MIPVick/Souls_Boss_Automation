#Config Example

TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
# gotta do your own for this part, need to donwload ADB ( avaialable online) and setup telegram bot stuff 
# you have to setup ADB in blue stacks settings and you will get your device ID from it.
# in powershell you have to change the directory to \Downloads\platform-tools-latest-windows\platform-tools or wherever you have downloaded your platform tools
# then do .\adb connect {Device}. you can find the device id in the settings of bluestacks
ADB_PATH = r"C:\Users\vick\Downloads\platform-tools-latest-windows\platform-tools\adb.exe"
DEVICE = "PUT YOUR DEVICE ADDRESS HERE" 
THRESHOLD = 1267688491420           # dmg threshold for the run to count as good or bad run

# Telegram bot stuff ( this stuff on how to make your own bot can be found online I believe)
# once you make your own bot, you can access your token from it, and you can get chat_ID, by using the token and using this link
# https://api.telegram.org/bot{TOKEN}/sendMessage
TOKEN = "YOUR TOKEN DETAILS HERE"
CHAT_ID = "YOUR CHAT ID HERE"
LAST_UPDATE_ID = None