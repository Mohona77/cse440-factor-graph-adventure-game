import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import random

# ------------------------
# Factor Graph Framework
# ------------------------


class Variable:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        self.factors = []

    def connect(self, factor):
        self.factors.append(factor)


class Factor:
    def __init__(self, name, func, variables):
        self.name = name
        self.func = func
        self.variables = variables
        for v in variables:
            v.connect(self)

    def update(self, action=None):
        self.func(self.variables, action)


# ------------------------
# Utility
# ------------------------
def load_image(name, size=(1000, 700)):
    img_path = os.path.join("assets", name + ".png")
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.BICUBIC
    if os.path.exists(img_path):
        img = Image.open(img_path).resize(size, resample)
    else:
        img = Image.new("RGB", size, color="gray")
    return img


# ------------------------
# Adventure Game (GUI + Factor Graph)
# ------------------------
class AdventureGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Adventure Quest (Factor Graph)")
        self.geometry("1000x700")
        self.resizable(False, False)

        # Game variables as factor graph nodes
        self.PlayerHP = Variable("PlayerHP", 100)
        self.EnemyHP = Variable("EnemyHP", 0)
        self.PlayerLocation = Variable("Location", "forest")
        self.Inventory = Variable("Inventory", [])

        # Factors
        self.factors = []
        self.factors.append(
            Factor("Movement", self.movement_factor, [self.PlayerLocation]))
        self.factors.append(Factor("Combat", self.combat_factor, [
                            self.PlayerHP, self.EnemyHP]))
        self.factors.append(Factor("Treasure", self.treasure_factor, [
                            self.PlayerLocation, self.Inventory]))

        # Images
        self.locations = ["forest", "cave",
                          "river", "treasure", "safe", "lost"]
        self.images = {name: ImageTk.PhotoImage(
            load_image(name)) for name in self.locations}

        # Background
        self.bg_label = tk.Label(self)
        self.bg_label.pack(fill="both", expand=True)

        # Story text
        self.story_text = tk.Label(self, text="", wraplength=900, justify="center",
                                   font=("Arial", 14), bg="white", fg="black")
        self.story_text.place(relx=0.5, rely=0.05, anchor="n")

        # Buttons
        self.button_frame = tk.Frame(self, bg="gray")
        self.button_frame.place(relx=0.5, rely=0.75, anchor="center")

        # Health bars
        self.player_bar = ttk.Progressbar(self, length=200, maximum=100)
        self.enemy_bar = ttk.Progressbar(self, length=200, maximum=100)
        tk.Label(self, text="Player HP").place(x=50, y=650)
        tk.Label(self, text="Enemy HP").place(x=750, y=650)
        self.player_bar.place(x=120, y=650)
        self.enemy_bar.place(x=820, y=650)

        # Log
        self.log_box = tk.Text(self, height=6, width=110, state="disabled",
                               bg="black", fg="lime", font=("Courier", 10))
        self.log_box.place(x=50, y=550)

        self.update_scene("forest", "You awaken in a mysterious forest. Paths lead to a cave and a river.",
                          [("Go to Cave", lambda: self.take_action("GoCave")),
                           ("Go to River", lambda: self.take_action("GoRiver"))])

    # ------------------------
    # Factor Functions
    # ------------------------
    def movement_factor(self, vars, action):
        loc = vars[0]
        if action == "GoCave":
            loc.value = "cave"
        elif action == "GoRiver":
            loc.value = "river"
        elif action == "GoTreasure":
            loc.value = "treasure"
        elif action == "ReturnForest":
            loc.value = "forest"

    def combat_factor(self, vars, action):
        player, enemy = vars
        if action == "Fight":
            enemy.value = 50
            self.log("⚔️ A wild enemy appears!")
        elif action == "Attack" and enemy.value > 0:
            dmg = random.randint(10, 25)
            enemy.value = max(0, enemy.value - dmg)
            self.log(f"You strike for {dmg}! Enemy HP = {enemy.value}")
        elif action == "Defend" and enemy.value > 0:
            dmg = max(0, random.randint(5, 15) - random.randint(0, 5))
            player.value = max(0, player.value - dmg)
            self.log(
                f"You defend! Enemy deals {dmg}. Player HP = {player.value}")

    def treasure_factor(self, vars, action):
        loc, inv = vars
        if loc.value == "treasure":
            inv.value = ["💰 Gold", "💎 Diamonds", "👑 Crown", "🗿 Ancient Relic"]
            self.log("🎉 You found the treasure!")

    # ------------------------
    # Game Flow
    # ------------------------
    def take_action(self, action):
        for f in self.factors:
            f.update(action)
        self.refresh_gui(action)

    def refresh_gui(self, action):
        loc = self.PlayerLocation.value
        hp, ehp = self.PlayerHP.value, self.EnemyHP.value

        # Update HP bars
        self.player_bar["value"] = max(0, hp)
        self.enemy_bar["value"] = max(0, ehp)

        # Scene logic based on location
        if loc == "forest":
            self.update_scene("forest", "You are in the forest.",
                              [("Go to Cave", lambda: self.take_action("GoCave")),
                               ("Go to River", lambda: self.take_action("GoRiver"))])
        elif loc == "cave":
            if ehp > 0:
                self.update_scene("cave", "An enemy blocks your path!",
                                  [("Attack", lambda: self.take_action("Attack")),
                                   ("Defend", lambda: self.take_action("Defend"))])
            else:
                self.update_scene("cave", "You step into the cave. Something stirs...",
                                  [("Fight Enemy", lambda: self.take_action("Fight")),
                                   ("Return to Forest", lambda: self.take_action("ReturnForest"))])
        elif loc == "river":
            self.update_scene("river", "The river flows swiftly. Something shines across.",
                              [("Cross River", lambda: self.take_action("GoTreasure")),
                               ("Return to Forest", lambda: self.take_action("ReturnForest"))])
        elif loc == "treasure":
            self.update_scene("treasure", "You found the hidden treasure!",
                              [("Play Again", lambda: self.take_action("ReturnForest")),
                               ("View Inventory", self.show_inventory)])

        # Defeat condition
        if hp <= 0:
            self.Inventory.value = [
                "⚔️ Broken Sword", "🪨 Rocks", "🛡️ Torn Shield"]
            self.update_scene("lost", "You were defeated...",
                              [("Retry", lambda: self.take_action("GoCave")),
                               ("View Inventory", self.show_inventory)])
        # Victory condition
        if ehp == 0 and action == "Attack" and loc == "cave":
            self.update_scene("safe", "Enemy defeated!",
                              [("Continue", lambda: self.take_action("GoTreasure"))])

    def update_scene(self, bg_name, text, options):
        self.bg_label.configure(image=self.images[bg_name])
        self.story_text.config(text=text)
        for w in self.button_frame.winfo_children():
            w.destroy()
        for label, action in options:
            tk.Button(self.button_frame, text=label, command=action,
                      font=("Arial", 12), width=18, height=2,
                      bg="navy", fg="white").pack(side="left", padx=10)

    def log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def show_inventory(self):
        win = tk.Toplevel(self)
        win.title("Inventory")
        win.geometry("300x250")
        tk.Label(win, text="Your Items:", font=(
            "Arial", 12, "bold")).pack(pady=5)
        items = self.Inventory.value
        if not items:
            tk.Label(win, text="(Empty)", font=("Arial", 10, "italic")).pack()
        else:
            for item in items:
                tk.Label(win, text="• " + item, font=("Arial", 11)
                         ).pack(anchor="w", padx=20)


if __name__ == "__main__":
    AdventureGame().mainloop()
