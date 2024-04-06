from elements.text import labels

targets = {
    'empty_list': {
        'image': "hole.png",
        'title': labels['error_titles']['empty_list']
    },
    'empty_jury': {
        'image': "no_jury.png",
        'title': labels['error_titles']['no_jury']
    },
    'empty_topics': {
        'image': "no_topics.png",
        'title': labels['error_titles']['no_topics']
    },
    'empty_groups': {
        'image': "no_groups.png",
        'title': labels['error_titles']['no_groups']
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
