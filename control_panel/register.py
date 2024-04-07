import datetime
import hashlib
import os
import platform
import random
import subprocess
import time
import uuid

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
        "Geologica": "fonts/Geologica.ttf",
    }
    page.scroll = ft.ScrollMode.ADAPTIVE

    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    # page.horizontal_alignment = ft.MainAxisAlignment.CENTER

    def confirmed(e):
        page.clean()

    confirmation_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Регистрация", size=20, weight=ft.FontWeight.W_700),
        actions_alignment=ft.MainAxisAlignment.END,
        actions=[
            ft.ElevatedButton(
                "Открыть бот",
                icon=ft.icons.TELEGRAM_ROUNDED,
                url="https://t.me/lrrrtm",
                on_click=confirmed
            ),
        ],
        content=ft.Column(
            [
                ft.Text("Твоя команда успешно зарегистрирована, ты можешь возвращаться к боту", size=18)
            ],
            width=350,
            height=200
        )
    )

    def title_text(text: str):
        return ft.Text(text, size=20, font_family="Geologica", weight=ft.FontWeight.W_700,
                       text_align=ft.TextAlign.CENTER)

    def register(e):
        sql_query = "INSERT INTO sgroups (name) VALUES (%s)"
        cur.execute(sql_query, (group_name_field.value,))

        sql_query = "INSERT INTO participants (telegram_id, name, study_group, status) VALUES (%s, %s, %s, %s)"
        cur.execute(sql_query, (user_id, captain_name_field.value, captain_group_field.value, 'captain'))

        cur.execute(f"SELECT group_id FROM sgroups WHERE name = '{group_name_field.value}'")
        group_id = cur.fetchone()['group_id']

        cur.execute(f"UPDATE participants SET group_id = {group_id} WHERE telegram_id = {user_id}")

        cur.execute(f"SELECT participant_id FROM participants WHERE group_id = {group_id} and status = 'captain'")
        captain_id = cur.fetchone()['participant_id']

        cur.execute(f"UPDATE sgroups SET captain_id = {captain_id} WHERE group_id = {group_id}")

        sql_query = "INSERT INTO participants (group_id, telegram_id, name, study_group, status) VALUES (%s, %s, %s, %s, %s)"

        participants = [el for el in parts.controls if type(el) == flet_core.textfield.TextField]
        for i in range(0, len(participants), 2):
            part = {}
            part['name'] = participants[i].value
            part['group'] = participants[i + 1].value
            cur.execute(sql_query, (group_id, 0, part['name'], part['group'], 'part',))

        cur.execute(f"DELETE FROM registration WHERE user_id = '{user_id}'")
        open_dialog(confirmation_dialog)

    def validate_fields(e):
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
        parts.controls.append(ft.Divider())
        parts.controls.append(
            ft.TextField(label='ФИО', hint_text='Иванов Иван Иванович', on_change=validate_fields)
        )
        parts.controls.append(
            ft.TextField(label='Номер группы', hint_text='5130904/20002', on_change=validate_fields)
        )
        btn_rem_part.disabled = False
        btn_register.disabled = True
        if len(parts.controls) == 15:
            btn_add_part.disabled = True
        page.update()

    def rem_part(e: ft.ControlEvent):
        for _ in range(3):
            parts.controls.pop()
        btn_add_part.disabled = False
        if len(parts.controls) == 0:
            btn_rem_part.disabled = True
        validate_fields('1')
        page.update()

    def open_dialog(dialog: ft.AlertDialog):
        page.dialog = dialog
        dialog.open = True
        page.update()

    def close_dialog(dialog: ft.AlertDialog):
        dialog.open = False
        page.update()


    group_name_field = ft.TextField(label='Название команды', hint_text='Введи название команды', on_change=validate_fields)

    captain_name_field = ft.TextField(label='ФИО', hint_text='Иванов Иван Иванович', on_change=validate_fields)
    captain_group_field = ft.TextField(label='Номер группы', hint_text='5130904/20002', on_change=validate_fields)

    name_field = ft.TextField(label='ФИО', hint_text='Иванов Иван Иванович', on_change=validate_fields)
    group_field = ft.TextField(label='Номер группы', hint_text='5130904/20002', on_change=validate_fields)

    parts = ft.Column([
        ft.Divider(),
        name_field,
        group_field
    ])

    btn_add_part = ft.IconButton(ft.icons.ADD_ROUNDED, on_click=add_part, tooltip="Добавить участника")
    btn_rem_part = ft.IconButton(ft.icons.REMOVE_ROUNDED, on_click=rem_part, tooltip="Удалить участника", disabled=True)
    btn_register = ft.ElevatedButton("Зарегистрироваться", icon=ft.icons.APP_REGISTRATION_ROUNDED, expand=False, width=400, disabled=True, on_click=register)

    reg_data = str(page.route).split("/")[-1].split("_")
    if len(reg_data) == 2:
        user_id = reg_data[0]
        hash = reg_data[1]

        cur.execute(f"SELECT * FROM registration WHERE user_id = '{user_id}' AND hash = '{hash}'")
        is_real_user = cur.fetchall()
        if len(is_real_user) == 1:
            page.controls = [
                ft.Card(
                    ft.Container(
                        ft.Column(
                            [
                                ft.Container(title_text('Команда'), margin=ft.margin.only(bottom=20)),
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
                                ft.Container(title_text('Капитан'), margin=ft.margin.only(bottom=20)),
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
                                        btn_add_part,
                                        btn_rem_part
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
    page.update()


DEFAULT_FLET_PATH = ''
DEFAULT_FLET_PORT = 8503

if __name__ == "__main__":
    connection, cur = create_db_connection()
    if platform.system() == 'Windows':
        ft.app(assets_dir='assets', target=main, use_color_emoji=True, upload_dir='assets/uploads', view=ft.AppView.WEB_BROWSER)
    else:
        flet_path = os.getenv("FLET_PATH", DEFAULT_FLET_PATH)
        flet_port = int(os.getenv("FLET_PORT", DEFAULT_FLET_PORT))
        ft.app(name=flet_path, target=main, view=None, port=flet_port, assets_dir='assets', use_color_emoji=True, upload_dir='assets/uploads')
