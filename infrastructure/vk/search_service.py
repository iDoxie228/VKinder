from datetime import date
from domain.services.vk_bdate_parser import parse_vk_bdate
from domain.services.age_calculator import calculate_age

class VkSearchService:
    def __init__(self, vk) -> None:
        self.vk = vk
        
    def search_candidates(
            self,
            city_id: int,
            sex: int,
            age_from: int | None,
            age_to: int | None
        ) -> list[dict]:
        response = self.vk.users.search(
            sex=sex, 
            city=city_id,
            age_from=age_from,
            age_to=age_to,
            has_photo=1,
            fields="id,city,sex,bdate,is_closed",
            count=1000
        )
        
        items = response.get("items", [])

        return [
            self._normilize_candidate(item)
            for item in items
            if not item.get("is_closed", False) 
        ]
    
    def _normilize_candidate(self, item: dict) -> dict:
        city = item.get("city", {})
        bdate = item.get("bdate")
        birth_date = parse_vk_bdate(bdate)
        age = calculate_age(birth_date)

        return {
            "vk_candidate_id": item["id"],
            "birth_date": birth_date,
            "sex": item.get("sex", 0),
            "first_name": item.get("first_name"),
            "last_name": item.get("last_name"),
            "age": age,
            "city_id": city.get("id"),
            "city_name": city.get("title"),
            "profile_url": f"https://vk.com/id{item['id']}",
            "is_closed": item.get("is_closed", False)
        }