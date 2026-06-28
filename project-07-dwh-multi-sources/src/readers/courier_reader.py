import requests
from typing import Generator, List, Dict

class CourierReader:

    def __init__(
        self,
        base_url: str,
        nickname: str,
        cohort: str,
        api_key: str,
        limit: int,
        sort_field: str,
        sort_direction: str
    ):
        self._base_url = base_url
        self._headers = {
            "X-Nickname": nickname,
            "X-Cohort": cohort,
            "X-API-KEY": api_key
        }
        self._limit = limit
        self._sort_field = sort_field
        self._sort_direction = sort_direction

    def get_couriers(self) -> Generator[List[Dict], None, None]:
        offset = 0

        while True:
            params = {
                "limit": self._limit,
                "offset": offset,
                "sort_field": self._sort_field,
                "sort_direction": self._sort_direction
            }

            response = requests.get(
                f"{self._base_url}/couriers",
                headers=self._headers,
                params=params
            )

            response.raise_for_status()
            data = response.json()

            if not data:
                break

            yield data

            if len(data) < self._limit:
                break

            offset += self._limit