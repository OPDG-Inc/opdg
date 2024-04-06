from flet import icons, ScrollMode

tabs_config = {
    0: {
        "index": "topics",
        "title": "Темы",
        "fab": True,
        "fab_text": "Импорт",
        "fab_icon": icons.UPLOAD_ROUNDED,
        "fab_target": "import_themes",
        "none_text": "Нет добавленных тем",
        "scroll": ScrollMode.ADAPTIVE,
    },
    1: {
        "index": "groups",
        "title": "Группы",
        "fab": None,
        "fab_text": "",
        "fab_icon": None,
        "fab_target": "",
        "scroll": ScrollMode.ADAPTIVE,
    },
    2: {
        "index": "jury",
        "title": "Жюри",
        "fab": True,
        "fab_text": "Добавить",
        "fab_icon": icons.GROUP_ADD_ROUNDED,
        "fab_target": "add_jury",
        "scroll": ScrollMode.ADAPTIVE,
    },
    3: {
        "index": "settings",
        "title": "Параметры",
        "fab": None,
        "fab_text": "",
        "fab_icon": None,
        "fab_target": "",
        "scroll": ScrollMode.ADAPTIVE,
    }
}
