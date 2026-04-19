from infrastructure.db.models import CandidatePhoto

def calculate_photo_score(photo: CandidatePhoto) -> int:
    if photo.likes_amount: 
        return photo.likes_amount
    else:
        return 0

def clear_photos(photos: list[CandidatePhoto]) -> list[CandidatePhoto]:
    unique_photos = []
    seen_keys = []

    for photo in photos:
        if photo.photo_url is None and photo.vk_photo_id is None:
            continue

        key = (photo.candidate_id, photo.vk_photo_id)
        if key in seen_keys:
            continue

        seen_keys.append(key)

        unique_photos.append(photo)

    return unique_photos

def sort_photos(photos: list[CandidatePhoto]) -> list[CandidatePhoto]:
    return sorted(
        photos,
        key=calculate_photo_score,
        reverse=True
    )

def get_top_photos(photos: list[CandidatePhoto], limit: int = 3) -> list[CandidatePhoto]:
    sorted_photos = sort_photos(clear_photos(photos))

    return sorted_photos[:limit]
