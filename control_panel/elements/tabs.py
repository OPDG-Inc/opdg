from flet import icons

tabs_config = {
    0: {
        "title": "Темы",
        "fab": True,
        "fab_text": "Импорт",
        "fab_icon": icons.UPLOAD_ROUNDED,
        "fab_target": "import_themes",
        "none_text": "Нет добавленных тем"
    },
    1: {
        "title": "Группы",
        "fab": None,
        "fab_text": "",
        "fab_icon": None,
        "fab_target": ""
    },
    2: {
        "title": "Жюри",
        "fab": True,
        "fab_text": "Добавить",
        "fab_icon": icons.GROUP_ADD_ROUNDED,
        "fab_target": "add_jury"
    },
    3: {
        "title": "Параметры",
        "fab": None,
        "fab_text": "",
        "fab_icon": None,
        "fab_target": ""
    }
}
