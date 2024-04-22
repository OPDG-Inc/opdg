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
        :param filepath: путь на диске, к файлу, который будет загружен (example: video/rkf45.mp4)
        :return:
        """
        url = f"{self.base_url}/resources/upload?path={filepath}"
        headers = {
            'Accept': 'application/json',
            'Authorization': f"OAuth {self.token}"
        }
        response = get(url=url, headers=headers)
        return response.json()

    def upload_file(self, filepath: str, file: str) -> {}:
        """
        :param filepath: путь к файлу на локальной машине (example: C:/users/lario/desktop/rkf45)
        :param file: ссылка, полученнная в get_upload_link
        :return:
        """
        url = f"{self.base_url}/resources/upload?path={filepath}&url={file}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"OAuth {self.token}"
        }
        response = post(url=url, headers=headers)
        return response.json()

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

    def get_async_operation_status(self, operation_url: str):
        """
        :param operation_id: ссылка на асинхронную операцию
        :return:
        """
        url = operation_url
        headers = {
            'Accept': 'application/json',
            'Authorization': f"OAuth {self.token}"
        }
        response = delete(url=url, headers=headers)
        return response.json()
