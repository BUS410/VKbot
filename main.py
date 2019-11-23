import vk_api
import json
from random import randint, choice
from vk_api.longpoll import VkLongPoll, VkEventType
from os import listdir
import requests
from bs4 import BeautifulSoup


class VkBot:
    def __init__(self, token, admin_id):
        self.admin_id = admin_id
        vk_session = vk_api.VkApi(token=token)
        vk_session._auth_token()
        self.longpoll = VkLongPoll(vk_session)
        self.vk = vk_session.get_api()

    def load_users(self):
        users = {}
        for user_file in listdir('users'):
            user_id = int(user_file[:-5])
            users[user_id] = json.load(open('users/'+user_file, encoding='utf-8'))
        return users

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

    def run(self):
        print('[Start work bot]\n')

        users = self.load_users()

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if event.from_user:
                    print(f'[ User: {event.user_id} ]')
                    print(f'[ Message: {event.text} ]')
                    if event.user_id == self.admin_id and event.text.lower() == 'выкл':
                        break
                    else:
                        if event.user_id not in users:
                            self.create_user(event.user_id)
                            users = self.load_users()
                            name = users[event.user_id]['name']
                            bot_message = f'Привет {name}, похоже что ты пишешь мне впервые\n'\
                            'Приятно познакомиться)\n'\
                            'А вот список доступных команд:\n'\
                            '1. !сменить имя на <новое имя>\n'\
                            '2. !погода <место и время>'
                            self.send_msg(user_id=event.user_id,
                            message=bot_message)
                        else:
                            user = users[event.user_id]
                            if '!погода' in event.text:
                                degress = self.get_weather(event.text)
                                bot_message = f'{degress}, не блогадари)'
                                self.send_msg(user_id=event.user_id,
                                message=bot_message)

                    print(f'[ Bot: {bot_message} ]\n')

        print('[End work bot]\n')

if __name__ == '__main__':
    VkBot(
    token = open('token.txt').read(),
    admin_id = int(open('admin_id.txt').read())
    ).run()
