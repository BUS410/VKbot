import json
from random import randint, choice
from vk_api.longpoll import VkLongPoll, VkEventType
from os import listdir
import requests
from bs4 import BeautifulSoup
import vk_api
import wikipedia as wiki

class VkBot:
    def __init__(self, token, admin_id):
        self.admin_id = admin_id
        vk_session = vk_api.VkApi(token=token)
        vk_session._auth_token()
        self.longpoll = VkLongPoll(vk_session)
        self.vk = vk_session.get_api()
        self.talk_dict = json.load(open('talk.json', encoding='utf-8'))
        wiki.set_lang('RU')

    def load_users(self):
        users = {}
        for user_file in listdir('users'):
            user_id = int(user_file[:-5])
            users[user_id] = json.load(open('users/'+user_file, encoding='utf-8'))
        return users

    def get_info(self, request):
        try:
            res = wiki.page(request).summary
        except:
            res = 'Извини, не понимаю'
        return res

    def rename_user(self, user_id, new_name):
        with open(f'users/{user_id}.json', 'w', encoding='utf-8') as file:
            user = {}
            user['name'] = new_name
            user['state'] = 'command'
            json.dump(user, file, ensure_ascii=False, indent=4)

    def create_user(self, user_id):
        with open(f'users/{user_id}.json', 'w', encoding='utf-8') as file:
            user = {}
            user['name'] = self.get_name(user_id)
            user['state'] = 'command'
            json.dump(user, file, ensure_ascii=False, indent=4)

    def get_name(self, user_id):
        html = requests.get(f'https://vk.com/id{user_id}')
        soup = BeautifulSoup(html.text, 'html.parser')
        return soup.find('h2').text.split(' ')[0]

    def send_msg(self, user_id, message):
        self.vk.messages.send(user_id=user_id, message=message,
        random_id=randint(-2*10**7, 2*10**7))

    def get_weather(self, msg):
        html = requests.get(
                'https://www.google.com/search?q='+msg.replace(' ', '+'),
                {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'}
                ).text
        soup = BeautifulSoup(html, 'html.parser')
        tags = [tag.text for tag in soup.find_all('div')]
        return tags[37]

    def talk(self, user_msg):
        answers = []
        for message, answer in self.talk_dict.items():
            if message.lower() in user_msg.lower():
                answers.append(answer)
        if answers:
            return choice(answers)
        else:
            return 'Непонел'

    def run(self):
        users = self.load_users()

        print('[Start work bot]\n')

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if event.from_user:
                    bot_message = "None"
                    print(f'[ User: {event.user_id} ]')
                    print(f'[ Message: {event.text} ]')
                    if event.user_id == self.admin_id and event.text.lower() == '!выкл':
                        break
                    else:
                        if event.user_id not in users:
                            self.create_user(event.user_id)
                            users = self.load_users()
                            name = users[event.user_id]['name']
                            bot_message = \
                            f'Привет {name}, похоже что ты пишешь мне впервые\n'\
                            'Приятно познакомиться)\n'\
                            'А вот список доступных команд:\n'\
                            '1. !называй меня <новое имя>\n'\
                            '2. !погода <место и время>\n'\
                            '3. !начать общение\n'\
                            '4. что такое <что-то>\n'\
                            '5. кто такой <кто-то>'
                            self.send_msg(user_id=event.user_id,
                            message=bot_message)
                        else:
                            user = users[event.user_id]
                            if user['state'] == 'command':
                                if '!погода' in event.text:
                                    degress = self.get_weather(event.text)
                                    bot_message = f'{degress}, не блогадари, {user["name"]})'
                                    self.send_msg(user_id=event.user_id,
                                    message=bot_message)
                                elif '!называй меня' in event.text:
                                    self.rename_user(event.user_id, event.text[13:])
                                    users = self.load_users()
                                    user = users[event.user_id]
                                    bot_message = f'Ну хорошо, теперь буду звать тебя {user["name"]}'
                                    self.send_msg(event.user_id,
                                    bot_message)
                                elif event.text == '!начать общение':
                                    users[event.user_id]['state'] = 'talk'
                                    self.send_msg(event.user_id,
                                    'Чтобы остановить общение напишите "!остановить общение"\n'\
                                    f'Чтож {user["name"]}, давай поболтаем')
                                elif 'что такое ' in event.text.lower() or 'кто такой ' in event.text.lower():
                                    bot_message = self.get_info(event.text)
                                    self.send_msg(event.user_id,
                                    bot_message)
                                else:
                                    bot_message = \
                                    'Команды:\n'\
                                    '1. !называй меня <новое имя>\n'\
                                    '2. !погода <место и время>\n'\
                                    '3. !начать общение'
                                    self.send_msg(event.user_id,
                                    bot_message
                                    )
                            elif user['state'] == 'talk':
                                if event.text == '!остановить общение':
                                    users[event.user_id]['state'] = 'command'
                                    self.send_msg(event.user_id,
                                    'Общение остановлено')
                                else:
                                    bot_message = self.talk(event.text)
                                    self.send_msg(event.user_id,
                                    bot_message)

                    print(f'[ Bot: {bot_message} ]\n')

        print('[End work bot]\n')

if __name__ == '__main__':
    VkBot(
    token = open('token.txt').read(),
    admin_id = int(open('admin_id.txt').read())
    ).run()
