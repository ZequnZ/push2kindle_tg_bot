import telegram as tg
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler
from telegram.utils.request import Request
import yaml
import requests
import sys

from utils import email2kindle, epub2mobi




def main():

    # Load config file
    yaml_file = r"./config.yaml"
    with open(yaml_file) as file:
        configs = yaml.full_load(file)
    token = configs["token"]
    bot = tg.Bot(token=token)
    message_url = f"https://api.telegram.org/bot{token}/getupdates"
    file_url = f"https://api.telegram.org/bot{token}/getfiles?"
    my_id = configs["my_id"]
    msg_id = configs['msg_id']
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


    while True:
        try:
            # getUpdates = Request().post(message_url, data={"offset": -1, "limit": 1})[0]
            req = requests.post(message_url).json()
            latest = req['result'][-1]
        except tg.error.TimedOut:
            time.sleep(50)
        except KeyboardInterrupt:
            with open(yaml_file, 'w') as file:
                yaml.dump(configs,file)
                print('Successfully save the configs at keyboardinterrupt.')
                sys.exit()
        except:
            with open(yaml_file, 'w') as file:
                yaml.dump(configs,file)
                print('Successfully save the configs when something went wrong.')
                sys.exit()

        else:
            if latest['update_id']>msg_id:
                msg_id = latest['update_id']
                configs['msg_id'] = msg_id
                chat_id = latest['message']['from']['id']
                if 'text' in latest['message']:
                    msg = latest['message']['text']
                else:
                    msg = None
                
                print(latest)
                
                # When a file is sent:
                if 'document' in latest['message']:
                    if chat_id not in configs: # haven't bind email
                        bot.send_message(
                                    chat_id, "Havn't bind email yet! Use /bind to bind your email."
                                        )
                    else:

                        file_name = latest["message"]["document"]["file_name"]
                        file_id = latest["message"]["document"]["file_id"]
                        file_unique_id = latest["message"]["document"]["file_unique_id"]
                        file_size = latest["message"]["document"]["file_size"]
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
                                bot.send_message(chat_id, "Download Successfully!!!")

                                if file_format in trans_format:
                                    file_local_path = epub2mobi(file_local_path)
                                    bot.send_message(
                                        chat_id, "Converting epub file into mobi....."
                                    )

                                try:
                                    email2kindle(file_local_path, configs[chat_id])

                                except Exception as e:
                                    bot.send_message(chat_id, e)
                                else:
                                    bot.send_message(
                                        chat_id,
                                        "Congratulations!! Book has been sent to kindle successfully!",
                                    )
                        else:
                            bot.send_message(chat_id, "Unsupported file.")

                # Handle different msg
                if msg is not None:
                    if msg == '/start':
                        bot.send_message(
                                            chat_id, "Welcome to use Push2Kindle bot. Bind your email address with '/bind'" \
                                            + "then you can push your book files to kindle."
                                        )
                    
                    if msg == '/bind':
                        if chat_id not in configs:
                            bot.send_message(
                                            chat_id, "Type '/bind+youremailaddress' to bind your email"
                                            )
                        else:
                            bot.send_message(
                                            chat_id, f"Your email address is {configs[chat_id]}"
                                            )   
                    
                    if msg.startswith('/bind+'):
                        email = msg.split('+')[-1]
                        print(email)
                        if '@' not in email:
                            bot.send_message(
                                        chat_id, "Invalid emaill address"
                                            )
                        else:
                            configs[chat_id] = email
                            bot.send_message(
                                        chat_id, f"Successfully bind your emaill address: {email}"
                                            )
                
            else: 
                continue



if __name__ == "__main__":
    main()
