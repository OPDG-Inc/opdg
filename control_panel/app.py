import datetime
import hashlib
import os
import platform
import random
import subprocess
import time
import uuid
import logging

import flet as ft
import flet_core
import requests
from mysql.connector import connect, Error as sql_error
from dotenv import load_dotenv

from functions import load_config_file, update_config_file
from elements.screens import screens
from elements.tabs import tabs_config
from elements.errors_targets import targets

import elements.global_vars
from elements.text import labels

current_tab_index = -1
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")


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
        logging.error(f"DATABASE CONNECTION: {e}")
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
        "Geologica": "fonts/Geologica.ttf",
    }

    page.window_width = 377
    page.window_height = 768

    def save_new_topic(e: ft.ControlEvent):
        topic = new_topic_field.value.strip()
        sql_query = "INSERT INTO topic (description) VALUES (%s)"
        params = (topic,)
        make_db_request(sql_query, params, put_many=False)
        new_topic_field.value = ''
        btn_add_topic.disabled = True

        open_snackbar(labels['snack_bars']['topic_added'])

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

    def make_db_request(sql_query: str, params: tuple = (), get_many: bool = None, put_many: bool = None):
        connection, cur = create_db_connection()
        if connection is not None:
            logging.info(f"DATABASE REQUEST: query: {sql_query}, params: {params}")
            try:
                data = True
                if get_many is not None:
                    cur.execute(sql_query, params)
                    if get_many:
                        data = cur.fetchall()
                    elif not get_many:
                        data = cur.fetchone()
                elif put_many is not None:
                    if put_many:
                        cur.executemany(sql_query, params)
                    elif not put_many:
                        cur.execute(sql_query, params)
                    data = True
                connection.commit()
                return data
            except Exception as e:
                elements.global_vars.ERROR_TEXT = str(e)
                elements.global_vars.DB_FAIL = True
                logging.error(f"DATABASE REQUEST: {e}\n{sql_query}{params}")
                if page.navigation_bar.selected_index != 3:
                    page.floating_action_button = None
                    show_error('db_request', labels['errors']['db_request'].format(elements.global_vars.ERROR_TEXT.split(":")[0]))
                    elements.global_vars.DB_FAIL = False
                return None
        else:
            if page.navigation_bar.selected_index != 3:
                page.floating_action_button = None
                show_error('db_request', labels['errors']['db_request'].format(elements.global_vars.ERROR_TEXT.split(":")[0]))
                elements.global_vars.DB_FAIL = False
                return None

    group_count = ft.Text(size=20, weight=ft.FontWeight.W_600)
    part_count = ft.Text(size=20, weight=ft.FontWeight.W_600)
    videos_count = ft.Text(size=20, weight=ft.FontWeight.W_600)

    app_ver = ft.Text(size=16, weight=ft.FontWeight.W_300)
    db_status = ft.Text(size=16, weight=ft.FontWeight.W_300)
    flask_status = ft.Text(size=16, weight=ft.FontWeight.W_300)
    bot_status = ft.Text(size=16, weight=ft.FontWeight.W_300)
    disk_status = ft.Text(size=16, weight=ft.FontWeight.W_300)

    def get_stats():
        if not elements.global_vars.DB_FAIL:
            sql_query = "SELECT COUNT(*) FROM sgroups"
            data = make_db_request(sql_query, get_many=False)
            if data is not None:
                group_count.value = data['COUNT(*)']

            sql_query = "SELECT COUNT(*) FROM participants"
            data = make_db_request(sql_query, get_many=False)
            if data is not None:
                part_count.value = data['COUNT(*)']

            sql_query = "SELECT COUNT(*) FROM sgroups WHERE video_status = 'uploaded'"
            data = make_db_request(sql_query, get_many=False)
            if data is not None:
                videos_count.value = data['COUNT(*)']

        else:
            group_count.value = labels['elements']['is_disabled']
            part_count.value = labels['elements']['is_disabled']
            videos_count.value = labels['elements']['is_disabled']
        page.update()

    def get_app_info():
        time.sleep(1)

        # db
        sql_query = "SELECT COUNT(*) FROM topic"
        if make_db_request(sql_query, get_many=False):
            db_status.value = labels['elements']['is_active']
            app_info_elements['db'].content.subtitle.controls[-1].visible = False
        else:
            db_status.value = labels['elements']['is_disabled']
            app_info_elements['db'].content.subtitle.controls[-1].visible = True

        # flask
        try:
            response = requests.get(url='http://localhost:5000/check')
            if response.status_code == 200:
                flask_status.value = labels['elements']['is_active']
                app_info_elements['flask'].content.subtitle.controls[-1].visible = False
            else:
                flask_status.value = labels['elements']['is_not_working'].format(response.status_code)
                app_info_elements['flask'].content.subtitle.controls[-1].visible = True
        except requests.exceptions.ConnectionError:
            flask_status.value = labels['elements']['is_disabled']
            app_info_elements['flask'].content.subtitle.controls[-1].visible = True

        # bot
        if True:
            bot_status.value = labels['elements']['is_active']
            app_info_elements['bot'].content.subtitle.controls[-1].visible = False
        else:
            bot_status.value = labels['elements']['is_disabled']
            app_info_elements['bot'].content.subtitle.controls[-1].visible = True

        # disk
        headers = {
            'Accept': 'application/json',
            'Authorization': f"OAuth {os.getenv('OAUTH_TOKEN')}"
        }
        try:
            response = requests.get(url="https://cloud-api.yandex.net/v1/disk", headers=headers)
            if response.status_code == 200:
                disk_status.value = labels['elements']['is_active']
            else:
                disk_status.value = labels['elements']['is_not_working'].format(response.status_code)
        except requests.exceptions.ConnectionError:
            disk_status.value = labels['elements']['is_disabled']

        # app ver
        if platform.system() == 'Windows':
            app_ver.value = str(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=parent_directory))[2:9]
        else:
            app_ver.value = str(subprocess.check_output(['/usr/bin/git', 'rev-parse', 'HEAD'], cwd=parent_directory))[2:9]

        page.update()

    def get_groups():
        time.sleep(0.5)
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
        # rr = ft.ResponsiveRow(columns=4)
        rr = ft.ListView(
            opacity=0,
            animate_opacity=300,
            width=800
        )
        page.add(rr)
        page.update()

        sql_query = "SELECT * FROM sgroups"
        groups_list = make_db_request(sql_query, (), get_many=True)
        if groups_list is not None:
            if len(groups_list) > 0:
                for group in groups_list:

                    sql_query = "SELECT * FROM topic WHERE topic_id = %s"
                    topic_info = make_db_request(sql_query, (group['topic_id'],), get_many=False)

                    sql_query = "SELECT * FROM participants WHERE group_id = %s"
                    participants_info = make_db_request(sql_query, (group['group_id'],), get_many=True)

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
                rr.opacity = 1
            else:
                show_error('empty_groups', labels['errors']['empty_groups'])

        page.update()

    def get_topics():
        time.sleep(0.5)
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

        # rr = ft.ResponsiveRow(columns=3)
        rr = ft.ListView(
            animate_opacity=300,
            opacity=0, width=800
        )
        page.add(rr)
        page.update()

        sql_query = "SELECT * from topic"
        topics_list = make_db_request(sql_query, get_many=True)
        if topics_list is not None:
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
                                        )
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
                                            )
                                        ],
                                        alignment=ft.MainAxisAlignment.END
                                    )
                                ]
                            ),
                            padding=15
                        ),
                        elevation=10,
                        col={"lg": 1},
                        data=topic['topic_id']
                    )
                    rr.controls.append(topic_card)
                rr.opacity = 1
            else:
                show_error('empty_topics', labels['errors']['empty_topics'])

        page.update()

    def get_jury():
        time.sleep(0.5)
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
        rr = ft.ListView(opacity=0, animate_opacity=300, width=800)

        sql_query = "SELECT * FROM jury"
        jury_list = make_db_request(sql_query, get_many=True)
        if jury_list is not None:
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
                        col={"lg": 1},
                        data=jury['jury_id']
                    )
                    rr.controls.append(jury_card)
                page.add(rr)
            else:
                show_error('empty_jury', labels['errors']['empty_jury'])

            page.update()
            rr.opacity = 1
        page.update()

    def show_error(target: str, description: str):
        # page.scroll = None
        # page.controls.clear()
        err_col = ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            opacity=0,
            animate_opacity=300
        )
        # page.add(err_col)
        # page.update()
        col = ft.Column(
            [
                ft.Container(ft.Image(
                    src=targets[target]['image'],
                    fit=ft.ImageFit.CONTAIN,
                    height=100,
                    error_content=ft.ProgressRing()
                ),
                ),
                ft.Text(targets[target]['title'], size=20, font_family="Geologica", weight=ft.FontWeight.W_500),
                ft.Column([
                    ft.Text(description, size=18, font_family="Geologica", text_align=ft.TextAlign.CENTER)
                ],
                    width=600,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ],
            width=600,
            height=230,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        err_dialog = ft.AlertDialog(
            title=ft.Row([ft.IconButton(ft.icons.CLOSE_ROUNDED, on_click=lambda _: close_dialog(err_dialog))], expand=True, alignment=ft.MainAxisAlignment.END),
            modal=True,
            actions_alignment=ft.MainAxisAlignment.END,
            # actions=[ft.ElevatedButton("Закрыть", icon=ft.icons.CLOSE_ROUNDED, on_click=lambda _:close_dialog(err_dialog))],
            content=col
        )

        open_dialog(err_dialog)
        # err_col.controls = [
        #     ft.Card(
        #         ft.Container(
        #             ft.Column(
        #                 [
        #                     ft.Container(ft.Image(
        #                         src=targets[target]['image'],
        #                         fit=ft.ImageFit.CONTAIN,
        #                         height=120,
        #                         error_content=ft.ProgressRing()
        #                     ),
        #                     ),
        #                     ft.Text(targets[target]['title'], size=20, font_family="Geologica", weight=ft.FontWeight.W_500),
        #                     ft.Column([
        #                         ft.Text(description, size=18, font_family="Geologica", text_align=ft.TextAlign.CENTER)
        #                     ],
        #                         width=800,
        #                         alignment=ft.MainAxisAlignment.CENTER,
        #                         horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        #                 ],
        #                 alignment=ft.MainAxisAlignment.CENTER,
        #                 horizontal_alignment=ft.CrossAxisAlignment.CENTER
        #             ),
        #             expand=True,
        #             padding=15
        #         ),
        #         elevation=10,
        #         width=800,
        #     )
        # ]

        # err_col.opacity = 1
        # page.update()

    def get_jury_link(e: ft.ControlEvent):
        page.set_clipboard(labels['elements']['bot_link'].format(e.control.data))
        open_snackbar(labels['snack_bars']['link_copied'])

    def goto_edit_topic(e: ft.ControlEvent):
        topic = e.control.data
        topic_description.value = topic['description']
        edit_topic_dialog.actions[-1].data = topic['topic_id']

        open_dialog(edit_topic_dialog)

    def goto_stats():
        get_stats()
        # open_snackbar(labels['snack_bars']['data_updated'])

    def make_loading():
        db_status.value = labels['elements']['status_loading']
        app_ver.value = labels['elements']['status_loading']
        flask_status.value = labels['elements']['status_loading']
        bot_status.value = labels['elements']['status_loading']
        disk_status.value = labels['elements']['status_loading']
        page.update()

    def goto_info():
        make_loading()
        get_app_info()

    def show_part_list(e: ft.ControlEvent):
        # statuses = {
        #     'captain': {
        #         'icon': ft.Icon(ft.icons.HIKING_SHARP),
        #         'title': "Капитан"
        #     },
        #     'part': {
        #         'icon': ft.Icon(ft.icons.ACCOUNT_CIRCLE_ROUNDED),
        #         'title': "Участник"
        #     },
        # }
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
                        title=ft.Text(f"{part['name']}", size=18),
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

        if tab_index != current_tab_index:
            current_tab_index = page.navigation_bar.selected_index
            page.controls.clear()
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
                # open_dialog(loading_dialog)
                time.sleep(1)

            if tab['fab'] is not None:
                page.floating_action_button = ft.FloatingActionButton(
                    text=tab['fab_text'],
                    icon=tab['fab_icon'],
                    on_click=lambda _: change_screen(tab['fab_target'])
                )
            page.update()

            if tab_index == 0:
                get_topics()
            elif tab_index == 1:
                get_groups()
            elif tab_index == 2:
                get_jury()
            elif tab_index == 3:
                settings_col.opacity = 0

                goto_stats()
                page.add(
                    ft.Container(
                        content=settings_col
                    )
                )
                page.update()

                settings_col.opacity = 1
                goto_info()

        page.update()

    def statistic_tile(title: str, descr: ft.Text):
        tile = ft.ListTile(
            title=ft.Row(
                [ft.Text(title, size=18, font_family="Geologica", weight=ft.FontWeight.W_400)]
            ),
            subtitle=ft.Column(
                [descr]
            ),
        )
        return ft.Container(tile, margin=ft.margin.only(top=-15))

    def reboot_service(e: ft.ControlEvent):
        e.control.visible = False
        scripts = {
            'db': {
                'file': 'rebootmysql',
                'name': labels['titles']['db_status']
            },
            'flask': {
                'file': 'rebootflash',
                'name': labels['titles']['flask_status']
            },
            'bot': {
                'file': 'rebootbot',
                'name': labels['titles']['bot_status']
            },
            'controlpanel': {
                'file': 'controlupdate',
                'name': labels['titles']['control_panel']
            }
        }
        if e.control.data == 'controlpanel':
            reboot_dialog.content = ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text(labels['elements']['rebooting'], size=20, weight=ft.FontWeight.W_500)
                ],
                height=100,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
            page.update()
        else:
            open_loading_snackbar(f"{scripts[e.control.data]['name']} перезагружается")
            make_loading()
        subprocess.run(['/bin/bash', f"/root/scripts/{scripts[e.control.data]['file']}.sh"])
        time.sleep(3)
        goto_info()

    def app_info_title(title: str, descr: ft.Text, btn_data):
        tile = ft.ListTile(
            title=ft.Row(
                [ft.Text(title, size=18, font_family="Geologica", weight=ft.FontWeight.W_400)]
            ),
            subtitle=ft.Row(
                [
                    descr,
                    ft.IconButton(ft.icons.RESTART_ALT_ROUNDED, on_click=reboot_service, visible=False, tooltip="Перезагрузка сервиса", data=btn_data)
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
        hint_text=labels['fields_hint']['param'],
        on_change=validate_param
    )

    def validate_jury_field(e: ft.ControlEvent):
        if len(jury_name_field.value.strip().split(" ")) in [2, 3]:
            new_jury_card.content.content.controls[-1].controls[-1].disabled = False
        else:
            new_jury_card.content.content.controls[-1].controls[-1].disabled = True
        page.update()

    def check_param(e: ft.ControlEvent):
        edit_params_dialog.actions[0].text = labels['buttons']['checking']
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

        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            param_field.border_color = ft.colors.GREEN
            edit_params_dialog.actions[-1].disabled = False
        else:
            param_field.border_color = ft.colors.RED
            edit_params_dialog.actions[-1].disabled = True
        param_field.helper_text = f"Код ответа: {response.status_code}"

        edit_params_dialog.actions[0].disabled = False
        edit_params_dialog.actions[0].text = labels['buttons']['check']

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
        time.sleep(0.5)
        open_dialog(reboot_dialog)
        # open_snackbar(labels['snack_bars']['data_updated'])

    def add_jury(e: ft.ControlEvent):
        e.control.disabled = True
        e.control.text = labels['buttons']['adding']
        page.update()
        time.sleep(0.5)

        pass_phrase = hashlib.sha1(str(uuid.uuid4()).encode('utf-8')).hexdigest()[:15]

        sql_query = "INSERT INTO jury (name, pass_phrase) VALUES (%s, %s)"
        if make_db_request(sql_query, (jury_name_field.value, pass_phrase,), put_many=False):
            e.control.text = labels['buttons']['add']
            jury_name_field.value = ''
            change_screen("main")
            change_navbar_tab(2)

    def get_update_params(e: ft.ControlEvent):
        param = e.control.data
        params = {
            'OAUTH_TOKEN': {
                'label': labels['statuses']['oauth_token'],
                'icon': ft.Image(src='yadisk.png', fit=ft.ImageFit.FIT_HEIGHT, height=30)
            },
            'BOT_TOKEN': {
                'label': labels['statuses']['bot_token'],
                'icon': ft.Icon(ft.icons.TELEGRAM_ROUNDED, color='#2AABEE', size=30)
            },
            'PASSWORD': {
                'label': labels['statuses']['password'],
                'icon': ft.Icon(ft.icons.PASSWORD_ROUNDED, color='#2AABEE', size=30)
            }
        }
        param_field.label = params[param]['label']
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
        global current_tab_index
        page.navigation_bar = None
        page.floating_action_button = None
        page.controls.clear()

        if target in screens.keys():
            appbar.title.value = screens[target]['title']
            appbar.leading = ft.IconButton(
                icon=screens[target]['lead_icon'],
                on_click=lambda _: change_screen(screens[target]['target'])
            )
        if target == "login":
            page.scroll = None
            page.appbar = None
            page.add(ft.Container(login_col, expand=True), )

        elif target == "main":
            page.appbar = appbar
            page.navigation_bar = navbar
            current_tab_index = -1
            change_navbar_tab(page.navigation_bar.selected_index)

        elif target == "add_jury":
            page.navigation_bar = navbar
            page.add(new_jury_card)

        elif target == "import_themes":
            page.navigation_bar = navbar

            sql_query = "SELECT COUNT(*) FROM topic"
            if make_db_request(sql_query, get_many=False):
                access_code = ''.join(random.choice('0123456789ABCDEF') for _ in range(15))
                config = load_config_file('config.json')
                config['upload_topic_access_code'] = access_code
                update_config_file(config, 'config.json')

                page.add(import_topics_col)

        page.update()

    def validate_login(e):
        if password_field.value:
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

    def copy_accesscode(e: ft.ControlEvent):
        access_code = load_config_file('config.json')['upload_topic_access_code']
        page.set_clipboard(access_code)
        open_snackbar(labels['snack_bars']['accesscode_copied'])

    def title_text(text: str):
        return ft.Text(text, size=20, font_family="Geologica", weight=ft.FontWeight.W_700,
                       text_align=ft.TextAlign.START)

    def login():
        if password_field.value.strip() == os.getenv('PASSWORD'):
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

    # def get_current_commit_hash():
    #     try:
    #         result = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE)
    #         return result.stdout.decode('utf-8').strip()[:7]
    #     except Exception as e:
    #         return e

    def confirm_delete(e: ft.ControlEvent):
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
        if not data[0].startswith('many'):

            sql_query = f"DELETE FROM {data[0]} WHERE {data[0]}_id = %s"
            if make_db_request(sql_query, (data[1],), put_many=False):
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

            sql_query = F"TRUNCATE TABLE {table}"
            if make_db_request(sql_query, put_many=False):
                if table == 'sgroups':
                    sql_query = "UPDATE topic SET status = %s WHERE status = %s"
                    make_db_request(sql_query, ('free', 'busy',), put_many=False)
                    sql_query = "TRUNCATE TABLE participants"
                    make_db_request(sql_query, put_many=False)
                time.sleep(1)
                open_snackbar(labels['snack_bars']['table_deleted'])

    def update_topic(e: ft.ControlEvent):

        sql_query = "UPDATE topic SET description = %s WHERE topic_id = %s"
        if make_db_request(sql_query, (topic_description.value, e.control.data,)):
            close_dialog(edit_topic_dialog)
            open_snackbar(labels['snack_bars']['data_edited'])

    def register(e):
        btn_register.disabled = True
        open_dialog(loading_dialog)
        sql_query = "INSERT INTO sgroups (name) VALUES (%s)"
        if make_db_request(sql_query, (group_name_field.value,), put_many=False):

            sql_query = "INSERT INTO participants (telegram_id, name, study_group, status) VALUES (%s, %s, %s, %s)"
            make_db_request(sql_query, (user_id, captain_name_field.value, captain_group_field.value, 'captain',), put_many=False)

            sql_query = "SELECT group_id FROM sgroups WHERE name = %s"
            group_id = make_db_request(sql_query, (group_name_field.value,), get_many=False)['group_id']

            sql_query = "UPDATE participants SET group_id = %s WHERE telegram_id = %s"
            make_db_request(sql_query, (group_id, user_id,), put_many=False)

            sql_query = "SELECT participant_id FROM participants WHERE group_id = %s and status = %s"
            captain_id = make_db_request(sql_query, (group_id, 'captain',), get_many=False)['participant_id']

            sql_query = "UPDATE sgroups SET captain_id = %s WHERE group_id = %s"
            make_db_request(sql_query, (captain_id, group_id,), put_many=False)

            sql_query = "INSERT INTO participants (group_id, telegram_id, name, study_group, status) VALUES (%s, %s, %s, %s, %s)"

            participants = [el for el in parts.controls if type(el) == flet_core.textfield.TextField]
            for i in range(0, len(participants), 2):
                part = {}
                part['name'] = participants[i].value
                part['group'] = participants[i + 1].value
                make_db_request(sql_query, (group_id, 0, part['name'], part['group'], 'part',), put_many=False)

            sql_query = "UPDATE sgroups SET topic_id = (SELECT topic_id FROM topic WHERE status != %s ORDER BY RAND() LIMIT 1) WHERE group_id = %s"
            make_db_request(sql_query, ('busy', group_id,), put_many=False)

            sql_query = "UPDATE topic SET status = %s WHERE topic_id = (SELECT topic_id FROM sgroups WHERE group_id = %s)"
            make_db_request(sql_query, ('busy', group_id), put_many=False)
            close_dialog(loading_dialog)
            time.sleep(1)
            open_dialog(confirmation_registration_dialog)
        close_dialog(loading_dialog)

    def validate_registrationfields(e):
        fl = True
        if all([
            group_name_field.value,
            captain_name_field.value,
            captain_group_field.value
        ]):
            fl = False
            for el in parts.controls:
                if type(el) == flet_core.textfield.TextField:
                    if el.value == '':
                        fl = True
                        break
            if fl:
                btn_register.disabled = True
            else:
                btn_register.disabled = False
        else:
            btn_register.disabled = True
        page.update()

    def add_part(e: ft.ControlEvent):
        if len(parts.controls) <= 12:
            parts.controls.append(ft.Divider())
            parts.controls.append(
                ft.TextField(label='ФИО', hint_text='Иванов Иван Иванович', on_change=validate_registrationfields)
            )
            parts.controls.append(
                ft.TextField(label='Номер группы', hint_text='5130904/20002', on_change=validate_registrationfields)
            )
            btn_rem_part.disabled = False
            btn_register.disabled = True
            parts_count.value = str(len(parts.controls) // 3)
            if len(parts.controls) == 15:
                btn_add_part.disabled = True
        page.update()

    def rem_part(e: ft.ControlEvent):
        if len(parts.controls) > 3:
            for _ in range(3):
                parts.controls.pop()
            btn_add_part.disabled = False
            if len(parts.controls) == 3:
                btn_rem_part.disabled = True
            parts_count.value = str(len(parts.controls) // 3)
            validate_registrationfields('1')
        page.update()

    group_name_field = ft.TextField(label='Название команды', hint_text='Введи название команды', on_change=validate_registrationfields)

    captain_name_field = ft.TextField(label='ФИО', hint_text='Иванов Иван Иванович', on_change=validate_registrationfields)
    captain_group_field = ft.TextField(label='Номер группы', hint_text='5130904/20002', on_change=validate_registrationfields)

    name_field = ft.TextField(label='ФИО', hint_text='Иванов Иван Иванович', on_change=validate_registrationfields)
    group_field = ft.TextField(label='Номер группы', hint_text='5130904/20002', on_change=validate_registrationfields)

    parts = ft.Column([
        ft.Divider(),
        name_field,
        group_field
    ])

    btn_add_part = ft.IconButton(ft.icons.ADD_ROUNDED, on_click=add_part, tooltip="Добавить участника")
    parts_count = ft.Text('1', size=16, weight=ft.FontWeight.W_400)
    btn_rem_part = ft.IconButton(ft.icons.REMOVE_ROUNDED, on_click=rem_part, tooltip="Удалить участника", disabled=True)
    btn_register = ft.ElevatedButton(text="Зарегистрироваться", width=300, height=50, disabled=True, on_click=register)

    reboot_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Перезагрузка", size=20, weight=ft.FontWeight.W_700),
        actions_alignment=ft.MainAxisAlignment.END,
        actions=[ft.ElevatedButton('Перезагрузить', icon=ft.icons.UPDATE_ROUNDED, on_click=reboot_service, data='controlpanel')],
        content=ft.Column(
            [
                ft.Text("Для того, чтобы изменение параметра вступило в силу, необходимо перезагрузить панель управления. Это также затронет страницу регистрации", size=18, text_align=ft.TextAlign.START)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            height=200,
            width=350
        )
    )

    confirmation_registration_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Регистрация", size=20, weight=ft.FontWeight.W_700),
        # actions_alignment=ft.MainAxisAlignment.END,
        # actions=[
        #     ft.ElevatedButton(
        #         "Вернуться",
        #         icon=ft.icons.TELEGRAM_ROUNDED,
        #         url="https://t.me/lrrrtm_testing_bot",
        #         on_click=confirmed
        #     ),
        # ],
        content=ft.Column(
            [
                ft.Text("Твоя команда успешно зарегистрирована, ты можешь возвращаться обратно к боту", size=18, text_align=ft.TextAlign.CENTER)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            height=200
        )
    )

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
                bgcolor=ft.colors.PRIMARY_CONTAINER,
                on_click=lambda _: copy_part()
            )
        ]
    )

    topic_description = ft.TextField(
        prefix_icon=ft.icons.TEXT_FIELDS_SHARP,
        label=labels['fields']['topic_description'],
        hint_text=labels['fields_hint']['topic_description'],
        on_change=lambda _: validate_description_field(),
    )

    confirm_field = ft.TextField(
        label=labels['fields']['confirm_code'],
        hint_text=labels['fields_hint']['confirm_code'],
        text_align=ft.TextAlign.CENTER,
        border_width=3,
        keyboard_type=ft.KeyboardType.NUMBER
    )

    confirmation_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Container(title_text(labels['titles']['confirm_action']), expand=True),
                ft.IconButton(ft.icons.CLOSE_ROUNDED, on_click=lambda _: close_dialog(confirmation_dialog))
            ]
        ),
        content=ft.Column(
            [
                ft.Text(labels['simple_text']['confirm_action'].format(str(datetime.datetime.now().date()).replace('-', '')), size=18),
                confirm_field
            ],
            width=350,
            height=150
        ),
        actions=[
            ft.ElevatedButton(
                text=labels['buttons']['accept'],
                icon=ft.icons.CHECK_ROUNDED,
                bgcolor=ft.colors.PRIMARY_CONTAINER,
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
            height=80
        ),
        actions=[
            ft.IconButton(
                # text=labels['buttons']['check'],
                icon=ft.icons.CHECK_ROUNDED,
                on_click=check_param,
                visible=False,
                disabled=True
            ),
            ft.ElevatedButton(
                text=labels['buttons']['save'],
                icon=ft.icons.SAVE_ROUNDED,
                on_click=update_param,
                bgcolor=ft.colors.PRIMARY_CONTAINER,
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

    password_field = ft.TextField(
        label=labels['fields']['password'], text_align=ft.TextAlign.LEFT,
        width=250, password=True, on_change=validate_login,
        can_reveal_password=True, height=70, on_submit=lambda _: login(),
    )
    button_login = ft.ElevatedButton(labels['buttons']['login'], width=250, on_click=lambda _: login(),
                                     disabled=True, height=50,
                                     icon=ft.icons.KEYBOARD_ARROW_RIGHT_ROUNDED,
                                     on_long_press=None)

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
            password_field,
            button_login
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    jury_name_field = ft.TextField(
        label=labels['fields']['jury'],
        hint_text=labels['fields_hint']['jury'],
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
                width=800,
                height=120
            ),
            padding=15
        ),
        elevation=10
    )

    app_info_elements = {
        'app_ver': statistic_tile(labels['titles']['app_ver'], app_ver),
        'db': app_info_title(labels['titles']['db_status'], db_status, 'db'),
        'flask': app_info_title(labels['titles']['flask_status'], flask_status, 'flask'),
        'bot': app_info_title(labels['titles']['bot_status'], bot_status, 'bot'),
        'yadisk': statistic_tile(labels['titles']['disk_status'], disk_status),
    }

    settings_col = ft.ListView(
        [
            ft.Card(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                ft.Row(
                                    [
                                        ft.Container(ft.Text(labels['titles']['statistics'], size=20, weight=ft.FontWeight.W_700), expand=True, margin=ft.margin.only(left=15)),
                                        ft.IconButton(ft.icons.RESTART_ALT_ROUNDED, on_click=lambda _: goto_stats(), tooltip="Обновить данные")
                                    ]
                                ),
                                margin=ft.margin.only(bottom=10)
                            ),
                            statistic_tile(labels['titles']['group_count'], group_count),
                            statistic_tile(labels['titles']['part_count'], part_count),
                            statistic_tile(labels['titles']['video_count'], videos_count),
                        ]
                    ),
                    padding=15
                ),
                elevation=10,
                width=450,
                col={"lg": 1}
            ),
            ft.Card(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(title_text(labels['titles']['removing_data']), margin=ft.margin.only(bottom=10, left=15)),
                            settings_tile(
                                title=labels['titles']['topics'],
                                descr=labels['simple_text']['rem_topics_descr'],
                                icon=ft.Icon(ft.icons.TOPIC_ROUNDED),
                                btn_text=labels['buttons']['delete'],
                                btn_data='delete_manytopic',
                                btn_action=confirm_delete
                            ),
                            settings_tile(
                                title=labels['titles']['groups'],
                                descr=labels['simple_text']['rem_groups_descr'],
                                icon=ft.Icon(ft.icons.GROUPS_ROUNDED, size=30),
                                btn_text=labels['buttons']['delete'],
                                btn_data='delete_manysgroups',
                                btn_action=confirm_delete
                            ),
                            settings_tile(
                                title=labels['titles']['jury'],
                                descr=labels['simple_text']['rem_jury_descr'],
                                icon=ft.Icon(ft.icons.EMOJI_PEOPLE_ROUNDED, size=30),
                                btn_text=labels['buttons']['delete'],
                                btn_data='delete_manyjury',
                                btn_action=confirm_delete
                            )
                        ]
                    ),
                    padding=15
                ),
                elevation=10,
                width=450,
                col={"lg": 1}
            ),

            ft.Card(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(title_text(labels['titles']['auth']), margin=ft.margin.only(bottom=20, left=15)),
                            settings_tile(
                                title=labels['statuses']['oauth_token'],
                                descr=labels['simple_text']['oauth_token_descr'],
                                icon=ft.Image(src='yadisk.png', fit=ft.ImageFit.FIT_HEIGHT, height=30),
                                btn_text=labels['buttons']['edit_token'],
                                btn_data='OAUTH_TOKEN',
                                btn_action=get_update_params
                            ),
                            settings_tile(
                                title=labels['statuses']['bot_token'],
                                descr=labels['simple_text']['bot_token_descr'],
                                icon=ft.Icon(ft.icons.TELEGRAM_ROUNDED, color='#2AABEE', size=30),
                                btn_text=labels['buttons']['edit_token'],
                                btn_data='BOT_TOKEN',
                                btn_action=get_update_params
                            ),
                            settings_tile(
                                title=labels['statuses']['password'],
                                descr=labels['simple_text']['password_descr'],
                                icon=ft.Icon(ft.icons.PASSWORD_ROUNDED, color='#2AABEE', size=30),
                                btn_text=labels['buttons']['edit_password'],
                                btn_data='PASSWORD',
                                btn_action=get_update_params
                            )
                        ]
                    ),
                    padding=15
                ),
                elevation=10,
                width=450,
                col={"lg": 1}
            ),
            ft.Card(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                ft.Row(
                                    [
                                        ft.Container(ft.Text(labels['titles']['info'], size=20, weight=ft.FontWeight.W_700), expand=True, margin=ft.margin.only(left=15)),
                                        ft.IconButton(ft.icons.RESTART_ALT_ROUNDED, on_click=lambda _: goto_info(), tooltip="Обновить данные")
                                    ]
                                ),
                                margin=ft.margin.only(bottom=20)
                            ),
                            app_info_elements['app_ver'],
                            app_info_elements['db'],
                            app_info_elements['flask'],
                            app_info_elements['bot'],
                            app_info_elements['yadisk'],
                        ]
                    ),
                    padding=15
                ),
                elevation=10,
                width=450,
                col={"lg": 1}
            )
        ],
        animate_opacity=300,
        width=800
    )

    btn_add_topic = ft.ElevatedButton(labels['buttons']['save'], icon=ft.icons.SAVE_ROUNDED, disabled=True, on_click=save_new_topic)
    new_topic_field = ft.TextField(label=labels['fields']['new_topic'], hint_text=labels['fields_hint']['new_topic'], on_change=validate_topic_name)
    btn_copy_code = ft.ElevatedButton(labels['buttons']['copy_code'], icon=ft.icons.COPY_ROUNDED, on_click=copy_accesscode)
    btn_open_form = ft.ElevatedButton(labels['buttons']['upload'], icon=ft.icons.FILE_UPLOAD_ROUNDED, url='https://forms.yandex.ru/u/661287c843f74fd25dec9fbc')

    import_topics_col = ft.Container(
        ft.Column(
            controls=[
                ft.Card(
                    ft.Container(
                        content=ft.Column(
                            [
                                title_text(labels['titles']['single_add']),
                                new_topic_field,
                                ft.Row([btn_add_topic], alignment=ft.MainAxisAlignment.END)
                            ],
                            # width=700
                        ),
                        padding=15
                    ),
                    elevation=10
                ),
                ft.Card(
                    ft.Container(
                        content=ft.Column(
                            [
                                title_text(labels['titles']['multi_add']),
                                ft.Text(labels['simple_text']['upload_topics'], size=18),
                                ft.Row([
                                    btn_copy_code
                                ],
                                    alignment=ft.MainAxisAlignment.END
                                ),
                                ft.Row([
                                    btn_open_form
                                ],
                                    alignment=ft.MainAxisAlignment.END
                                ),

                            ],
                            # width=700
                        ),
                        padding=15
                    ),
                    elevation=10
                )
            ],
            width=800,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    # vertext = ft.Text(
    #     value=None,
    #     text_align=ft.TextAlign.START,
    #     size=16
    # )

    # vertext.value = labels['elements']['app_version'].format(get_current_commit_hash())

    if platform.system() == "Windows":
        page.route = '/panel'
        # page.route = f'/registration/{random.randint(1000, 10000)}'

    if elements.global_vars.DB_FAIL:
        show_error('db', labels['errors']['db_connection'].format(elements.global_vars.ERROR_TEXT.split(":")[0]))
    else:
        routes = str(page.route).split("/")
        page_route = routes[1]
        if page_route == 'panel':
            page.scroll = None
            change_screen("login")

        elif page_route == 'registration' and len(routes) == 3:
            user_id = routes[2]
            page.scroll = ft.ScrollMode.ADAPTIVE
            sql_query = "SELECT * FROM participants WHERE telegram_id = %s"
            user = make_db_request(sql_query, (user_id,), get_many=True)
            if user is not None:
                if len(user) == 0:
                    page.controls = [
                        ft.Text(f'Telegram ID: {user_id}', size=16),
                        ft.Card(
                            ft.Container(
                                ft.Column(
                                    [
                                        ft.Container(title_text('Команда'), margin=ft.margin.only(bottom=10)),
                                        ft.Container(group_name_field)
                                    ],
                                    width=600,
                                ),
                                padding=15
                            ),
                            elevation=10
                        ),
                        ft.Card(
                            ft.Container(
                                ft.Column(
                                    [
                                        ft.Container(title_text('Капитан'), margin=ft.margin.only(bottom=10)),
                                        ft.Container(captain_name_field),
                                        ft.Container(captain_group_field)
                                    ],
                                    width=600
                                ),
                                padding=15
                            ),
                            elevation=10
                        ),
                        ft.Card(
                            ft.Container(
                                ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Container(ft.Text("Участники", size=20, weight=ft.FontWeight.W_700), expand=True),
                                                btn_rem_part,
                                                parts_count,
                                                btn_add_part

                                            ]
                                        ),
                                        parts
                                    ],
                                    width=600,
                                ),
                                padding=15
                            ),
                            elevation=10
                        ),
                        ft.Row([btn_register], alignment=ft.MainAxisAlignment.CENTER)
                    ]
                else:
                    show_error('already_registered', labels['errors']['already_registered'])

    page.update()


DEFAULT_FLET_PATH = ''
DEFAULT_FLET_PORT = 8502

if __name__ == "__main__":
    # connection, cur = create_db_connection()
    if platform.system() == 'Windows':
        ft.app(assets_dir='assets', target=main, use_color_emoji=True)
    else:
        flet_path = os.getenv("FLET_PATH", DEFAULT_FLET_PATH)
        flet_port = int(os.getenv("FLET_PORT", DEFAULT_FLET_PORT))
        ft.app(name=flet_path, target=main, view=None, port=flet_port, assets_dir='assets', use_color_emoji=True, upload_dir='assets/uploads')
