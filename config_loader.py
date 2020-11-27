import json


class ConfigLoader:

    def __init__(self):
        with open("config.json", "w") as file:
            self.data = json.load(file)
