import requests
import json

with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
group_id_telegram = config['group_id_telegram']
telegram_bot_token = config['telegram_bot_token']

def send_telegram(message):

    # The Telegram Bot API endpoint URL
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
    
    # Parameters for the message
    params = {
        'chat_id': group_id_telegram,
        'text': message,
        'disable_web_page_preview': True,
        'parse_mode': 'Markdown'
    }
    
    # Send the message
    response = requests.post(url, json=params)

    return response

if __name__ == "__main__":
    message = f'My favorite _search_ *engine* is [Duck Duck Go](https://duckduckgo.com)'
    send_telegram(message)