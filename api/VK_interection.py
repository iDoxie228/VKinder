import vk_api
import sys
sys.path.append('/Users/sb/Desktop/Python/VKinder')
from config import bot_token, user_token

class InterectionVKapi:
    def __init__(self, user_token):
        vk_session = vk_api.VkApi(token=user_token)
        self.vk = vk_session.get_api()
        
    def people_search(self, sex, city, age_min, age_max):
        response = self.vk.users.search(
            sex=sex, 
            city=city, 
            age_from=age_min, 
            age_to=age_max,
            has_photo=1,
            fields='id,name,last_name,city,bdate,sex,photo_max_orig') #тут мы ищем по след параметрам, а в выводе просим вернуть чуть другие данные
        users_data = response['items']
        
        return users_data

    # def get_info(): - это для доп заданий, все основное мы получили в серч

    def get_photos(self, id): # тут мы получим 3 фото
        response = self.vk.photos.get(owner_id=id, 
            album_id='profile', 
            extended=1, 
            count=200)
        photos_data = response['items'] 
        sorted_photos_data = sorted(photos_data, 
            key=lambda photos_data: photos_data['likes']['count'],
            reverse=True) # это теперь список словарей
        
        
        photos_links = []
        for ph_data in sorted_photos_data[:3]: 
            sizes_lst = ph_data['sizes'] # возвращает СПИСОК словарей
            best_photo = max(sizes_lst, key=lambda sizes_lst: sizes_lst['width']) # выбираем лучшее качество для фото
            photos_links.append(best_photo['url'])

        return photos_links

            


            
        

        

        
        





    


