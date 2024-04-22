from requests import get, post, put, delete


class YandexAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def is_connected(self) -> {}:
        # проверяет подключение к диску по токену

        url = self.base_url
        headers = {
            'Accept': 'application/json',
            'Authorization': f"OAuth {self.token}"
        }
        response = get(url=url, headers=headers)
        return response.json()

    def get_file_link(self, filepath: str) -> {}:
        """
        :param filepath: путь к файлу/папке
        :return:
        """
        url = f"{self.base_url}/resources/download?path={filepath}"
        headers = {
            'Accept': 'application/json',
            'Authorization': f"OAuth {self.token}"
        }
        response = get(url=url, headers=headers)
        return response.json()

    def make_dir(self, filepath: str) -> {}:
        """
        :param filepath: путь, по которму будет создана папка
        :return:
        """
        url = f"{self.base_url}/resources?path={filepath}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"OAuth {self.token}"
        }
        response = put(url=url, headers=headers)
        return response.json()

    def get_upload_link(self, filepath: str) -> {}:
        """
        :param filepath: путь на Яндекс.диске, к файлу, который будет загружен (example: video/rkf45.mp4)
        :return:
        """
        url = f"{self.base_url}/resources/upload?path={filepath}"
        headers = {
            'Accept': 'application/json',
            'Authorization': f"OAuth {self.token}"
        }
        response = get(url=url, headers=headers)
        return response.json()

    def upload_file(self, url: str, filepath: str) -> {}:
        """
        :param url: поле href из get_upload_link
        :param filepath: путь к файлу на локальной машине
        :return:
        """
        file = open(filepath, mode='rb')
        put(url=url, files={'file': file})

    def delete(self, filepath: str, permanently: bool = False) -> {}:
        """
        :param filepath: путь к файлу или папке
        :param permanently: перманентное удаление или перенос в корзину
        :return:
        """
        url = f"{self.base_url}/resources?path={filepath}&permanently={permanently}"
        headers = {
            'Accept': 'application/json',
            'Authorization': f"OAuth {self.token}"
        }
        response = delete(url=url, headers=headers)
        return response.json()


# api = YandexAPI("https://cloud-api.yandex.net/v1/disk", "y0_AgAAAAAdcNW3AADLWwAAAAEBGkUkAAAnJkzf72ZFMIjCDEzgzRpDfiIqRQ")
# link = api.get_upload_link('test123.png')['href']
# api.upload_file(link, "C:/Users/Lario/Downloads/gr1541_2000_1100.png")