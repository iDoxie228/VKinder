from infrastructure.db.models import Candidate

def exclude_closed(candidates: list[Candidate]) -> list[Candidate]:
    return [candidate for candidate in candidates if candidate.is_closed==False]

def exclude_blacklisted(candidates: list[Candidate], blacklisted_ids: list[int] | None) -> list[Candidate]:
    if blacklisted_ids is None:
        return candidates
    
    return[
        candidate 
        for candidate in candidates
        if candidate.id not in blacklisted_ids
    ]
    
def exclude_shown(candidates: list[Candidate], shown_ids: list[int] | None) -> list[Candidate]:
    if shown_ids is None:
        return candidates

    return[
        candidate 
        for candidate in candidates
        if candidate.id not in shown_ids
    ]

def filter_by_sex(candidates: list[Candidate], sex: str | None) -> list[Candidate]:
    
    if sex is None:
        return candidates
    
    return[
        candidate
        for candidate in candidates
        if candidate.sex == sex
    ]

def filter_by_city(candidates: list[Candidate], city_id: int | None) -> list[Candidate]:
    if city_id is None:
        return candidates
    
    return[
        candidate
        for candidate in candidates
        if candidate.city_id == city_id
    ]

def filter_by_age(candidates: list[Candidate], age: int) -> list[Candidate]:
    if age is None:
        return candidates
    
    return[
        candidate
        for candidate in candidates
        if candidate.age == age
    ]

def filter_by_age_range(candidates: list[Candidate], age_min: int | None, age_max: int | None) -> list[Candidate]:
    if age_max is None and age_min is None:
        return candidates

    if age_max is None:
        return[candidate for candidate in candidates if candidate.age <= age_max]
    
    if age_min is None:
        return[candidate for candidate in candidates if candidate.age >= age_min]
    
    return[
        candidate
        for candidate in candidates
        if age_min <= candidate.age and candidate.age <= age_max
    ]

def all_filters(
        candidates: list[Candidate],
        blacklisted_ids: list[int] | None = None,
        shown_ids: list[int] | None = None,
        sex: str | None = None,
        city_id: int | None = None,
        age: int | None = None,
        age_max: int | None = None,
        age_min: int | None = None,
        exclude_closed_flag: bool = True
) -> list[Candidate]:
    res = candidates
    if exclude_closed_flag:
        res = exclude_closed(candidates)
    
    res = exclude_blacklisted(res, blacklisted_ids)
    res = exclude_shown(res, shown_ids)
    res = filter_by_sex(res, sex)
    res = filter_by_city(res, city_id)
    res = filter_by_age(res, age)
    res = filter_by_age_range(res, age_max, age_min)

    return res


