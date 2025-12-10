from ...utils.api.models import ZZZAvatarInfo


class Character:
    def __init__(self, char_dict: ZZZAvatarInfo):
        self.id: int = char_dict["id"]
