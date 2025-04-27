import requests
import json
import os
import threading

from dotenv import load_dotenv
from AllQuran import AllQuran

load_dotenv()
all_quran = AllQuran()

BOT_TOKEN = os.environ.get('BOT_TOKEN')

def ask_question(prompt):
    answer = all_quran.answer(prompt)
    return answer


def ask_image(prompt):
    response = requests.post(
        'https://api.openai.com/v1/images/generations',
        headers={'Authorization': f'Bearer {API_KEY}'},
        json={'model': MODEL, 'prompt': prompt, 'temperature': 0.4, 'max_tokens': 300}
    )
    response_text = json.loads(response.text)
    return response_text['data'][0]['url']


def telegram_send_message(bot_message, chat_id, msg_id):
    data = {'chat_id': chat_id, 'text': bot_message, 'reply_to_message_id': msg_id}
    response = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json=data,
    )
    return response.json()


def telegram_send_picture(image_url, group_id, msg_id):
    data = {'chat_id': group_id, 'photo': image_url, 'reply_to_message_id': msg_id}
    response = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
            json=data,
    )
    return response.json()


def Chatbot():
    cwd = os.getcwd()
    filename = cwd + '/chatgpt.txt'
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("1")
    else:
        print("File Exists")

    with open(filename) as f:
        last_update = f.read()

    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update}'
    response = requests.get(url)
    data = json.loads(response.content)

    for result in data['result']:
        try:
            if float(result['update_id']) > float(last_update):
                if not result['message']['from']['is_bot']:
                    last_update = str(int(result['update_id']))


                    msg_id = str(int(result['message']['message_id']))

                    chat_id = str(result['message']['chat']['id'])


                    if '/img' in result['message']['text']:
                        prompt = result['message']['text'].replace("/img", "")
                        bot_response = ask_image(prompt)
                        print(telegram_send_image(bot_response, chat_id, msg_id))
                    if True :
                        print(result['message']['text'], chat_id, msg_id)
                        prompt = result['message']['text'].replace("@ask_chatgptbot", "")
                        bot_response = ask_question(prompt).strip()
                        print(bot_response)
                        print(telegram_send_message(bot_response, chat_id, msg_id))
                    if 'reply_to_message' in result['message']:
                        if result['message']['reply_to_message']['from']['is_bot']:
                            prompt = result['message']['text']
                            bot_response = ask_question(f"{prompt}")
                            print(telegram_send_message(bot_response, chat_id, msg_id))
        except Exception as e:
            print(e)
    
    with open(filename, 'w') as f:
        f.write(last_update)
    
    return "done"


def main():
    timer_time = 5
    Chatbot()

    threading.Timer(timer_time, main).start()

if __name__=='__main__':
    main()

