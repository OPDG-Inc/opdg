class Topic:
    def __init__(self, topic_id=None, description=None, status=None):
        self.topic_id = topic_id
        self.description = description
        self.status = status


class StudentGroup:
    def __int__(self, group_id=None, name=None, topic_id=None, captain_id=None, video_status=None):
        self.group_id = group_id
        self.name = name
        self.topic_id = topic_id
        self.captain_id = captain_id
        self.video_status = video_status


class Participant:
    def __init__(self, participant_id=None, group_id=None, name=None, study_group=None, status=None):
        self.participant_id = participant_id
        self.group_id = group_id
        self.name = name
        self.study_group = study_group
        self.status = status


class Jury:
    def __init__(self, jury_id=None, telegram_id=None, name=None, pass_phrase=None):
        self.jury_id = jury_id
        self.telegram_id = telegram_id
        self.name = name
        self.pass_phrase = pass_phrase
