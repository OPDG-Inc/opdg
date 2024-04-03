import flet as ft

from elements.cards import card
from elements.screens import screens
from elements.tabs import tabs_config

current_tab_index = -1


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.START,
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(font_family="Montserrat")
    page.fonts = {
        "Montserrat": "fonts/Montserrat-SemiBold.ttf",
        "Geologica-Black": "fonts/Geologica-black.ttf"
    }

    def open_snackbar(text: str, bg_color=None, text_color=None):
        # Оповещение в нижней части экрана

        content = ft.Text(text)
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
        return []

    def get_cards(target: str):
        # Генерация карточек

        data = get_from_db('000')
        if data:
            main_card = card[target]
            for el in data:
                # наполнение карточки
                pass
        else:
            # если данных по данному таргету нет
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
                            ft.Text("Данные отсутствуют", size=30, font_family="Geologica-Black",
                                    text_align=ft.TextAlign.CENTER)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    expand=True
                )
            )
        page.update()

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

        page.floating_action_button = None
        if tab['fab'] is not None:
            page.floating_action_button = ft.FloatingActionButton(
                text=tab['fab_text'],
                icon=tab['fab_icon'],
                on_click=lambda _: change_screen(tab['fab_target'])
            )
        if tab_index in [0, 1, 2]:
            get_cards('0000')

        page.update()

    def change_screen(target: str):
        page.navigation_bar = None
        page.floating_action_button = None
        page.clean()

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
    footer = ft.Row(
        controls=[
            ft.Text("Панель управления ботом (сборка abc123)", text_align=ft.TextAlign.START)
        ],
        alignment=ft.MainAxisAlignment.START
    )

    change_screen("main")
    page.update()


if __name__ == "__main__":
    ft.app(
        target=main,
        assets_dir="assets"
    )
