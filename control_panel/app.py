import datetime
import hashlib
import os
import platform
import random
import subprocess
import time
import uuid

import flet as ft
import requests
from mysql.connector import connect, Error as sql_error
from dotenv import load_dotenv

from functions import load_config_file
from elements.screens import screens
from elements.tabs import tabs_config
from elements.errors_targets import targets

import elements.global_vars
from elements.text import labels

current_tab_index = -1
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)

load_dotenv()


def create_db_connection():
    try:
        connection = connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        cur = connection.cursor(dictionary=True)
        connection.autocommit = True
        return connection, cur

    except sql_error as e:
        elements.global_vars.ERROR_TEXT = str(e)
        elements.global_vars.DB_FAIL = True
        return None, None


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.START,
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        font_family="Geologica",
        color_scheme=ft.ColorScheme(
            primary=ft.colors.WHITE
        )
    )

    page.fonts = {
        "Montserrat": "fonts/Montserrat-SemiBold.ttf",
        "Geologica": "fonts/Geologica.ttf",
        # "Geologica-Black": "fonts/Geologica-black.ttf"
    }

    # page.window_width = 720
    # page.window_height = 1280

    def on_dialog_result(e: ft.FilePickerResultEvent):
        print("Selected files:", e.files)
        save_uploaded_file()

    def save_new_topic(e: ft.ControlEvent):
        topic = new_topic_field.value.strip()
        get_from_db(f"INSERT INTO topic (description) VALUES ('{topic}')")
        new_topic_field.value = ''
        btn_add_topic.disabled = True

        open_snackbar("Тема добавлена")

    def save_uploaded_file():
        upload_list = []
        if filepicker.result is not None and filepicker.result.files is not None:
            file = filepicker.result.files[-1]
            open_loading_snackbar(f"Загружаем {file.name}")
            upload_list.append(
                ft.FilePickerUploadFile(
                    file.name,
                    upload_url=page.get_upload_url(file.name, 600),
                )
            )
            print("OK")
            print(filepicker.upload(upload_list))
            print("OK")
            time.sleep(3)
            print("OK3")
            upload_topic_from_file(file.name)

    filepicker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(filepicker)

    def open_loading_snackbar(text: str):
        content = ft.Row(
            [
                ft.ProgressRing(color=ft.colors.BLACK, scale=0.6),
                ft.Text(text, size=18, font_family="Geologica", weight=ft.FontWeight.W_400)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
        sb = ft.SnackBar(
            content=content,
            duration=1000
        )
        page.snack_bar = sb
        sb.open = True
        page.update()

    def open_snackbar(text: str, bg_color=None, text_color=None):
        # Оповещение в нижней части экрана

        content = ft.Text(text, size=18, font_family="Geologica", weight=ft.FontWeight.W_400)
        sb = ft.SnackBar(
            content=content,
            duration=1000
        )

        if bg_color is not None:
            sb.bgcolor = bg_color

        if text_color is not None:
            content.color = text_color

        page.snack_bar = sb
        sb.open = True
        page.update()

    def get_from_db(request_text: str, many=False):
        try:
            cur.execute(request_text)
        except sql_error as e:
            elements.global_vars.ERROR_TEXT = str(e)
            elements.global_vars.DB_FAIL = True
        if many:
            return cur.fetchall()
        else:
            return cur.fetchone()

    def upload_topic_from_file(file: str):
        with open(os.path.join('assets/uploads', file)) as file:
            topics_list = [topic.strip() for topic in file.readlines()]
        for topic in topics_list:
            get_from_db(f"INSERT INTO topic (description) VALUES ('{topic}')")
        change_screen('main')
        change_navbar_tab(0)
        open_snackbar("Темы загружены")

    def get_stats():
        elements.global_vars.GROUP_COUNT = get_from_db("SELECT COUNT(*) FROM sgroups")['COUNT(*)']
        elements.global_vars.PART_COUNT = get_from_db("SELECT COUNT(*) FROM participants")['COUNT(*)']
        elements.global_vars.VIDEOS = get_from_db("SELECT COUNT(*) FROM sgroups WHERE video_status = 'uploaded'")['COUNT(*)']

        stats_card = ft.Card(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            ft.Row(
                                [
                                    ft.Container(ft.Text("Статистика", size=20, weight=ft.FontWeight.W_700), expand=True),
                                    ft.IconButton(ft.icons.RESTART_ALT_ROUNDED, on_click=lambda _: goto_stats(), tooltip="Обновить данные")
                                ]
                            ),
                            margin=ft.margin.only(bottom=20)
                        ),
                        statistic_tile(
                            title="Количество групп",
                            descr=f"{elements.global_vars.GROUP_COUNT}",
                            # icon=ft.Icon(ft.icons.GROUPS_ROUNDED),
                        ),
                        statistic_tile(
                            title="Количество участников",
                            descr=f"{elements.global_vars.PART_COUNT}",
                            # icon=ft.Icon(ft.icons.ACCOUNT_CIRCLE, size=30),
                        ),
                        statistic_tile(
                            title="Загружено видео",
                            descr=f"{elements.global_vars.VIDEOS} из {elements.global_vars.GROUP_COUNT}",
                            # icon=ft.Icon(ft.icons.VIDEO_CAMERA_FRONT_ROUNDED, size=30),
                        )
                    ]
                ),
                padding=15
            ),
            elevation=10,
            width=450,
            col={"lg": 1}
        )
        page.controls[-1].content.controls.insert(0, stats_card)
        page.update()

    def get_groups():
        statuses = {
            'waiting': {
                'title': labels['statuses']['video_waiting'],
                'flag': True
            },
            'uploaded': {
                'title': labels['statuses']['video_uploaded'],
                'flag': False
            }
        }
        rr = ft.ResponsiveRow(columns=4)
        groups_list = get_from_db("SELECT * FROM sgroups", many=True)
        if len(groups_list) > 0:
            for group in groups_list:

                topic_info = get_from_db(f"SELECT * FROM topic WHERE topic_id = {group['topic_id']}")

                participants_info = get_from_db(
                    f"SELECT * FROM participants WHERE group_id = {group['group_id']}",
                    many=True)

                participants_panel = ft.ExpansionTile(
                    title=ft.Text(labels['elements']['participants_panel_title'], size=18),
                    affinity=ft.TileAffinity.LEADING,
                )
                for part in participants_info:
                    participants_panel.controls.append(
                        ft.ListTile(title=ft.Text(f"{part['name']} ({part['study_group']})", size=18,
                                                  text_align=ft.TextAlign.START))
                    )

                group_card = ft.Card(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ListTile(
                                    title=ft.Text(f"{group['name']}", size=20, font_family="Geologica", weight=ft.FontWeight.W_700),
                                    subtitle=ft.Text(f"#{topic_info['topic_id']} {topic_info['description']}", size=18),
                                ),
                                ft.Container(
                                    ft.ListTile(
                                        title=ft.Text(labels['elements']['marks_title'], size=20, font_family="Geologica", weight=ft.FontWeight.W_700),
                                        subtitle=ft.Text(labels['elements']['no_marks_subtitle'], size=18),
                                    ),
                                    margin=ft.margin.only(top=-20),
                                    visible=not statuses[group['video_status']]['flag']
                                ),
                                ft.ResponsiveRow(
                                    [
                                        ft.ElevatedButton(
                                            text=labels['buttons']['group_part'],
                                            icon=ft.icons.GROUPS_ROUNDED,
                                            bgcolor=ft.colors.PRIMARY_CONTAINER,
                                            data=participants_info,
                                            on_click=show_part_list,
                                            col={"lg": 1}
                                        ),
                                        ft.ElevatedButton(
                                            text=statuses[group['video_status']]['title'],
                                            icon=ft.icons.ONDEMAND_VIDEO_ROUNDED,
                                            disabled=statuses[group['video_status']]['flag'],
                                            bgcolor=ft.colors.PRIMARY_CONTAINER,
                                            url=group['video_link'],
                                            col={"lg": 1}
                                        ),

                                    ],
                                    columns=2,
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                            ],
                        ),
                        padding=15
                    ),
                    col={"lg": 1},
                    elevation=10,
                    data=group['group_id']
                )
                rr.controls.append(group_card)
            page.add(rr)
        else:
            if elements.global_vars.DB_FAIL:
                show_error('db_request', labels['errors']['db_request'].format(elements.global_vars.ERROR_TEXT.split(":")[0]))
            else:
                show_error('empty_groups', labels['errors']['empty_groups'])
        page.update()

    def get_topics():
        statuses = {
            "free": {
                "title": labels['statuses']['topic_free'],
                'icon': ft.Icon(ft.icons.MESSAGE_ROUNDED, color=ft.colors.GREEN),
                "flag": True
            },
            "busy": {
                "title": labels['statuses']['topic_busy'],
                'icon': ft.Icon(ft.icons.GROUPS_ROUNDED, color=ft.colors.AMBER),
                "flag": False
            },
        }

        rr = ft.ResponsiveRow(columns=3)

        topics_list = get_from_db(f"SELECT * from topic", many=True)
        print(len(topics_list))
        if len(topics_list) > 0:
            busy_count = 0
            for topic in topics_list:
                if topic['status'] == "busy":
                    busy_count += 1
                topic_card = ft.Card(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ListTile(
                                    title=ft.Text(f"#{topic['topic_id']} {topic['description']}", size=20, font_family="Geologica", weight=ft.FontWeight.W_700),
                                    subtitle=ft.Row(
                                        [
                                            statuses[topic['status']]['icon'],
                                            ft.Text(statuses[topic['status']]['title'], size=18)
                                        ]
                                    ),
                                    # expand=True
                                ),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            text=labels['buttons']['edit'], icon=ft.icons.EDIT_ROUNDED,
                                            visible=statuses[topic['status']]['flag'],
                                            data=topic,
                                            on_click=goto_edit_topic,
                                            bgcolor=ft.colors.PRIMARY_CONTAINER
                                        ),
                                        ft.ElevatedButton(
                                            text=labels['buttons']['delete'], icon=ft.icons.DELETE_ROUNDED,
                                            visible=statuses[topic['status']]['flag'],
                                            on_click=confirm_delete,
                                            data=f"delete_topic_{topic['topic_id']}",
                                            bgcolor=ft.colors.RED
                                        ),
                                        # ft.ElevatedButton(
                                        #     text=labels['buttons']['group_info'], icon=ft.icons.FILE_OPEN_ROUNDED,
                                        #     visible=not statuses[topic['status']]['flag'],
                                        #     bgcolor=ft.colors.PRIMARY_CONTAINER
                                        # ),
                                    ],
                                    alignment=ft.MainAxisAlignment.END
                                )
                            ]
                        ),
                        padding=15
                    ),
                    elevation=10,
                    # height=200,
                    col={"lg": 1},
                    data=topic['topic_id']
                )
                rr.controls.append(topic_card)
            page.add(rr)
        else:
            if elements.global_vars.DB_FAIL:
                show_error('db_request', labels['errors']['db_request'].format(elements.global_vars.ERROR_TEXT))
            else:
                show_error('empty_topics', labels['errors']['empty_topics'])
        page.update()

    def get_jury():
        statuses = {
            "waiting": {
                "title": labels['statuses']['jury_waiting'],
                "flag": True,
                "icon": ft.Icon(ft.icons.ACCESS_TIME_ROUNDED, color=ft.colors.AMBER)
            },
            "registered": {
                "title": labels['statuses']['jury_registered'],
                "flag": False,
                "icon": ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE_OUTLINED, color=ft.colors.GREEN)
            },
        }
        rr = ft.ResponsiveRow(columns=4)
        jury_list = get_from_db("SELECT * FROM jury", many=True)
        if len(jury_list) > 0:
            for jury in jury_list:
                jury_card = ft.Card(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ListTile(
                                    title=ft.Text(f"{jury['name']}", size=20, font_family="Geologica", weight=ft.FontWeight.W_700),
                                    subtitle=ft.Row([
                                        statuses[jury['status']]['icon'],
                                        ft.Text(f"{statuses[jury['status']]['title']}", size=18)
                                    ])
                                ),
                                ft.Row(
                                    # scroll=ft.ScrollMode.ADAPTIVE,
                                    controls=[
                                        ft.ElevatedButton(
                                            text=labels['buttons']['delete'],
                                            icon=ft.icons.DELETE_ROUNDED,
                                            bgcolor=ft.colors.RED,
                                            data=f"delete_jury_{jury['jury_id']}",
                                            on_click=confirm_delete
                                        ),
                                        ft.ElevatedButton(
                                            text=labels['buttons']['link'], icon=ft.icons.LINK_ROUNDED,
                                            visible=statuses[jury['status']]['flag'],
                                            data=jury['pass_phrase'],
                                            bgcolor=ft.colors.PRIMARY_CONTAINER,
                                            on_click=get_jury_link
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.END
                                )
                            ]
                        ),
                        padding=15
                    ),
                    elevation=10,
                    # height=200,
                    col={"lg": 1},
                    data=jury['jury_id']
                )
                rr.controls.append(jury_card)
            page.add(rr)
        else:
            if elements.global_vars.DB_FAIL:
                show_error('db_request', labels['errors']['db_request'].format(elements.global_vars.ERROR_TEXT))
            else:
                show_error('empty_jury', labels['errors']['empty_jury'])

    def show_error(target: str, description: str):
        page.scroll = None
        page.clean()
        page.add(
            ft.Column(
                controls=[
                    ft.Card(
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Container(ft.Image(
                                        src=targets[target]['image'],
                                        fit=ft.ImageFit.CONTAIN,
                                        height=120,
                                        error_content=ft.ProgressRing()
                                    ),
                                    ),
                                    ft.Text(targets[target]['title'], size=20, font_family="Geologica", weight=ft.FontWeight.W_500),
                                    ft.Text(description, size=18, font_family="Geologica")
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            expand=True,
                            padding=15
                        ),
                        elevation=10,
                        width=800,
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def get_jury_link(e: ft.ControlEvent):
        page.set_clipboard(labels['elements']['bot_link'].format(e.control.data))
        open_snackbar(labels['snack_bars']['link_copied'])

    def goto_edit_topic(e: ft.ControlEvent):
        topic = e.control.data
        topic_description.value = topic['description']
        edit_topic_dialog.actions[-1].data = topic['topic_id']

        open_dialog(edit_topic_dialog)

    def goto_stats():
        page.controls[-1].content.controls.pop(0)
        get_stats()
        open_snackbar(labels['snack_bars']['data_updated'])

    def show_part_list(e: ft.ControlEvent):
        statuses = {
            'captain': {
                'icon': ft.Icon(ft.icons.HIKING_SHARP),
                'title': "Капитан"
            },
            'part': {
                'icon': ft.Icon(ft.icons.ACCOUNT_CIRCLE_ROUNDED),
                'title': "Участник"
            },
        }
        part_list = e.control.data
        participants_dialog.content = ft.Column(
            width=500,
            height=300,
            scroll=ft.ScrollMode.ADAPTIVE
        )
        participants_dialog.data = part_list
        for index, part in enumerate(part_list):
            participants_dialog.content.controls.append(
                ft.Container(
                    ft.ListTile(
                        # leading=statuses[part['status']]['icon'],
                        title=ft.Text(f"{part['name']}", size=18),
                        # title=ft.TextButton(part['name'], on_click=lambda _: page.set_clipboard(part)),
                        subtitle=ft.Text(part['study_group'], size=16)
                    ),
                    margin=ft.margin.only(top=-20)
                )
            )
        open_dialog(participants_dialog)

    def change_navbar_tab(e):
        global current_tab_index
        if type(e) == int:
            tab_index = e
        else:
            tab_index = e.control.selected_index

        page.clean()
        page.appbar.actions.clear()

        appbar.leading = ft.IconButton(
            icon=screens['main']['lead_icon'],
            on_click=lambda _: change_screen(screens['main']['target'])
        )
        tab = tabs_config[tab_index]
        appbar.title.value = tab['title']
        page.scroll = tab['scroll']
        page.floating_action_button = None

        if tab_index in [0, 1, 2]:
            open_loading_snackbar(labels['snack_bars']['loading'])
            time.sleep(1)

        if tab['fab'] is not None:
            page.floating_action_button = ft.FloatingActionButton(
                text=tab['fab_text'],
                icon=tab['fab_icon'],
                on_click=lambda _: change_screen(tab['fab_target'])
            )

        if tab_index == 0:
            get_topics()
        elif tab_index == 1:
            get_groups()
        elif tab_index == 2:
            get_jury()
        elif tab_index == 3:
            page.add(
                ft.Container(
                    content=ft.ResponsiveRow(
                        [

                            ft.Card(
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Container(title_text("Удаление данных"), margin=ft.margin.only(bottom=20)),
                                            settings_tile(
                                                title="Темы",
                                                descr="Удаляются все темы, которые находятся в базе данных",
                                                icon=ft.Icon(ft.icons.TOPIC_ROUNDED),
                                                btn_text="Удалить темы",
                                                btn_data='delete_manytopic',
                                                btn_action=confirm_delete
                                            ),
                                            settings_tile(
                                                title="Группы",
                                                descr="Удаляются все участники, загруженные видео, очищается список групп, в том числе рейтинг",
                                                icon=ft.Icon(ft.icons.GROUPS_ROUNDED, size=30),
                                                btn_text="Удалить группы",
                                                btn_data='delete_manysgroups',
                                                btn_action=confirm_delete
                                            ),
                                            settings_tile(
                                                title="Жюри",
                                                descr="Удаляется всё жюри с потерей доступа к оцениваю работ",
                                                icon=ft.Icon(ft.icons.EMOJI_PEOPLE_ROUNDED, size=30),
                                                btn_text="Удалить жюри",
                                                btn_data='delete_manyjury',
                                                btn_action=confirm_delete
                                            )
                                        ]
                                    ),
                                    padding=15
                                ),
                                elevation=10,
                                width=450,
                                # height=500,
                                col={"lg": 1}
                            ),

                            ft.Card(
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Container(title_text("Авторизация"), margin=ft.margin.only(bottom=20)),
                                            settings_tile(
                                                title="OAuth-токен",
                                                descr="Токен для связи бота с Яндекс.Диском",
                                                icon=ft.Image(src='yadisk.png', fit=ft.ImageFit.FIT_HEIGHT, height=30),
                                                btn_text="Изменить токен",
                                                btn_data='OAUTH_TOKEN',
                                                btn_action=get_update_params
                                            ),
                                            settings_tile(
                                                title="Bot-токен",
                                                descr="Токен для связи с Telegram API",
                                                icon=ft.Icon(ft.icons.TELEGRAM_ROUNDED, color='#2AABEE', size=30),
                                                btn_text="Изменить токен",
                                                btn_data='BOT_TOKEN',
                                                btn_action=get_update_params
                                            ),
                                            settings_tile(
                                                title="Пароль",
                                                descr="Пароль для входа в панель управления и подтверждения действий",
                                                icon=ft.Icon(ft.icons.PASSWORD_ROUNDED, color='#2AABEE', size=30),
                                                btn_text="Изменить пароль",
                                                btn_data='PASSWORD',
                                                btn_action=get_update_params
                                            )
                                        ]
                                    ),
                                    padding=15
                                ),
                                elevation=10,
                                width=450,
                                # height=500,
                                col={"lg": 1}
                            )
                        ],
                        columns=3,
                        alignment=ft.MainAxisAlignment.START,
                        width=1200
                        # horizontal_alignment=ft.CrossAxisAlignment.START
                    ),
                    # expand=True
                )
            )
            get_stats()

        page.update()

    def statistic_tile(title: str, descr: str):
        tile = ft.ListTile(
            title=ft.Row(
                [
                    # icon,
                    ft.Text(title, size=18, font_family="Geologica", weight=ft.FontWeight.W_400)
                ]
            ),
            subtitle=ft.Column(
                [
                    ft.Text(descr, size=20, weight=ft.FontWeight.W_600),
                ]
            ),
        )
        return ft.Container(tile, margin=ft.margin.only(top=-15))

    def settings_tile(title: str, descr: str, btn_text: str, btn_action, icon, btn_data: str):
        tile = ft.ListTile(
            title=ft.Row(
                [
                    icon,
                    ft.Text(title, size=18, font_family="Geologica", weight=ft.FontWeight.W_400)
                ]
            ),
            subtitle=ft.Column(
                [
                    ft.Text(descr, size=16),
                    ft.ElevatedButton(
                        width=200,
                        text=btn_text,
                        data=btn_data,
                        on_click=btn_action
                    )
                ]
            ),
        )
        return ft.Container(tile, margin=ft.margin.only(top=-15))

    def validate_param(e: ft.ControlEvent):
        if param_field.value:
            edit_params_dialog.actions[0].disabled = False
        else:
            edit_params_dialog.actions[0].disabled = True
        page.update()

    def validate_topic_name(e: ft.ControlEvent):
        if new_topic_field.value:
            btn_add_topic.disabled = False
        else:
            btn_add_topic.disabled = True
        page.update()

    param_field = ft.TextField(
        password=True,
        can_reveal_password=False,
        border_width=3,
        hint_text='Введите значение параметра',
        on_change=validate_param
    )

    def validate_jury_field(e: ft.ControlEvent):
        print(len(jury_name_field.value.strip().split(" ")))
        if len(jury_name_field.value.strip().split(" ")) in [2, 3]:
            new_jury_card.content.content.controls[-1].controls[-1].disabled = False
        else:
            new_jury_card.content.content.controls[-1].controls[-1].disabled = True
        page.update()

    def check_param(e: ft.ControlEvent):
        edit_params_dialog.actions[0].text = "Проверяем"
        edit_params_dialog.actions[0].disabled = True
        page.update()
        param = e.control.data
        url, headers = "", {}

        if param == 'OAUTH_TOKEN':
            url = "https://cloud-api.yandex.net/v1/disk"
            headers = {
                'Accept': 'application/json',
                'Authorization': f'OAuth {param_field.value}'
            }
        elif param == 'BOT_TOKEN':
            url = f"https://api.telegram.org/bot{param_field.value}/getMe"

        print(url)
        print(headers)
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            param_field.border_color = ft.colors.GREEN
            edit_params_dialog.actions[-1].disabled = False
        else:
            param_field.border_color = ft.colors.RED
            edit_params_dialog.actions[-1].disabled = True
        param_field.helper_text = f"Код ответа: {response.status_code}"

        edit_params_dialog.actions[0].disabled = False
        edit_params_dialog.actions[0].text = "Проверить"

        page.update()
        time.sleep(3)
        param_field.border_color = None
        param_field.helper_text = ''
        page.update()

    def update_env_var(variable, value):
        parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_file_path = os.path.join(parent_directory, '.env')
        with open(env_file_path, 'r') as file:
            lines = file.readlines()

        for i in range(len(lines)):
            if lines[i].startswith(f'{variable}='):
                lines[i] = f'{variable}={value}\n'

        with open(env_file_path, 'w') as file:
            file.writelines(lines)

    def update_param(e: ft.ControlEvent):
        param = e.control.data
        update_env_var(param, param_field.value)
        close_dialog(edit_params_dialog)
        open_snackbar(labels['snack_bars']['data_updated'])

    def add_jury(e: ft.ControlEvent):
        pass_phrase = hashlib.sha1(str(uuid.uuid4()).encode('utf-8')).hexdigest()[:15]
        print(pass_phrase)
        get_from_db(f"INSERT INTO jury (name, pass_phrase) VALUES ('{jury_name_field.value}', '{pass_phrase}')")
        jury_name_field.value = ''
        change_screen("main")
        change_navbar_tab(2)
        new_jury_card.content.content.controls[-1].controls[-1].disabled = True

    def get_update_params(e: ft.ControlEvent):
        param = e.control.data
        params = {
            'OAUTH_TOKEN': {
                'label': "OAuth-токен",
                'icon': ft.Image(src='yadisk.png', fit=ft.ImageFit.FIT_HEIGHT, height=30)
            },
            'BOT_TOKEN': {
                'label': "Bot-токен",
                'icon': ft.Icon(ft.icons.TELEGRAM_ROUNDED, color='#2AABEE', size=30)
            },
            'PASSWORD': {
                'label': "Пароль",
                'icon': ft.Icon(ft.icons.PASSWORD_ROUNDED, color='#2AABEE', size=30)
            }
        }
        param_field.label = params[param]['label']
        # param_field.value = os.getenv(param)
        edit_params_dialog.actions[-1].data = param
        edit_params_dialog.actions[0].data = param
        if param in ['OAUTH_TOKEN', 'BOT_TOKEN']:
            edit_params_dialog.actions[-1].disabled = True
            edit_params_dialog.actions[0].visible = True
        else:
            edit_params_dialog.actions[-1].disabled = False
            edit_params_dialog.actions[0].visible = False
        param_field.value = ""
        open_dialog(edit_params_dialog)

    def change_screen(target: str):
        page.navigation_bar = None
        page.floating_action_button = None
        page.clean()

        if target in screens.keys():
            appbar.title.value = screens[target]['title']
            appbar.leading = ft.IconButton(
                icon=screens[target]['lead_icon'],
                on_click=lambda _: change_screen(screens[target]['target'])
            )
        if target == "login":
            page.scroll = None
            page.appbar = None
            page.add(ft.Container(login_col, expand=True), )  # footer)

        elif target == "main":
            page.appbar = appbar
            page.navigation_bar = navbar
            change_navbar_tab(page.navigation_bar.selected_index)

        elif target == "add_jury":
            page.navigation_bar = navbar
            page.add(new_jury_card)

        elif target == "import_themes":
            page.navigation_bar = navbar
            elements.global_vars.ACCESS_CODE = ''.join(random.choice('0123456789ABCDEF') for _ in range(15))
            page.add(import_topics_col)

        # elif target == "error":
        #     page.add(ft.Container(error_col, expand=True), )  # footer)

        page.update()

    def validate_login(e):
        if all([login_field.value, password_field.value]):
            button_login.disabled = False
        else:
            button_login.disabled = True
        page.update()

    appbar = ft.AppBar(
        title=ft.Text(),
        bgcolor=ft.colors.SURFACE_VARIANT
    )

    def validate_description_field():
        if topic_description.value:
            edit_topic_dialog.actions[-1].disabled = False
        else:
            edit_topic_dialog.actions[-1].disabled = True
        page.update()

    def copy_part():
        text = ""
        for index, part in enumerate(participants_dialog.data):
            text += f"{index + 1}. {part['name']} ({part['study_group']})\n"

        page.set_clipboard(text)
        close_dialog(participants_dialog)
        open_snackbar(labels['snack_bars']['group_list_copied'])

    def copy_error_text(e: ft.ControlEvent):
        page.set_clipboard(elements.global_vars.ERROR_TEXT)
        open_snackbar(labels['snack_bars']['error_text_copied'])

    def title_text(text: str):
        return ft.Text(text, size=20, font_family="Geologica", weight=ft.FontWeight.W_700,
                       text_align=ft.TextAlign.CENTER)

    def update():
        if platform.system() == 'Windows':
            open_snackbar(labels['snack_bars']['action_unavaliable'])
        else:
            open_dialog(loading_dialog)
            os.system("/root/controlupdate.sh")

    def login():
        auth_data = load_config_file("config.json")['auth']
        if login_field.value.strip() == auth_data['login'] and password_field.value.strip() == os.getenv('PASSWORD'):
            password_field.value = ""
            open_snackbar(labels['snack_bars']['welcome'], bg_color=ft.colors.GREEN, text_color=ft.colors.WHITE)
            change_screen("main")
        else:
            open_snackbar(labels['snack_bars']['wrong_login'], bg_color=ft.colors.RED, text_color=ft.colors.WHITE)

    def open_dialog(dialog: ft.AlertDialog):
        page.dialog = dialog
        dialog.open = True
        page.update()

    def close_dialog(dialog: ft.AlertDialog):
        dialog.open = False
        page.update()

    def get_current_commit_hash():
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE)
            return result.stdout.decode('utf-8').strip()[:7]
        except Exception as e:
            return e

    def confirm_delete(e: ft.ControlEvent):
        print('data', e.control.data)
        confirmation_dialog.actions[-1].data = e.control.data
        open_dialog(confirmation_dialog)

    def check_confirm(e: ft.ControlEvent):
        if confirm_field.value == str(datetime.datetime.now().date()).replace('-', ''):
            close_dialog(confirmation_dialog)

            action = e.control.data.split("_")[0]
            if action == 'delete':
                delete_element(e.control.data.split("_")[1:])

            confirm_field.value = ''
        else:
            confirm_field.border_color = ft.colors.RED
            page.update()
            time.sleep(2)
            confirm_field.border_color = None
            page.update()

    def delete_element(data):
        print(data)
        if not data[0].startswith('many'):
            get_from_db(f"DELETE FROM {data[0]} WHERE {data[0]}_id = {data[1]}")
            for index, card in enumerate(page.controls[-1].controls):
                if card.data == int(data[1]):
                    page.controls[-1].controls.pop(index)
                    if len(page.controls[-1].controls) == 0:
                        show_error('empty_list', labels['errors']['empty_list'])
                    page.update()
                    break
            open_snackbar(labels['snack_bars']['element_deleted'])
        else:
            table = data[0].split('many')[-1]
            get_from_db(f'TRUNCATE TABLE {table}')
            if table == 'sgroups':
                get_from_db("UPDATE topic SET status = 'free' WHERE status = 'busy'")
                get_from_db(f'TRUNCATE TABLE participants')
            open_snackbar(labels['snack_bars']['table_deleted'])

    def update_topic(e: ft.ControlEvent):
        get_from_db(f"UPDATE topic SET description = '{topic_description.value}' WHERE topic_id = {e.control.data}")
        close_dialog(edit_topic_dialog)
        open_snackbar(labels['snack_bars']['data_edited'])

    participants_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Container(ft.Text(labels['elements']['part_list'], size=20, font_family="Geologica", weight=ft.FontWeight.W_700), expand=True),
                ft.IconButton(ft.icons.CLOSE_ROUNDED, on_click=lambda _: close_dialog(participants_dialog))
            ]
        ),
        content=ft.Column(
            height=300,
            width=600
        ),
        actions_alignment=ft.MainAxisAlignment.END,
        actions=[
            ft.ElevatedButton(
                text=labels['buttons']['copy'],
                icon=ft.icons.COPY_ROUNDED,
                on_click=lambda _: copy_part()
            )
        ]
    )

    topic_description = ft.TextField(
        prefix_icon=ft.icons.TEXT_FIELDS_SHARP,
        label="Название",
        hint_text="Введите название темы",
        on_change=lambda _: validate_description_field(),
    )

    confirm_field = ft.TextField(
        label='Код подтверждения',
        hint_text='Введите код подтверждения',
        text_align=ft.TextAlign.CENTER,
        border_width=3
    )

    confirmation_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Container(ft.Text("Подтверждение действия", size=20, font_family="Geologica", weight=ft.FontWeight.W_700), expand=True),
                ft.IconButton(ft.icons.CLOSE_ROUNDED, on_click=lambda _: close_dialog(confirmation_dialog))
            ]
        ),
        content=ft.Column(
            [
                ft.Text(f"Чтобы подтвердить своё действие, введите в окно {str(datetime.datetime.now().date()).replace('-', '')}", size=18),
                confirm_field
            ],
            width=350,
            height=150
        ),
        actions=[
            ft.ElevatedButton(
                text="Подтвердить",
                icon=ft.icons.CHECK_ROUNDED,
                on_click=check_confirm
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    edit_params_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Container(ft.Text(labels['elements']['edit_params_title'], size=20, font_family="Geologica", weight=ft.FontWeight.W_700), expand=True),
                ft.IconButton(ft.icons.CLOSE_ROUNDED, on_click=lambda _: close_dialog(edit_params_dialog))
            ]
        ),
        content=ft.Column(
            [
                param_field
            ],
            width=700,
            height=60
        ),
        actions=[
            ft.ElevatedButton(
                text=labels['buttons']['check'],
                icon=ft.icons.CHECK_ROUNDED,
                on_click=check_param,
                visible=False,
                disabled=True
            ),
            ft.ElevatedButton(
                text=labels['buttons']['save'],
                icon=ft.icons.SAVE_ROUNDED,
                on_click=update_param,
                disabled=True
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END

    )

    edit_topic_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Container(ft.Text(labels['elements']['edit_topic_title'], size=20, font_family="Geologica", weight=ft.FontWeight.W_700), expand=True),
                ft.IconButton(ft.icons.CLOSE_ROUNDED, on_click=lambda _: close_dialog(edit_topic_dialog))
            ]
        ),
        content=ft.Column(
            controls=[
                topic_description
            ],
            height=60,
            width=700
        ),
        actions_alignment=ft.MainAxisAlignment.END,
        actions=[
            ft.ElevatedButton(
                text=labels['buttons']['save'],
                icon=ft.icons.SAVE_ROUNDED,
                on_click=update_topic
            )
        ]

    )

    loading_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(),
        content=ft.Column(
            width=100,
            height=100,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.ProgressRing(),
                ft.Container(ft.Text(labels['elements']['loading'], size=20, font_family="Geologica", weight=ft.FontWeight.W_500), margin=ft.margin.only())
            ]
        )
    )

    navbar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.TOPIC_ROUNDED, label=tabs_config[0]['title']),
            ft.NavigationDestination(icon=ft.icons.GROUPS_2_ROUNDED, label=tabs_config[1]['title']),
            ft.NavigationDestination(icon=ft.icons.EMOJI_PEOPLE_ROUNDED, label=tabs_config[2]['title']),
            ft.NavigationDestination(icon=ft.icons.SETTINGS_ROUNDED, label=tabs_config[3]['title']),
        ],
        on_change=change_navbar_tab
    )

    login_field = ft.TextField(
        label=labels['fields']['login'], text_align=ft.TextAlign.LEFT,
        width=250, on_change=validate_login,
        height=70
    )
    password_field = ft.TextField(
        label=labels['fields']['password'], text_align=ft.TextAlign.LEFT,
        width=250, password=True, on_change=validate_login,
        can_reveal_password=True, height=70, on_submit=lambda _: login(),
    )
    button_login = ft.ElevatedButton(labels['buttons']['login'], width=250, on_click=lambda _: login(),
                                     disabled=True, height=50,
                                     icon=ft.icons.KEYBOARD_ARROW_RIGHT_ROUNDED,
                                     on_long_press=None)
    button_update = ft.OutlinedButton(labels['buttons']['update_project'], width=250, on_click=lambda _: update(), height=50)

    login_col = ft.Column(
        controls=[
            # ft.Container(
            #     ft.Lottie(
            #         src='https://lottie.host/bbf984e1-7cba-417a-8a6f-472105c726b0/joNPBJ5N73.json',
            #         # on_error=lambda _: open_snackbar("3453454")
            #         background_loading=True,
            #         scale=0.2
            #     ),
            #     margin=ft.margin.all(-460)
            # ),
            ft.Container(ft.Image(src="logo.png",
                                  fit=ft.ImageFit.CONTAIN,
                                  height=200,
                                  error_content=ft.ProgressRing()
                                  ),
                         ),
            login_field,
            password_field,
            button_login,
            # button_update,
            # ft.Text("login: admin | password: admin")
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    jury_name_field = ft.TextField(
        label="ФИО",
        hint_text="Иванов Иван Иванович",
        on_change=validate_jury_field
    )

    new_jury_card = ft.Card(
        ft.Container(
            content=ft.Column(
                [
                    ft.Container(jury_name_field, expand=True),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                text=labels['buttons']['add'],
                                icon=ft.icons.ADD_ROUNDED,
                                on_click=add_jury,
                                disabled=True

                            )
                        ],
                        alignment=ft.MainAxisAlignment.END
                    )
                ],
                width=600,
                height=120
            ),
            padding=15
        ),
        elevation=10
    )

    btn_add_topic = ft.ElevatedButton(labels['buttons']['save'], icon=ft.icons.SAVE_ROUNDED, disabled=True, on_click=save_new_topic)
    new_topic_field = ft.TextField(label="Тема", hint_text="Введите описание темы", on_change=validate_topic_name)

    import_topics_col = ft.Container(
        ft.Column(
            controls=[
                ft.Card(
                    ft.Container(
                        content=ft.Column(
                            [
                                title_text('Одиночное добавление'),
                                new_topic_field,
                                ft.Row([btn_add_topic], alignment=ft.MainAxisAlignment.END)
                            ],
                            width=700,
                            height=150
                        ),
                        padding=15
                    ),
                    elevation=10
                ),
                ft.Card(
                    ft.Container(
                        content=ft.Column(
                            [
                                title_text('Массовая загрузка'),
                                ft.Text(f"Скопируйте код подключения, после чего откройте форму и вставьте список тем, не забудьте вставить скопированный код подключения", size=18),
                                ft.Row([
                                    ft.ElevatedButton(labels['buttons']['copy_code'], icon=ft.icons.COPY_ROUNDED, on_click=lambda _: page.set_clipboard(elements.global_vars.ACCESS_CODE)),
                                    ft.ElevatedButton(labels['buttons']['upload'], icon=ft.icons.FILE_UPLOAD_ROUNDED, url='https://forms.yandex.ru/u/661287c843f74fd25dec9fbc')
                                ]),

                            ],
                            width=700,
                            height=150
                        ),
                        padding=15
                    ),
                    elevation=10
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        # expand=True,
    )

    vertext = ft.Text(
        value=None,
        text_align=ft.TextAlign.START,
        size=16
    )
    footer = ft.Row(
        controls=[
            vertext
        ],
        alignment=ft.MainAxisAlignment.START
    )

    vertext.value = labels['elements']['app_version'].format(get_current_commit_hash())

    if elements.global_vars.DB_FAIL:
        show_error('db', labels['errors']['db_connection'].format(elements.global_vars.ERROR_TEXT.split(":")[0]))
    else:
        change_screen("login")

    page.update()


DEFAULT_FLET_PATH = ''
DEFAULT_FLET_PORT = 8502

if __name__ == "__main__":
    connection, cur = create_db_connection()
    if platform.system() == 'Windows':
        ft.app(assets_dir='assets', target=main, use_color_emoji=True, upload_dir='assets/uploads')
    else:
        flet_path = os.getenv("FLET_PATH", DEFAULT_FLET_PATH)
        flet_port = int(os.getenv("FLET_PORT", DEFAULT_FLET_PORT))
        ft.app(name=flet_path, target=main, view=None, port=flet_port, assets_dir='assets', use_color_emoji=True, upload_dir='assets/uploads')
