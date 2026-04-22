from config import bot_token, user_token
from api.VK_interection import InterectionVKapi
from random import randrange
import vk_api
import json
from vk_api.longpoll import VkLongPoll, VkEventType
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.db.repositories.candidate_repository import CandidateRepository
from infrastructure.db.repositories.favorites_repository import FavoriteRepository
from infrastructure.db.repositories.blacklist_repository import BlacklistRepository
from dataclasses import dataclass
from infrastructure.db.models import Candidate
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.db.favorites import add_to_favorites, get_list_favorites

user_repo = UserRepository()
candidate_repo = CandidateRepository()
favorites_repo = FavoriteRepository()
blacklist_repo = BlacklistRepository()
vk = vk_api.VkApi(token=bot_token)
vk_interection = InterectionVKapi(user_token)
longpoll = VkLongPoll(vk)
users_sessions = {}

def write_message(user_id, message, keyboard):
    vk.method("messages.send", {
        "user_id": user_id,
        "message": message,
        "keyboard": keyboard,
        "random_id": randrange(10**7)})

def get_keyboard():
    keyboard = {
        "one_time": False,
        "buttons":[
            [
                {
                    "action":{
                        "type":"text", 
                        "label":"❤️В избранное"}
                }
                
            ],
            [
                {
                    "action":{
                        "type":"text",
                        "label":"➡️Далее➡️"}
                    
                }
            ],
            [
                {
                    "action":{
                        "type":"text",
                        "label":"🙅‍♂️Не нравится"}
                }

            ],
            [
                {
                    "action":{
                        "type":"text", 
                        "label":"📌Список избранных"}
                }
                
            ],
            [
                {
                    "action":{
                        "type":"text",
                        "label":"🚫Не хочу больше искать"}
                    
                }
            ]
        ]
    }
    keyboard_json = json.dumps(keyboard, ensure_ascii=False) # преобразовали в json тк метод в котором будет использоваться параметр keyboard ожидает СТРОКУ а не СЛОВАРЬ
    return keyboard_json

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text.lower()

            if request == "привет" or request == 'начать':
                welcome_text = ('Привет, давай приступим к поиску. \n\n'
                'Укажите пол, который вас интересует,\
                      где 1 - это девушки👩, 2 - мужчины👨\n'
                      'Укажите город, где 1 - Москва, 2 - Санкт-Петербург\n'
                      'И укажите интервал возраста в котором ищите человека\n'
                      'Пример 1, 1, 18, 28')
                write_message(event.user_id, welcome_text, get_keyboard())

            elif request.count(',') == 3:
                request_data = request.replace(' ', '').split(',')
                users = vk_interection.people_search(
                    request_data[0], request_data[1],
                    request_data[2], request_data[3])
                if not users:
                    write_message(event.user_id, "Никого не найдено. Попробуй другие параметры.")
                else:
                    users_sessions[event.user_id] = {'users': users,'index': 0} # тут у нас сессии пользователей и у каждого пользователя свой словарь людей которые подошли
                    user = users[0]
                    text = f"👤 {user.get('name', '')} {user.get('last_name', '')}\n🔗 https://vk.com/id{user['id']}"
                    write_message(event.user_id, text, get_keyboard())
                    
                    photo_urls = vk_interection.get_photos(user['id'])
                    for url in photo_urls[:3]:
                        parts = url.split('/')[-1].split('_')
                        owner_id = parts[0].replace('photo', '')
                        photo_id = parts[1].split('.')[0]
                        vk.method('messages.send', {
                            'user_id': event.user_id,
                            'attachment': f"photo{owner_id}_{photo_id}",
                            'random_id': randrange(10**7)
                        })

            elif request == '➡️Далее➡️' or request == '🙅‍♂️Не нравится':
                session = users_sessions.get(event.user_id)
                if session:
                    session['index'] += 1
                    if session['index'] >= len(session['users']):
                        write_message(event.user_id, "🏁 Больше нет кандидатов!")
                        session['index'] = len(session['users']) - 1  
                        continue
                    write_message(event.user_id, "Идем дальше")
                    user = session['users'][session['index']]
                    text = f"👤 {user.get('name', '')} {user.get('last_name', '')}\n🔗 https://vk.com/id{user['id']}"
                    write_message(event.user_id, text, get_keyboard())
                    photo_urls = vk_interection.get_photos(user['id'])

                    for url in photo_urls[:3]:
                        parts = url.split('/')[-1].split('_')
                        owner_id = parts[0].replace('photo', '')
                        photo_id = parts[1].split('.')[0]
                        vk.method('messages.send', {
                            'user_id': event.user_id,
                            'attachment': f"photo{owner_id}_{photo_id}",
                            'random_id': randrange(10**7)
                        })
            
            elif request == "❤️в избранное":
                session = users_sessions.get(event.user_id)
                if not session:
                    write_message(event.user_id, "Сначала начни поиск!")
                else:
                    current_user = session['users'][session['index']]
                    candidate_id = current_user['id']
                    
                    result = add_to_favorites(
                        app_user_id=event.user_id,
                        candidate_id=candidate_id,
                        user_repository=user_repo,
                        candidate_repository=candidate_repo,
                        favorites_repository=favorites_repo,
                        blacklist_repository=blacklist_repo
                    )
                    write_message(event.user_id, result.message)
                    
            elif request == "📌список избранных":
                result = get_list_favorites(
                    app_user_id=event.user_id,
                    user_repository=user_repo,
                    favorites_repository=favorites_repo
                )
                
                if not result.success:
                    write_message(event.user_id, result.message)
                elif not result.favorites:
                    write_message(event.user_id, "Список избранных пуст.")
                else:
                    text = "*Ваши избранные:*\n\n"
                    for i, candidate in enumerate(result.favorites, 1):
                        name = getattr(candidate, 'first_name', 'Неизвестно')
                        last_name = getattr(candidate, 'last_name', '')
                        vk_id = getattr(candidate, 'vk_id', '')
                        text += f"{i}. {name} {last_name} — vk.com/id{vk_id}\n"
                    write_message(event.user_id, text)
                

            else:
                write_message(event.user_id, "Не поняла вашего ответа...")





