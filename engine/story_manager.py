# engine/story_manager.py
import json


class StoryManager:
    def __init__(self, path="data/story.json"):
        with open(path) as f:
            self.story = json.load(f)
