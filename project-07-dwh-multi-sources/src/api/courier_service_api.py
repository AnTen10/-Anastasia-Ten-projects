import requests

class CourierServiceApi:
    def __init__(self, base_url, nickname, cohort, api_key):
        self.base_url = base_url
        self.headers = {
            "X-Nickname": nickname,
            "X-Cohort": cohort,
            "X-API-KEY": api_key,
        }

    def _get(self, endpoint, params=None):
        response = requests.get(
            f"{self.base_url}/{endpoint}",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_restaurants(self, limit=50, offset=0):
        return self._get(
            "restaurants",
            {"limit": limit, "offset": offset}
        )

    def get_couriers(self, limit=50, offset=0):
        return self._get(
            "couriers",
            {"limit": limit, "offset": offset}
        )