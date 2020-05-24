import telegram as tg
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler
from telegram.utils.request import Request
import yaml

from utils import email2kindle, epub2mobi

# Load config file
with open(r"./config.yaml") as file:
    configs = yaml.full_load(file)
token = configs["token"]
bot = tg.Bot(token=token)
message_url = f"https://api.telegram.org/bot{token}/getupdates"
file_url = f"https://api.telegram.org/bot{token}/getfiles?"
my_id = configs["my_id"]
supported_format = [
    "mobi",
    "azw",
    "doc",
    "docx",
    "html",
    "rtf",
    "txt",
    "jpg",
    "jpeg",
    "gif",
    "png",
    "bmp",
    "pdf",
]
trans_format = ["epub"]


def main():
    message_id = 0
    while True:
        try:
            getUpdates = Request().post(message_url, data={"offset": -1, "limit": 1})[0]
        except tg.error.TimedOut:
            time.sleep(50)
        else:
            if message_id != getUpdates["message"]["message_id"]:
                message_id = getUpdates["message"]["message_id"]
                chat_id = getUpdates["message"]["from"]["id"]
                print(getUpdates)
                m = getUpdates

                if "document" in getUpdates["message"]:

                    file_name = getUpdates["message"]["document"]["file_name"]
                    file_id = getUpdates["message"]["document"]["file_id"]
                    file_unique_id = getUpdates["message"]["document"]["file_unique_id"]
                    file_size = getUpdates["message"]["document"]["file_size"]
                    file_format = file_name.split(".")[-1]

                    if file_format in supported_format + trans_format:

                        try:
                            getFiles = tg.Bot.getFile(bot, file_id=file_id, timeout=120)
                        except tg.error.TimedOut:
                            bot.send_message(
                                chat_id, "Timeout happens when try to download!"
                            )
                        else:
                            file_path = getFiles["file_path"]
                            kindle_file = tg.File(
                                file_id=file_id,
                                bot=bot,
                                file_size=str(file_size),
                                file_path=file_path,
                                file_unique_id=file_unique_id,
                            )
                            file_local_path = "./files/" + file_name
                            kindle_file.download(custom_path=file_local_path)
                            bot.send_message(chat_id, "Download Success!!!")

                            if file_format in trans_format:
                                file_local_path = epub2mobi(file_local_path)
                                bot.send_message(
                                    chat_id, "Converting epub file into mobi....."
                                )

                            try:
                                email2kindle(file_local_path)
                                pass
                            except Exception as e:
                                bot.send_message(chat_id, e)
                            else:
                                bot.send_message(
                                    chat_id,
                                    "Congratulations!! Book has been sent to kindle successfully!",
                                )
                    else:
                        bot.send_message(chat_id, "Unsupported file.")


if __name__ == "__main__":
    main()
