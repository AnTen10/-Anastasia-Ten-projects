import requests
from pathlib import Path


class APIRequester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def get(self, url: str = ""):
        url = url.lstrip('/')
        full_url = f"{self.base_url}/{url}" if url else f"{self.base_url}/"

        try:
            response = requests.get(full_url, verify=False)
            response.raise_for_status()
            return response
        except requests.RequestException:
            print("Возникла ошибка при выполнении запроса")
            return None


class SWRequester(APIRequester):
    def get_sw_categories(self):
        response = self.get("")
        if response:
            data = response.json()
            return data.keys()
        return []

    def get_sw_info(self, sw_type):
        response = self.get(f"{sw_type}/")
        if response:
            return response.text
        return ""


def save_sw_data():
    requester = SWRequester("https://swapi.dev/api")
    path = Path("data")
    path.mkdir(exist_ok=True)

    categories = requester.get_sw_categories()
    for category in categories:
        file_path = f"data/{category}.txt"
        data = requester.get_sw_info(category)
        if data:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(data)
