class VKPhotosService:
    def __init__(self, vk) -> None:
        self.vk = vk

    def get_top_photos(
        self,
        vk_candidate_id: int,
        count: int = 3,
    ) -> list[dict]:
        response = self.vk.photos.get(
            owner_id=vk_candidate_id,
            album_id="profile",
            extended=1,
            photo_sizes=1,
        )

        items = response.get("items", [])

        photos = [
            self._normalize_photo(photo)
            for photo in items
            if photo.get("sizes")
        ]

        photos.sort(
            key=lambda photo: photo["likes_amount"],
            reverse=True,
        )

        return photos[:count]

    def _normalize_photo(self, photo: dict) -> dict:
        return {
            "vk_photo_id": photo["id"],
            "owner_id": photo["owner_id"],
            "photo_url": self._get_best_size_url(photo),
            "likes_amount": photo.get("likes", {}).get("count", 0),
            "attachment": f"photo{photo['owner_id']}_{photo['id']}",
        }

    def _get_best_size_url(self, photo: dict) -> str | None:
        sizes = photo.get("sizes") or []

        if not sizes:
            return None

        best_size = max(
            sizes,
            key=lambda size: size.get("width", 0) * size.get("height", 0),
        )

        return best_size.get("url")