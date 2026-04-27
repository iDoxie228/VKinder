from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
import vk_api
import json

from infrastructure.config.settings import VK_GROUP_TOKEN, VK_USER_TOKEN
from app.api.VK_interection import InterectionVKapi

from infrastructure.db.session import SessionLocal
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.db.repositories.candidate_repository import CandidateRepository
from infrastructure.db.repositories.favorites_repository import FavoriteRepository
from infrastructure.db.repositories.blacklist_repository import BlacklistRepository
from infrastructure.db.repositories.candidate_photo_repository import CandidatePhotoRepository
from infrastructure.db.repositories.shown_candidate_repository import ShownCandidateRepository
from dataclasses import dataclass

from app.use_cases.add_to_favorites import add_to_favorites
from app.use_cases.list_favorites import get_list_favorites
from app.use_cases.add_to_blacklist import add_to_blacklist

db = SessionLocal()

user_repo = UserRepository(db)
candidate_repo = CandidateRepository(db)
favorites_repo = FavoriteRepository(db)
blacklist_repo = BlacklistRepository(db)
photo_repo = CandidatePhotoRepository(db)
shown_repo = ShownCandidateRepository(db)

vk = vk_api.VkApi(token=VK_GROUP_TOKEN)
vk_interection = InterectionVKapi(VK_USER_TOKEN)
longpoll = VkLongPoll(vk)
users_sessions = {}

def write_message(user_id, message, keyboard = None):
    
    params = {
        "user_id": user_id,
        "message": message,
        "random_id": randrange(10**7)
        }
    
    if keyboard is not None:
        params["keyboard"] = keyboard

    vk.method("messages.send", params)

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
            app_user, _ = user_repo.get_or_create(
                vk_user_id=event.user_id,
                defaults={
                    "profile_url": f"https://vk.com/id{event.user_id}",
                },
            )

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
                    saved_candidate_ids = []

                    for vk_user in users:
                        candidate, _ = candidate_repo.get_or_create(
                            vk_candidate_id=vk_user["id"],
                            defaults={
                                "first_name": vk_user.get("first_name"),
                                "last_name": vk_user.get("last_name"),
                                "sex": vk_user.get("sex"),
                                "city_id": vk_user.get("city", {}).get("id") if vk_user.get("city") else None,
                                "city_name": vk_user.get("city", {}).get("title") if vk_user.get("city") else None,
                                "profile_url": f"https://vk.com/id{vk_user['id']}",
                                "is_closed": vk_user.get("is_closed", False),
                            },
                        )
                        saved_candidate_ids.append(candidate.id)

                    users_sessions[event.user_id] = {
                        "app_user_id": app_user.id,
                        "candidate_ids": saved_candidate_ids,
                        "index": 0,
                    } # тут у нас сессии пользователей и у каждого пользователя свой словарь людей которые подошли
                    
                    candidate_id = users_sessions[event.user_id]["candidate_ids"][0]
                    candidate = candidate_repo.get_by_id(candidate_id)

                    text = (
                        f"👤 {candidate.first_name or ''} {candidate.last_name or ''}\n"
                        f"🔗 {candidate.profile_url}"
                    )
                    write_message(event.user_id, text, get_keyboard())

                    photos = vk_interection.get_photos(candidate.vk_candidate_id)

                    photo_repo.add_many(
                        candidate_id=candidate.id,
                        photos_data=photos,
                    )

                    for photo in photos:
                        vk.method("messages.send", {
                            "user_id": event.user_id,
                            "attachment": photo["attachment"],
                            "random_id": randrange(10**7),
                        })

            elif request == "➡️далее➡️":
                session = users_sessions.get(event.user_id)

                if not session:
                    write_message(event.user_id, "Сначала начни поиск!")
                    continue

                session["index"] += 1

                candidate_ids = session["candidate_ids"]

                if session["index"] >= len(candidate_ids):
                    write_message(event.user_id, "🏁 Больше нет кандидатов!")
                    session["index"] = len(candidate_ids) - 1
                    continue

                candidate_id = candidate_ids[session["index"]]
                candidate = candidate_repo.get_by_id(candidate_id)

                text = (
                    f"👤 {candidate.first_name or ''} {candidate.last_name or ''}\n"
                    f"🔗 {candidate.profile_url}"
                )

                write_message(event.user_id, text, get_keyboard())

                photos = vk_interection.get_photos(candidate.vk_candidate_id)

                photo_repo.add_many(
                    candidate_id=candidate.id,
                    photos_data=photos,
                )

                for photo in photos:
                    vk.method("messages.send", {
                        "user_id": event.user_id,
                        "attachment": photo["attachment"],
                        "random_id": randrange(10**7),
                    })

            elif request == "🙅‍♂️не нравится":
                session = users_sessions.get(event.user_id)

                if not session:
                    write_message(event.user_id, "Сначала начни поиск!")
                    continue

                candidate_ids = session["candidate_ids"]
                index = session["index"]

                if index >= len(candidate_ids):
                    write_message(event.user_id, "🏁 Больше нет кандидатов!")
                    continue

                candidate_id = candidate_ids[index]

                result = add_to_blacklist(
                    app_user_id=session["app_user_id"],
                    candidate_id=candidate_id,
                    user_repository=user_repo,
                    candidate_repository=candidate_repo,
                    favorites_repository=favorites_repo,
                    blacklist_repository=blacklist_repo,
                )

                write_message(event.user_id, result.message)

                session["index"] += 1

                if session["index"] >= len(candidate_ids):
                    write_message(event.user_id, "🏁 Больше нет кандидатов!")
                    session["index"] = len(candidate_ids) - 1
                    continue

                next_candidate_id = candidate_ids[session["index"]]
                candidate = candidate_repo.get_by_id(next_candidate_id)

                text = (
                    f"👤 {candidate.first_name or ''} {candidate.last_name or ''}\n"
                    f"🔗 {candidate.profile_url}"
                )

                write_message(event.user_id, text, get_keyboard())

                photos = vk_interection.get_photos(candidate.vk_candidate_id)

                photo_repo.add_many(
                    candidate_id=candidate.id,
                    photos_data=photos,
                )

                for photo in photos:
                    vk.method("messages.send", {
                        "user_id": event.user_id,
                        "attachment": photo["attachment"],
                        "random_id": randrange(10**7),
                    })

            elif request == "❤️в избранное":
                session = users_sessions.get(event.user_id)
                if not session:
                    write_message(event.user_id, "Сначала начни поиск!")
                else:
                    session = users_sessions[event.user_id]
                    candidate_id = session["candidate_ids"][session["index"]]

                    result = add_to_favorites(
                        app_user_id=session["app_user_id"],
                        candidate_id=candidate_id,
                        user_repository=user_repo,
                        candidate_repository=candidate_repo,
                        favorites_repository=favorites_repo,
                        blacklist_repository=blacklist_repo
                    )
                    write_message(event.user_id, result.message)
                    
            elif request == "📌список избранных":
                result = get_list_favorites(
                    app_user_id=app_user.id,
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
                        vk_id = candidate.vk_candidate_id
                        text += f"{i}. {candidate.first_name} {candidate.last_name} — https://vk.com/id{vk_id}\n"
                    write_message(event.user_id, text)
                

            else:
                write_message(event.user_id, "Не поняла вашего ответа...")




