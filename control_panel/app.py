import os
import platform
import subprocess
import time

import flet as ft
from mysql.connector import connect, Error as sql_error

from functions import load_config_file
from elements.screens import screens
from elements.tabs import tabs_config

import elements.global_vars
from elements.text import labels

current_tab_index = -1
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)


def create_db_connection():
    try:
        connection = connect(
            host=os.getenv('db_host'),
            user="developer",
            password="kLRWua&sAHT4sXB",
            database="opd"
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
        # font_family="Geologica",
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

    def open_snackbar(text: str, bg_color=None, text_color=None):
        # Оповещение в нижней части экрана

        content = ft.Text(text, size=18)
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
        cur.execute(request_text)
        if many:
            return cur.fetchall()
        else:
            return cur.fetchone()

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
        groups_list = get_from_db("SELECT * FROM student_groups", many=True)
        if len(groups_list) > 0:
            for group in groups_list:

                topic_info = get_from_db(f"SELECT * FROM topics WHERE topic_id = {group['topic_id']}")

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
                                    title=ft.Text(f"{group['name']}", size=20, font_family="Geologica", weight=ft.FontWeight.W_900),
                                    subtitle=ft.Text(f"#{topic_info['topic_id']} {topic_info['description']}", size=18),
                                ),
                                ft.Container(
                                    ft.ListTile(
                                        title=ft.Text("Оценки", size=20, font_family="Geologica", weight=ft.FontWeight.W_900),
                                        subtitle=ft.Text(f"не выставлены", size=18),
                                    ),
                                    margin=ft.margin.only(top=-20),
                                    visible=not statuses[group['video_status']]['flag']
                                ),
                                ft.ResponsiveRow(
                                    [
                                        ft.ElevatedButton(
                                            text="Участники",
                                            icon=ft.icons.GROUPS_ROUNDED,
                                            bgcolor=ft.colors.PRIMARY_CONTAINER,
                                            col={"lg": 1}
                                        ),
                                        ft.ElevatedButton(
                                            text=statuses[group['video_status']]['title'],
                                            icon=ft.icons.ONDEMAND_VIDEO_ROUNDED,
                                            disabled=statuses[group['video_status']]['flag'],
                                            bgcolor=ft.colors.PRIMARY_CONTAINER,
                                            col={"lg": 1}
                                        ),

                                    ],
                                    columns=2,
                                    alignment=ft.MainAxisAlignment.END,
                                    # scroll=ft.ScrollMode.HIDDEN,
                                ),
                            ],
                            # horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        padding=15
                    ),
                    col={"lg": 1},
                    elevation=10
                )
                rr.controls.append(group_card)
            page.add(rr)
        else:
            set_no_data()
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

        topics_list = get_from_db(f"SELECT * from topics", many=True)
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
                                    title=ft.Text(f"#{topic['topic_id']} {topic['description']}", size=20, font_family="Geologica", weight=ft.FontWeight.W_900),
                                    subtitle=ft.Row(
                                            [
                                                statuses[topic['status']]['icon'],
                                                ft.Text(statuses[topic['status']]['title'], size=20)
                                            ]
                                        ),
                                    expand=True
                                ),
                                # ft.Column(
                                #     controls=[
                                #         ft.Text(f"#{topic['topic_id']} {topic['description']}", size=20, weight=ft.FontWeight.W_400),
                                #         ft.Row(
                                #             [
                                #                 statuses[topic['status']]['icon'],
                                #                 ft.Text(statuses[topic['status']]['title'], size=20)
                                #             ]
                                #         ),
                                #     ],
                                # ),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            text=labels['buttons']['edit'], icon=ft.icons.EDIT_ROUNDED,
                                            visible=statuses[topic['status']]['flag'],
                                            bgcolor=ft.colors.PRIMARY_CONTAINER
                                        ),
                                        ft.ElevatedButton(
                                            text=labels['buttons']['delete'], icon=ft.icons.DELETE_ROUNDED,
                                            visible=statuses[topic['status']]['flag'],
                                            bgcolor=ft.colors.RED
                                        ),
                                        ft.ElevatedButton(
                                            text=labels['buttons']['group_info'], icon=ft.icons.FILE_OPEN_ROUNDED,
                                            visible=not statuses[topic['status']]['flag'],
                                            bgcolor=ft.colors.PRIMARY_CONTAINER
                                        ),
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
                )
                rr.controls.append(topic_card)
            page.add(rr)
        else:
            set_no_data()
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
                                    title=ft.Text(f"{jury['name']}", size=20, font_family="Geologica", weight=ft.FontWeight.W_900),
                                    subtitle=ft.Row([
                                            statuses[jury['status']]['icon'],
                                            ft.Text(f"{statuses[jury['status']]['title']}", size=18, weight=ft.FontWeight.W_400)
                                        ])
                                ),
                                ft.Row(
                                    # scroll=ft.ScrollMode.ADAPTIVE,
                                    controls=[
                                        ft.ElevatedButton(
                                            text=labels['buttons']['delete'],
                                            icon=ft.icons.DELETE_ROUNDED,
                                            bgcolor=ft.colors.RED,
                                            on_click=None
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
                    col={"lg": 1}
                )
                rr.controls.append(jury_card)
            page.add(rr)
        else:
            set_no_data()

    def set_no_data():
        page.scroll = None
        page.add(
            ft.Container(
                ft.Column(
                    [
                        ft.Container(ft.Image(src="no_data.png",
                                              fit=ft.ImageFit.CONTAIN,
                                              height=200,
                                              error_content=ft.ProgressRing()
                                              ),
                                     ),
                        title_text(labels['elements']['no_data'])
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                expand=True
            )
        )

    def get_jury_link(e: ft.ControlEvent):
        page.set_clipboard(labels['elements']['bot_link'].format(e.control.data))
        open_snackbar(labels['snack_bars']['link_copied'])

    def change_navbar_tab(e):
        global current_tab_index
        if type(e) == int:
            tab_index = e
        else:
            tab_index = e.control.selected_index

        page.clean()
        page.appbar.actions.clear()

        tab = tabs_config[tab_index]
        appbar.title.value = tab['title']
        page.scroll = tab['scroll']
        page.floating_action_button = None

        if tab_index in [0, 1, 2]:
            open_dialog(loading_dialog)
            time.sleep(1)
            pass

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

        close_dialog(loading_dialog)

        page.update()

    def change_screen(target: str):
        # page.appbar.actions.clear()
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
            page.add(ft.Container(login_col, expand=True), )#footer)

        elif target == "main":
            page.appbar = appbar
            page.navigation_bar = navbar
            change_navbar_tab(0)

        elif target == "error":
            page.add(ft.Container(error_col, expand=True), )#footer)

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

    def copy_error_text(e: ft.ControlEvent):
        page.set_clipboard(elements.global_vars.ERROR_TEXT)
        open_snackbar(labels['snack_bars']['error_text_copied'])

    def title_text(text: str):
        return ft.Text(text, size=30, font_family="Geologica", weight=ft.FontWeight.W_900,
                       text_align=ft.TextAlign.CENTER)

    def update():
        if platform.system() == 'Windows':
            open_snackbar(labels['snack_bars']['action_unavaliable'])
        else:
            open_dialog(loading_dialog)
            os.system("/root/controlupdate.sh")

    def login():
        print(login_field.value.strip(), password_field.value.strip())
        auth_data = load_config_file("config.json")['auth']
        print(auth_data['login'], auth_data['password'])
        if login_field.value.strip() == auth_data['login'] and password_field.value.strip() == auth_data['password']:
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

    loading_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(),
        content=ft.Column(
            width=100,
            height=100,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.ProgressRing(scale=1.5),
                ft.Container(ft.Text(labels['elements']['loading'], size=20), margin=ft.margin.only(top=20))
            ]
        )
    )

    navbar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.FORMAT_LIST_BULLETED_ROUNDED, label=tabs_config[0]['title']),
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
            ft.Container(ft.Image(src="logo.png",
                                  fit=ft.ImageFit.CONTAIN,
                                  height=200,
                                  error_content=ft.ProgressRing()
                                  ),
                         ),
            login_field,
            password_field,
            button_login,
            button_update,
            # ft.Text("login: admin | password: admin")
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    error_text = ft.Text("", size=18, text_align=ft.TextAlign.START)

    error_col = ft.Column(
        controls=[
            ft.Card(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            title_text(labels['elements']['db_error_title']),
                            error_text,
                            ft.ElevatedButton(
                                text=labels['buttons']['copy_error_text'],
                                icon=ft.icons.COPY_ROUNDED,
                                on_click=copy_error_text
                            )
                        ]
                    ),
                    padding=15
                ),
                elevation=15
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
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
        error_text.value = labels['errors']['db_connection'].format(elements.global_vars.ERROR_TEXT)
        change_screen('error')
    else:
        change_screen("login")
    page.update()


DEFAULT_FLET_PATH = ''
DEFAULT_FLET_PORT = 8502

if __name__ == "__main__":
    connection, cur = create_db_connection()
    if platform.system() == 'Windows':
        ft.app(assets_dir='assets', target=main, use_color_emoji=True, name='', port=8502)
    else:
        flet_path = os.getenv("FLET_PATH", DEFAULT_FLET_PATH)
        flet_port = int(os.getenv("FLET_PORT", DEFAULT_FLET_PORT))
        ft.app(name=flet_path, target=main, view=None, port=flet_port, assets_dir='assets', use_color_emoji=True)
