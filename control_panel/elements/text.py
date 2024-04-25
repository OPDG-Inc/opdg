labels = {
    'errors': {
        'db_connection': "код ошибки: {0}",
        'db_request': "код ошибки: {0}",
        'empty_list': "На этой странице ещё не добавлена информация",
        'empty_jury': "Чтобы добавить члена жюри, нажмите на кнопку справа снизу",
        'empty_topics': "Чтобы начать добавлять темы, нажмите на кнопку справа снизу",
        'empty_groups': "Как только первая группа зарегистрируется, здесь появится карточка с информацией о ней",
        'already_registered': "Твоя команда уже зарегистрирована",
    },
    'elements': {
        'bot_link': "https://t.me/vshpm_event_bot?start=jury_{0}",
        'loading': "Загружаем",
        'no_marks_subtitle': "не выставлены",
        'is_active': "🟢 работает",
        'is_disabled': "🔴 недоступно",
        'is_not_working': "🟡 не работает (код {0})",
        'status_loading': "загрузка..."
    },
    'titles': {
        'edit_params': "Изменение параметра",
        'marks_title': "Общая оценка",
        'part_list': "Обзор группы",
        'edit_topic': "Редактирование темы",
        'participants_panel': "Список группы",
        'control_panel': 'Панель',
        'removing_data': "Удаление данных",
        'auth': "Авторизация",
        'rebooting': "Перезагрузка",
        'single_add': "Одиночное добавление",
        'multi_add': "Массовое добавление",
        'confirm_action': "Подтверждение действия",
        'topics': "Темы",
        'groups': "Группы",
        'jury': "Жюри",
        'statistics': "Статистика",
        'group_count': "Количество групп",
        'part_count': "Количество участников",
        'video_count': "Загружено видео",
        'info': "Состояние системы",
        'app_ver': "Версия",
        'db_status': "База данных",
        'flask_status': "Flask-сервер",
        'bot_status': "Telegram-бот",
        'disk_status': "Яндекс.Диск",
        'registration': "Регистрация",
        'registration_group': "Команда",
        'registration_captain': "Капитан",
        'registration_participants': "Участники",
        'group_info': "Обзор группы"
    },
    'buttons': {
        # actions
        'delete': "Удалить",
        'save': "Сохранить",
        'edit': "Изменить",
        'add': "Добавить",
        'check': "Проверить",
        'register_group': "Зарегистрироваться",
        'reboot': "Перезагрузить",
        'accept': "Подтвердить",
        'login': "Войти",
        'update_project': "Обновить проект",
        'copy_code': "Копировать код",
        'upload': "Открыть форму",
        'edit_token': "Изменить токен",
        'edit_password': "Изменить пароль",
        'link': "Ссылка",
        'copy_participants_list': "Копировать",
        # statuses
        'adding': "Добавляем",
        'checking': "Проверяем",

        # other
        'group_part': "Участники",
    },
    'fields': {
        'login': "Логин",
        'password': "Пароль",
        'topic_description': "Название",
        'confirmation_code': "Код подтверждения",
        'initials': "ФИО",
        'new_topic': "Тема",
        'group': "Номер группы",
        'new_group_name': "Название команды",
        'tid': "Telegram ID",
        'group_search': "Поиск команды"

    },
    'fields_hint': {
        'param': 'Введите значение параметра',
        'topic_description': "Введите название темы",
        'confirmation_code': "Введите код",
        'initials': "Иванов Иван Иванович",
        'new_topic': "Введите описание темы",
        'group': "5130904/20002",
        'new_group_name': "Введи название команды",
        'tid': "4090180157",
        'group_search': "Введите название команды"
    },
    'snack_bars': {
        'welcome': "С возвращением!",
        'wrong_login': "Неверный пароль",
        'link_copied': "Пригласительная ссылка скопирована",
        'error_text_copied': "Текст ошибки скопирован",
        'action_unavaliable': "Действие недоступно",
        'group_list_copied': "Состав группы скопирован",
        'element_deleted': "Элемент удалён",
        'table_deleted': "Таблица удалена",
        'data_edited': "Данные изменены",
        'data_updated': "Данные обновлены",
        'loading': "Загружаем",
        'accesscode_copied': "Код подключения скопирован",
        'topic_added': "Тема добавлена",
        'rebooting': "Перезагружаем",
        'jury_already_exists': "Жюри с такими данными уже существует",
        'group_name_already_exists': "Название команды уже занято"
    },
    'statuses': {
        'topic_free': "Свободна",
        'topic_busy': "Занята",
        'jury_waiting': "Ожидание",
        'jury_registered': "Зарегистрирован",
        'video_waiting': "Ожидаем видео",
        'video_uploaded': "Видео",
        'oauth_token': "OAuth-токен",
        'bot_token': "Bot-токен",
        'password': "Пароль"
    },
    'simple_text': {
        'upload_topics': "Скопируйте код подключения, после чего откройте форму и вставьте список тем, не забудьте вставить скопированный код подключения",
        'confirm_action': "Чтобы подтвердить своё действие, введите в окно {0}",
        'bot_token_descr': "Токен для связи с Telegram API",
        'oauth_token_descr': "Токен для связи бота с Яндекс.Диском",
        'password_descr': "Пароль для входа в панель управления и подтверждения действий",
        'rem_topics_descr': "Удаляются все темы, которые находятся в базе данных",
        'rem_groups_descr': "Удаляются все участники, загруженные видео, очищается список групп, в том числе рейтинг",
        'rem_jury_descr': "Удаляется всё жюри с потерей доступа к оцениваю работ",
        'rebooting_info': "Для того, чтобы изменение параметра вступило в силу, необходимо перезагрузить панель управления. Это также затронет страницу регистрации",
        'registration_end': "Твоя команда успешно зарегистрирована, ты можешь возвращаться обратно к боту"
    },
    'bot_text': {
        'registration_end': "*{0}*, регистрация команды *«{1}»* успешно завершена! 🎉" \
                            "\n\n{2}\n📨 Тема ролика вашей команды: *«{3}»*" \
                            "\n\n📍Когда ролик будет готов к загрузке, введи команду /sendvideo или просто нажми на неё" \
                            "\n\n📍*Загрузить ролик можно будет только 1 раз*"
    },
    'error_titles': {
        'empty_list': "Ничего не осталось",
        'no_jury': "Никого не видим",
        'no_topics': "Не нашли ни одной темы",
        'no_groups': "Ждём первую группу",
        'db_connect': "Ошибка базы данных",
        'db_request': "Ошибка базы данных",
        'already_registered': "А всё уже",
    },
    'tooltips': {
        'add_participant': "Добавить участника",
        'remove_participant': "Удалить участника",
        'update_data': "Обновить данные",
        'rebooting': "Перезагрузка сервиса",
    },
    'page_titles': {
        'registration': "Регистрация команды",
        'panel': "Панель управления"
    }
}
