import os
import platform
# import git

import flet as ft
from mysql.connector import connect, Error as sql_error
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
    page.theme_mode = ft.ThemeMode.SYSTEM
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

        rr = ft.ResponsiveRow(
            columns=3
        )

        topics_list = get_from_db(f"SELECT * from topics")
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
                                            f"ID: {topic['topic_id']} | Статус: {statuses[topic['status']]['title']}",
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
                    col={"lg": 1},
                    height=180
                )
                rr.controls.append(topic_card)
            page.add(rr)
            page.appbar.actions = [
                ft.Container(ft.Text(f"Занято {busy_count}/{len(topics_list)}", size=18),
                             margin=ft.margin.only(right=20))]
        else:
            page.scroll = None
            page.add(
                ft.Container(
                    ft.Column(
                        [
                            ft.Container(ft.Image(src="assets/images/no_data.png",
                                                  fit=ft.ImageFit.CONTAIN,
                                                  height=200,
                                                  error_content=ft.ProgressRing()
                                                  ),
                                         ),
                            # margin=ft.margin.only(bottom=20)),
                            title_text("Данные отсутствуют")
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    expand=True
                )
            )

        page.update()

    # def get_cards(target: str):
    #     # Генерация карточек
    #
    #     data = get_from_db()
    #     if data:
    #         # print(data)
    #         for el in data:
    #             print(el)
    #             cur_card = copy(card[target])
    #             cur_card.content.content.controls = [
    #                 ,
    #                 ft.ElevatedButton("Test"),
    #                 ft.Divider(thickness=5)
    #             ]
    #             page.add(cur_card)
    #             # pass
    #         print(len(page.controls))
    #     else:
    #         # если данных по данному таргету нет
    #         page.add(
    #             ft.Container(
    #                 ft.Column(
    #                     [
    #                         ft.Container(ft.Image(src="assets/images/no_data.png",
    #                                               fit=ft.ImageFit.CONTAIN,
    #                                               height=200,
    #                                               error_content=ft.ProgressRing()
    #                                               ),
    #                                      ),
    #                         # margin=ft.margin.only(bottom=20)),
    #                         ft.Text("Данные отсутствуют", size=30, font_family="Geologica-Black",
    #                                 text_align=ft.TextAlign.CENTER)
    #                     ],
    #                     alignment=ft.MainAxisAlignment.CENTER,
    #                     horizontal_alignment=ft.CrossAxisAlignment.CENTER
    #                 ),
    #                 expand=True
    #             )
    #         )
    #     page.update()

    def change_navbar_tab(e):
        global current_tab_index
        if type(e) == int:
            tab_index = e
        else:
            tab_index = e.control.selected_index

        # if tab_index == current_tab_index:
        #     return
        # else:
        #     current_tab_index = tab_index

        page.clean()
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
        # if tab_index in [0, 1, 2]:
        #     get_cards(tabs_config[tab_index]['index'])

        page.update()

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
        can_reveal_password=True, height=70, on_submit=lambda _: change_screen("main"),
    )
    button_login = ft.ElevatedButton("Войти", width=250, on_click=lambda _: change_screen("main"),
                                     disabled=True, height=50,
                                     icon=ft.icons.KEYBOARD_ARROW_RIGHT_ROUNDED,
                                     on_long_press=None)

    login_col = ft.Column(
        controls=[
            ft.Icon(ft.icons.ADMIN_PANEL_SETTINGS_OUTLINED, size=150),
            login_field,
            password_field,
            button_login
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
    # vertext.value = f"Панель управления ботом (сборка {repo.head.object.hexsha[:7]})"
    vertext.value = f"Панель управления ботом (сборка developer)"
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
