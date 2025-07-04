# engine/game_state.py
import pickle


class GameState:
    def __init__(self):
        self.name = "Player"
        self.energy = 3
        self.reputation = 0
        self.inventory = []

    def apply_effects(self, effects):
        self.energy += effects.get("energy", 0)
        self.reputation += effects.get("reputation", 0)
        self.inventory += effects.get("inventory", [])


def save_game(state, node, path='save.dat'):
    with open(path, 'wb') as f:
        pickle.dump((state, node), f)


def load_game(path='save.dat'):
    with open(path, 'rb') as f:
        return pickle.load(f)
