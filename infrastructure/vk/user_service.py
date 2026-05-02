from domain.services.vk_bdate_parser import parse_vk_bdate
from domain.services.age_calculator import calculate_age

class VKUsersService:
    def __init__(self, vk):
        self.vk = vk

    def get_user_profile(self, vk_user_id: int) -> dict:
        response = self.vk.users.get(
            user_ids=vk_user_id,
            fields="id,city,sex,bdate"
        )

        return self._normilize_user(response)
    
    def _normilize_user(self, user_info: dict) -> dict:
        city = user_info.get("city", {})
        bdate = user_info.get("bdate")
        birth_date = parse_vk_bdate(bdate)
        age = calculate_age(birth_date)

        return {
            "vk_candidate_id": user_info["id"],
            "birth_date": birth_date,
            "sex": user_info.get("sex", 0),
            "first_name": user_info.get("first_name"),
            "last_name": user_info.get("last_name"),
            "age": age,
            "city_id": city.get("id"),
            "city_name": city.get("title"),
            "profile_url": f"https://vk.com/id{user_info['id']}"
        }