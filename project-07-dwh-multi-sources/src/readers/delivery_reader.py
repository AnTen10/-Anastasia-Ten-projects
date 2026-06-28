import requests

class DeliveryReader:
    def __init__(self, base_url, nickname, cohort, api_key, date_from, date_to, limit=50, sort_field="delivery_ts", sort_direction="asc"):
        self._base_url = base_url
        self._headers = {
            "X-Nickname": nickname,
            "X-Cohort": cohort,
            "X-API-KEY": api_key
        }
        self.date_from = date_from
        self.date_to = date_to
        self._limit = limit
        self._sort_field = sort_field
        self._sort_direction = sort_direction

    def get_delivery(self):
        offset = 0
        while True:
            params = {
                "from": self.date_from,
                "to": self.date_to,
                "limit": self._limit,
                "offset": offset,
                "sort_field": self._sort_field,
                "sort_direction": self._sort_direction
            }

            resp = requests.get(f"{self._base_url}/deliveries", headers=self._headers, params=params)
            if resp.status_code == 400:
                print(f"Некорректный диапазон: {self.date_from} - {self.date_to}")
                break
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            yield data
            if len(data) < self._limit:
                break
            offset += self._limit
