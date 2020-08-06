import os
import json
import time
import pickle
import requests


TOKEN = '<insert-your-telegram-bot-token>'
URL = f'https://api.telegram.org/bot{TOKEN}/'
CMD = [
    '/start', '/ccc', '/search', '/help',
    '/start@catechismbot', '/ccc@catechismbot',
    '/search@catechismbot', '/help@catechismbot',
]
LOGGER_PATH = '/log/'
CCC_PATH = '/bot/catechism.pickle'
with open(CCC_PATH, 'rb') as in_file:
    CCC = pickle.load(in_file)
CCC_keys = CCC.keys()


def process(payload):
    msg_type = get_type(payload)
    if msg_type == 'MSG_TEXT':
        chat_id = payload['message']['chat']['id']
        first_name = payload['message']['from']['first_name']
        text = payload['message']['text']
        cmd, code, keywords = extract_text(text)
        msg_text_proc(chat_id, first_name, cmd, code, keywords)

    elif msg_type == 'MSG_ENTITIES':
        chat_id = payload['message']['chat']['id']
        first_name = payload['message']['from']['first_name']
        text = payload['message']['text']
        cmd, code, keywords = extract_text(text)
        msg_text_proc(chat_id, first_name, cmd, code, keywords)
    
    elif msg_type == 'EDITED_MSG':
        chat_id = payload['edited_message']['chat']['id']
        first_name = payload['edited_message']['from']['first_name']
        text = payload['edited_message']['text']
        cmd, code, keywords = extract_text(text)
        msg_text_proc(chat_id, first_name, cmd, code, keywords)

    else:
        pass

def search(keywords):
    if keywords == None:
        return None
    else:
        target_keys = CCC_keys
        article_num = []
        keywords = [kw.upper() for kw in keywords]
        for kw in keywords:
            for ck in target_keys:
                if kw in CCC[ck][0].upper():
                    article_num.append(ck)
            target_keys = article_num
            article_num = []
        return target_keys


def logger(payload):
    with open(LOGGER_PATH, 'a') as out_file:
        out_file.write(f'{str(payload)}, {get_type(get_json(payload))}, {time.asctime()}\n')


def is_int(s):
    try:
        int(s)
        return s
    except:
        return False


def get_json(payload):
    js = json.loads(payload)
    return js


def catechise(code):
    passage = f'*CCC {code}*\t{CCC[code][0]}'
    return passage


def send_message(text, chat_id):
    url = URL + f'sendMessage?text={text}&chat_id={chat_id}&parse_mode=Markdown'
    requests.get(url)


def send_invalid(chat_id):
    send_message('Invalid command! Seek /help', chat_id)


def request_keywords(chat_id):
    send_message('Please supplement command with keyword(s)!', chat_id)


def request_reference(chat_id):
    send_message('Please supplement command with an article number!', chat_id)


def send_limit(chat_id):
    send_message(f'There are only 2865 articles in the Catechism of the Catholic Church.', chat_id)


def send_search_results(search_results, num_results, chat_id):
    send_message(f"The following {num_results} articles contain your search keyword(s):\n\n{search_results}", chat_id)


def send_help(first_name, chat_id):
    send_message(f'Hi {first_name}! Please enter one of the following commands:\n\nDirect message:\n/ccc <number>\n/search <keyword>\n\nExamples:\n/ccc 1639\n/search apostle Paul', chat_id)


def get_type(payload):
    if 'message' in payload.keys():
        if 'reply_to_message' in payload['message'].keys():
            payload_type = 'MSG_RE'
        elif 'forward_from' in payload['message'].keys():
            if 'title' in payload['message']['forward_from'].keys():
                payload_type = 'FWD_CHANNEL_MSG'
            elif 'first_name' in payload['message']['forward_from'].keys():
                payload_type = 'FWD_MSG'
        elif 'entities' in payload['message'].keys():
            payload_type = 'MSG_ENTITIES'
        elif 'audio' in payload['message'].keys():
            payload_type = 'MSG_AUDIO'
        elif 'document' in payload['message'].keys():
            payload_type = 'MSG_DOC'
        elif 'voice' in payload['message'].keys():
            payload_type = 'VOICE_MSG'
        elif 'text' in payload['message'].keys():
            payload_type = 'MSG_TEXT'
        else:
            payload_type = 'IGNORE'
    
    elif 'edited_message' in payload.keys():
        payload_type = 'EDITED_MSG'
    
    elif 'inline_query' in payload.keys():
        payload_type = 'INLINE_QUERY'
    
    elif 'callback_query' in payload.keys():
        payload_type = 'CALLBACK_QUERY'
    
    elif 'chosen_inline_result' in payload.keys():
        payload_type = 'CHOSEN_QUERY'
    
    return payload_type


def extract_text(text):
    text = text.split()
    if len(text) >= 2:
        if text[0] in CMD:
            cmd = text[0]
            if is_int(text[1]):
                code = text[1]
                keywords = None
            else:
                code = None
                keywords = text[1:]
        else:
            cmd = None
            code = None
            keywords = None
    
    else:
        if text[0] in CMD:
            cmd = text[0]
        else:
            cmd = None
        code = None
        keywords = None
    return cmd, code, keywords


def msg_text_proc(chat_id, first_name, cmd, code, keywords):
    if cmd == '/start' or cmd == '/start@catechismbot':
        send_message('Welcome to Catechism Bot!', chat_id)
    
    elif cmd == '/ccc' or cmd == '/ccc@catechismbot':
        if is_int(code):
            if int(code) > 0 and int(code) <= 2865:
                send_message(catechise(code), chat_id)
            elif int(code) > 2865:
                send_limit(chat_id)
            elif int(code) < 0:
                send_invalid(chat_id)
        else:
            request_reference(chat_id)
    
    elif cmd == '/search' or cmd == '/search@catechismbot':
        if keywords == None:
            request_keywords(chat_id)
        else:
            search_results = search(keywords)
            num_results = len(search_results)
            search_results = '   '.join(search_results)
            send_search_results(search_results, num_results, chat_id)
    
    elif cmd == '/help' or cmd == '/help@catechismbot':
        send_help(first_name, chat_id)
    
    else:
        pass

