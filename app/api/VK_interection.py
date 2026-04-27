import vk_api
from infrastructure.config.settings import VK_GROUP_TOKEN, VK_USER_TOKEN

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

    def get_photos(self, user_id: int, count: int = 3) -> list[dict]:
        photos = self.vk.photos.get(
            owner_id=user_id,
            album_id="profile",
            extended=1,
            photo_sizes=1,
        )

        items = photos.get("items", [])

        result = []

        for photo in items:
            sizes = photo.get("sizes", [])
            if not sizes:
                continue

            best_size = max(sizes, key=lambda size: size.get("width", 0) * size.get("height", 0))

            result.append({
                "vk_photo_id": photo["id"],
                "owner_id": photo["owner_id"],
                "photo_url": best_size["url"],
                "likes_amount": photo.get("likes", {}).get("count", 0),
                "attachment": f"photo{photo['owner_id']}_{photo['id']}",
            })

        result.sort(key=lambda item: item["likes_amount"], reverse=True)

        return result[:count]

            


            
        

        

        
        





    

