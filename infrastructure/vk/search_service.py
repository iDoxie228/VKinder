from datetime import date

class VkSearchService:
    def __init__(self, vk) -> None:
        self.vk = vk
        
    def search_candidates(
            self,
            city: int,
            sex: int,
            age_from: int | None,
            age_to: int | None
        ) -> list[dict]:
        response = self.vk.users.search(
            sex=sex, 
            city=city,
            age_from=age_from,
            age_to=age_to,
            has_photo=1,
            fields="id,city,sex,bdate,is_closed"
        )
        
        items = response.get("items", [])

        return [
            self._normilize_candidate(item)
            for item in items
            if item.get("is_closed", False) 
        ]
    
    def _normilize_candidate(self, item: dict) -> dict:
        city = item.get("city", {})

        return {
            "vk_candidate_id": item["id"],
            "birth_date": item.get("bdate"),
            "sex": item.get("sex", 0),
            "first_name": item.get("first_name"),
            "last_name": item.get("last_name"),
            "age": None,
            "city_id": city.get("id"),
            "city_name": city.get("title"),
            "profile_url": f"https://vk.com/id{item['id']}",
            "is_closed": item.get("is_closed", False)
        }