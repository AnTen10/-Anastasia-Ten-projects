import requests

class RestaurantsReader:
    def __init__(self, base_url: str, nickname: str, cohort: str, api_key: str, limit: int = 50, sort_field: str = "id", sort_direction: str = "asc"):
        self._base_url = base_url
        self._headers = {
            "X-Nickname": nickname,
            "X-Cohort": cohort,
            "X-API-KEY": api_key
        }
        self._limit = limit
        self._sort_field = sort_field
        self._sort_direction = sort_direction

    def get_restaurants(self):
        offset = 0
        while True:
            params = {
                "limit": self._limit,
                "offset": offset,
                "sort_field": self._sort_field,
                "sort_direction": self._sort_direction
            }
            resp = requests.get(f"{self._base_url}/restaurants", headers=self._headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            yield data
            if len(data) < self._limit:
                break
            offset += self._limit
