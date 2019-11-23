import vk_api
import json
from random import randint, choice
from vk_api.longpoll import VkLongPoll, VkEventType


class VkBot:
    def __init__(self, token, admin_id):
        self.admin_id = admin_id
        vk_session = vk_api.VkApi(token=token)
        vk_session._auth_token()
        self.longpoll = VkLongPoll(vk_session)
        self.vk = vk_session.get_api()


    def run(self):
        pass

if __name__ == '__main__':
    VkBot(
    token = open('token.txt').read(),
    admin_id = int(open('admin_id.txt').read())
    ).run()
