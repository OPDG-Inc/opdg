from json import dump, loads
import logging

from bs4 import BeautifulSoup
from requests import get

from control_panel.functions import update_config_file, load_config_file

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")


def get_institutes():
    structure = {}
    url = "https://ruz.spbstu.ru/"
    page = get(url)

    if page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html.parser')
        script_tags = soup.find_all('script')
        current_script = script_tags[3]
        data_string = current_script.text.split("window.__INITIAL_STATE__ = ")[-1].replace(';', '')
        data = loads(data_string)
        institutes = data['faculties']['data']
        for a in institutes:
            structure[a['id']] = {
                'name': a['name'],
                'abbr': a['abbr'],
                'groups': []
            }
        with open('parsed.json', mode='w', encoding='utf-8') as config_file:
            dump(structure, config_file)
    else:
        logging.error(f"UPDATING GROUP LIST: request: {page.request}, json: {page.json()}")


def get_groups():
    structure = load_config_file('parsed.json')
    groups_list = load_config_file('study_groups.json')
    for inst_id in structure.keys():
        print(inst_id)
        url = f"https://ruz.spbstu.ru/faculty/{inst_id}/groups"
        page = get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            script_tags = soup.find_all('script')
            current_script = script_tags[3]
            data_string = current_script.text.split("window.__INITIAL_STATE__ = ")[-1].replace(';', '')
            data = loads(data_string)
            groups = data['groups']['data'][f'{inst_id}']
            for group in groups:
                groups_list.append(group['name'])
        else:
            logging.error(f"UPDATING GROUP LIST: request: {page.request}, json: {page.json()}")
            return
    update_config_file(structure, 'parsed.json')
    update_config_file(groups_list, 'study_groups.json')


def clear_empty():
    old = load_config_file('parsed.json')
    new = {}
    for key in old.keys():
        if len(old[key]['groups']) != 0:
            new[key] = old[key]
    update_config_file(new, 'parsed.json')


def update_group_list():
    get_institutes()
    get_groups()


update_group_list()
