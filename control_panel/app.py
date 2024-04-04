import os
import platform
# import git

import flet as ft
from mysql.connector import connect, Error as sql_error

from control_panel.functions import load_config_file
from elements.screens import screens
from elements.tabs import tabs_config

import elements.global_vars

current_tab_index = -1
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)


def connect_to_db():
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
    page.theme = ft.Theme(font_family="Montserrat",
                          color_scheme=ft.ColorScheme(
                              primary=ft.colors.WHITE
                          )
                          )
    page.fonts = {
        "Montserrat": "fonts/Montserrat-SemiBold.ttf",
        # "Geologica-Black": "fonts/Geologica-black.ttf"
    }

    page.window_width = 720
    page.window_height = 1280

    def open_snackbar(text: str, bg_color=None, text_color=None):
        # Оповещение в нижней части экрана

        content = ft.Text(text, size=18)
        sb = ft.SnackBar(
            content=content
        )

        if bg_color is not None:
            sb.bgcolor = bg_color

        if text_color is not None:
            content.color = text_color

        page.snack_bar = sb
        sb.open = True
        page.update()

    def get_from_db(request_text: str):
        cur.execute(request_text)
        return cur.fetchall()

    def get_groups():
        rr = ft.ResponsiveRow(columns=3)
        groups_list = get_from_db("SELECT * FROM student_groups")
        if len(groups_list) > 0:
            for group in groups_list:
                captain_info = get_from_db(f"SELECT * FROM participants WHERE participant_id = {group['captain_id']}")[0]

                participants_info = get_from_db(f"SELECT * FROM participants WHERE group_id = {group['group_id']} and status != 'captain'")
                participants_col = ft.Column()
                for part in participants_info:
                    participants_col.controls.append(
                        ft.Text(f"{part['name']} ({part['study_group']})", size=18, text_align=ft.TextAlign.START)
                    )
                participants_panel = ft.ExpansionPanelList(
                    elevation=8,
                    controls=[
                        ft.ExpansionPanel(
                            # bgcolor=ft.colors.BLUE_400,
                            header=ft.ListTile(title=ft.Text(f"Список участников", size=18)),
                            content=participants_col,
                        )
                    ]
                )
                # for part in participants_info:
                #     participants_panel.controls.append(
                #         ft.ExpansionPanel(
                #             header=ft.ListTile(title=ft.Text(f"Panel AHAHA")),
                #         )
                #     )

                group_card = ft.Card(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(f"#{group['group_id']} | {group['name']}", size=20),
                                ft.Text(f"Капитан: {captain_info['name']} ({captain_info['study_group']})", size=18),
                                participants_panel
                            ]
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
                "title": "Свободна",
                "flag": True
            },
            "busy": {
                "title": "Занята",
                "flag": False
            },
        }

        rr = ft.ResponsiveRow(columns=3)

        topics_list = get_from_db(f"SELECT * from topics")
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
                                ft.Column(
                                    controls=[
                                        ft.Text(topic['description'], size=20, weight=ft.FontWeight.W_400),
                                        ft.Text(
                                            f"#{topic['topic_id']} | {statuses[topic['status']]['title']}",
                                            size=20, weight=ft.FontWeight.W_400),
                                    ],
                                    expand=True
                                ),
                                ft.Row(
                                    scroll=ft.ScrollMode.ADAPTIVE,
                                    controls=[
                                        ft.ElevatedButton(text="Изменить", icon=ft.icons.EDIT_ROUNDED,
                                                          visible=statuses[topic['status']]['flag']
                                                          ),
                                        ft.ElevatedButton(text="Удалить", icon=ft.icons.DELETE_ROUNDED,
                                                          visible=statuses[topic['status']]['flag']
                                                          ),
                                        ft.ElevatedButton(text="Перейти к группе", icon=ft.icons.FILE_OPEN_ROUNDED,
                                                          visible=not statuses[topic['status']]['flag']),
                                    ]
                                )
                            ]
                        ),
                        padding=15
                    ),
                    elevation=10,
                    height=200,
                    col={"lg": 1},
                )
                rr.controls.append(topic_card)
            page.add(rr)
            # page.appbar.actions = [
            #     ft.Container(ft.Text(f"Занято {busy_count}/{len(topics_list)}", size=18),
            #                  margin=ft.margin.only(right=20))]
        else:
            set_no_data()
        page.update()

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
                        title_text("Данные отсутствуют")
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                expand=True
            )
        )

    def change_navbar_tab(e):
        page.clean()
        page.appbar.actions.clear()

        global current_tab_index
        if type(e) == int:
            tab_index = e
        else:
            tab_index = e.control.selected_index

        tab = tabs_config[tab_index]
        appbar.title.value = tab['title']
        page.scroll = tab['scroll']
        page.floating_action_button = None

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
            page.appbar = None
            page.add(ft.Container(login_col, expand=True), footer)

        elif target == "main":
            page.appbar = appbar
            page.navigation_bar = navbar
            change_navbar_tab(0)

        elif target == "error":
            page.add(ft.Container(error_col, expand=True), footer)

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
        open_snackbar("Текст ошибки скопирован")

    def title_text(text: str):
        return ft.Text(text, size=30, font_family="Geologica", weight=ft.FontWeight.W_900,
                       text_align=ft.TextAlign.CENTER)

    def login():
        print(login_field.value.strip(), password_field.value.strip())
        auth_data = load_config_file("config.json")['auth']
        print(auth_data['login'], auth_data['password'])
        if login_field.value.strip() == auth_data['login'] and password_field.value.strip() == auth_data['password']:
            password_field.value = ""
            open_snackbar("С возвращением!", bg_color=ft.colors.GREEN, text_color=ft.colors.WHITE)
            change_screen("main")
        else:
            open_snackbar("Неверный логин или пароль", bg_color=ft.colors.RED, text_color=ft.colors.WHITE)

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
        label="Логин", text_align=ft.TextAlign.LEFT,
        width=250, on_change=validate_login,
        height=70
    )
    password_field = ft.TextField(
        label="Пароль", text_align=ft.TextAlign.LEFT,
        width=250, password=True, on_change=validate_login,
        can_reveal_password=True, height=70, on_submit=lambda _: login(),
    )
    button_login = ft.ElevatedButton("Войти", width=250, on_click=lambda _: login(),
                                     disabled=True, height=50,
                                     icon=ft.icons.KEYBOARD_ARROW_RIGHT_ROUNDED,
                                     on_long_press=None)

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
            ft.Text("login: admin | password: admin")
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
                            title_text("Ошибка БД"),
                            error_text,
                            ft.ElevatedButton(text="Скопировать текст ошибки", icon=ft.icons.COPY_ROUNDED,
                                              on_click=copy_error_text)
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
    vertext = ft.Text("", text_align=ft.TextAlign.START, size=16)
    footer = ft.Row(
        controls=[
            vertext
        ],
        alignment=ft.MainAxisAlignment.START
    )

    # repo = git.Repo(parent_directory)
    # vertext.value = f"сборка {repo.head.object.hexsha[:7]}"
    vertext.value = f"сборка developer"
    if elements.global_vars.DB_FAIL:
        error_text.value = f"При подключении к базе данных произошла ошибка. Обратитесь к администартору, сообщив текст ошибки: \n{elements.global_vars.ERROR_TEXT}"
        change_screen('error')
    else:
        change_screen("login")
    page.update()


DEFAULT_FLET_PATH = ''
DEFAULT_FLET_PORT = 8502

if __name__ == "__main__":
    connection, cur = connect_to_db()
    if platform.system() == 'Windows':
        ft.app(assets_dir='assets', target=main)
    else:
        flet_path = os.getenv("FLET_PATH", DEFAULT_FLET_PATH)
        flet_port = int(os.getenv("FLET_PORT", DEFAULT_FLET_PORT))
        ft.app(name=flet_path, target=main, view=None, port=flet_port, assets_dir='assets')
