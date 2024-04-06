from control_panel.elements.text import labels

targets = {
    'empty_list': {
        'image': "empty_folder.png",
        'title': labels['error_titles']['no_data']
    },
    'db': {
        'image': "db_error.png",
        'title': labels['error_titles']['db_connect']
    },
    'db_request': {
        'image': "db_request.png",
        'title': labels['error_titles']['db_request']
    }
}
