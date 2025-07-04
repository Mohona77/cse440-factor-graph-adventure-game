import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageEnhance
import json
import os
import random
import pickle
import pygame
import tkinter.font as font

from engine.factor_graph_ai import AIDecisionEngine
from engine.game_state import GameState, save_game, load_game
from engine.story_manager import StoryManager

pygame.mixer.init()


def play_music(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play(-1)


def play_click_sound():
    click_path = os.path.join("assets", "sounds", "click.wav")
    if os.path.exists(click_path):
        click_sound = pygame.mixer.Sound(click_path)
        click_sound.play()


class AdventureGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Adventure Quest: AI Chronicles")
        self.master.geometry("800x700")
        self.master.configure(bg='black')

        self.story = StoryManager().story
        self.ai = AIDecisionEngine()
        self.state = GameState()
        self.current_node = "start"
        self.story_log = []

        self.custom_font = font.Font(family="Georgia", size=14, weight="bold")

        self.create_widgets()
        self.show_intro()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.master, width=800,
                                height=400, highlightthickness=0)
        self.canvas.pack()

        # Semi-transparent rectangle behind text
        self.text_bg = self.canvas.create_rectangle(
            20, 300, 780, 390, fill='#000000', stipple='gray25', outline='')

        self.story_text = tk.Label(self.master, text="", font=self.custom_font,
                                   fg='white', bg='#000000', wraplength=760, justify='left')
        self.story_text.pack(pady=(5, 0))

        # Scrollable Story Log
        self.log_frame = tk.Frame(self.master)
        self.log_frame.pack(pady=5, fill='x')
        self.log_scrollbar = tk.Scrollbar(self.log_frame)
        self.log_scrollbar.pack(side='right', fill='y')
        self.log_text = tk.Text(self.log_frame, height=6, state='disabled',
                                bg='black', fg='lightgray', font=('Courier', 10))
        self.log_text.pack(side='left', fill='x', expand=True)
        self.log_text.config(yscrollcommand=self.log_scrollbar.set)
        self.log_scrollbar.config(command=self.log_text.yview)

        self.choice_frame = tk.Frame(self.master, bg='black')
        self.choice_frame.pack(pady=10)

        self.ai_label = tk.Label(self.master, text="",
                                 fg="cyan", font=("Arial", 12), bg='black')
        self.ai_label.pack()

        self.stats = tk.Label(self.master, font=(
            "Arial", 12), fg="lightgreen", bg='black')
        self.stats.pack(pady=10)

        self.ctrl_frame = tk.Frame(self.master, bg='black')
        self.ctrl_frame.pack()
        ttk.Style().configure('TButton', font=('Georgia', 12))
        ttk.Button(self.ctrl_frame, text="💾 Save",
                   command=self.save_state).pack(side="left", padx=10)
        ttk.Button(self.ctrl_frame, text="📂 Load",
                   command=self.load_state).pack(side="left", padx=10)
        ttk.Button(self.ctrl_frame, text="🧠 Show AI Graph",
                   command=self.ai.show_graph).pack(side="left", padx=10)

    def show_intro(self):
        self.canvas.delete("all")
        self.story_text.config(
            text="Welcome to Adventure Quest!\nEnter your name to begin:")
        self.name_entry = tk.Entry(self.master, font=('Georgia', 14))
        self.name_entry.pack()
        self.start_btn = tk.Button(self.master, text="Start Game", font=(
            'Georgia', 14), command=self.start_game, bg='darkgreen', fg='white')
        self.start_btn.pack(pady=10)

    def start_game(self):
        play_click_sound()
        self.state.name = self.name_entry.get() or "Player"
        self.name_entry.destroy()
        self.start_btn.destroy()
        self.display_node()

    def display_node(self):
        node = self.story[self.current_node]

        # Play background music
        music_path = os.path.join(
            "assets", "sounds", f"{self.current_node}.mp3")
        if os.path.exists(music_path):
            play_music(music_path)

        # Background image with fade effect
        img_path = os.path.join("assets", node.get("image", "default.png"))
        if os.path.exists(img_path):
            self.fade_in_background(img_path)
        else:
            self.canvas.delete("all")
            self.canvas.create_rectangle(0, 0, 800, 400, fill='black')

        self.story_text.config(text=node["text"])
        self.append_to_log(node["text"])

        for widget in self.choice_frame.winfo_children():
            widget.destroy()

        choices = node.get("choices", {})
        if not choices:
            messagebox.showinfo("Game Over", "Thanks for playing!")
            self.master.quit()
            return

        ai_choice = self.ai.suggest(
            self.state.energy, self.state.reputation, choices)
        self.ai_label.config(text=f"🤖 AI Suggests: {ai_choice}")

        for choice_text, choice_data in choices.items():
            btn = tk.Button(self.choice_frame, text=choice_text, font=('Georgia', 12),
                            bg='gray15', fg='white', activebackground='darkgreen', activeforeground='white',
                            command=lambda c=choice_text: self.make_choice(c))
            btn.pack(side="left", padx=10, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='darkgreen'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg='gray15'))

        self.update_stats()

    def fade_in_background(self, img_path):
        self.canvas.delete("all")
        # FIX: convert image mode to RGBA before brightness enhancement
        self.bg_img_pil = Image.open(img_path).convert(
            "RGBA").resize((800, 400))
        self.alpha = 0
        self.bg_img_tk = None
        self._fade_step()

    def _fade_step(self):
        if self.alpha < 1.0:
            enhancer = ImageEnhance.Brightness(self.bg_img_pil)
            img = enhancer.enhance(self.alpha)
            self.bg_img_tk = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor='nw', image=self.bg_img_tk)
            self.alpha += 0.05
            self.master.after(50, self._fade_step)
        else:
            self.bg_img_tk = ImageTk.PhotoImage(self.bg_img_pil)
            self.canvas.create_image(0, 0, anchor='nw', image=self.bg_img_tk)

    def append_to_log(self, text):
        self.story_log.append(text)
        self.log_text.config(state='normal')
        self.log_text.insert('end', text + "\n\n")
        self.log_text.config(state='disabled')
        self.log_text.see('end')

    def make_choice(self, choice):
        play_click_sound()
        node = self.story[self.current_node]
        choice_data = node["choices"][choice]

        effects = choice_data.get("effects", {})
        self.state.apply_effects(effects)

        self.current_node = choice_data["next"]
        self.display_node()

    def update_stats(self):
        inv = ', '.join(
            self.state.inventory) if self.state.inventory else 'Empty'
        self.stats.config(
            text=f"🧍 {self.state.name} | ❤️ {self.state.energy} | ⭐ {self.state.reputation} | 🎒 {inv}")

    def save_state(self):
        save_game(self.state, self.current_node)
        messagebox.showinfo("Saved", "Game saved successfully!")

    def load_state(self):
        try:
            self.state, self.current_node = load_game()
            self.display_node()
        except:
            messagebox.showerror("Error", "No saved file found.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdventureGUI(root)
    root.mainloop()
