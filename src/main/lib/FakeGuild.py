class FakeGuild:

    _instance = None

    def __init__(self):
        self.id = 0

    @staticmethod
    def instance():
        if not FakeGuild._instance:
            FakeGuild._instance = FakeGuild()
        return FakeGuild._instance
