# duck_game.py (Tkinter GUI part)
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import time
import random
import pygame
import os

pygame.mixer.init()
pygame.mixer.music.load("quack_1.mp3")

class DuckApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(1)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "white")
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.root.config(bg="white")

        self.size = 100
        self.max_size = int(self.screen_width * 0.35)
        self.current_frame = 0
        self.duck_frames = self.load_duck_frames()
        self.duck_label = tk.Label(root, image=self.duck_frames[0], bg="white")
        self.duck_label.place(x=150, y=150)

        self.health_canvas = tk.Canvas(root, width=100, height=10, bg="white", highlightthickness=0)
        self.health_bar = self.health_canvas.create_rectangle(0, 0, 100, 10, fill="green")
        self.health_canvas.place(x=150, y=150 + self.size + 5)

        self.feed_button = tk.Button(root, text="FEED ME", font=("Arial", 18), command=self.feed_duck)
        self.feed_button_visible = False
        self.toggle_button_color()

        self.last_fed = time.time()
        self.eggs = []
        self.prompt_shown = False
        self.hungry_mode = False
        self.chaos_mode_active = False
        self.egg_drop_rate = 1000
        self.egg_loop_running = False

        self.egg_image = ImageTk.PhotoImage(Image.open("egg2.png").resize((32, 32)))

        self.animate_duck()
        self.monitor_hunger()
        self.quack_loop()
        self.update_health_bar()
        self.update_streamlit_status()

    def load_duck_frames(self):
        duck_img = Image.open("duck.gif")
        return [ImageTk.PhotoImage(img.copy().resize((self.size, self.size))) 
                for img in ImageSequence.Iterator(duck_img)]

    def animate_duck(self):
        self.current_frame = (self.current_frame + 1) % len(self.duck_frames)
        self.duck_label.configure(image=self.duck_frames[self.current_frame])
        self.root.after(100, self.animate_duck)

    def feed_duck(self):
        self.last_fed = time.time()
        self.size = 100
        self.duck_frames = self.load_duck_frames()
        self.duck_label.config(image=self.duck_frames[self.current_frame])
        self.duck_label.place(x=150, y=150)
        self.update_health_bar_position()
        for egg in self.eggs:
            egg.destroy()
        self.eggs.clear()

        self.prompt_shown = False
        self.hungry_mode = False
        self.chaos_mode_active = False
        self.egg_drop_rate = 1000
        self.egg_loop_running = False

        self.feed_button.place_forget()

    def monitor_hunger(self):
        elapsed = time.time() - self.last_fed
        if elapsed > 5:
            self.hungry_mode = True
            if not self.feed_button.winfo_ismapped():
                self.feed_button.place(x=self.screen_width//2 - 100, y=self.screen_height//2 - 25, width=200, height=50)
            self.go_rogue()
        self.root.after(300, self.monitor_hunger)

    def update_health_bar(self):
        elapsed = time.time() - self.last_fed
        if elapsed >= 10:
            self.health_canvas.place_forget()
        else:
            remaining = max(0, 10 - elapsed)
            width = int((remaining / 10) * 100)
            color = "green" if remaining > 6 else "orange" if remaining > 3 else "red"
            self.health_canvas.coords(self.health_bar, 0, 0, width, 10)
            self.health_canvas.itemconfig(self.health_bar, fill=color)
            self.update_health_bar_position()
        self.root.after(100, self.update_health_bar)

    def update_health_bar_position(self):
        duck_x = self.duck_label.winfo_x()
        duck_y = self.duck_label.winfo_y()
        self.health_canvas.place(x=duck_x, y=duck_y + self.size + 5)

    def quack_loop(self):
        if self.hungry_mode and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        self.root.after(800, self.quack_loop)

    def go_rogue(self):
        if self.size < self.max_size:
            self.grow_duck()
            self.move_duck()
            self.lay_egg()
        else:
            if not self.chaos_mode_active:
                self.chaos_mode_active = True
                self.start_chaos_mode()

    def grow_duck(self):
        growth_step = max(20, (self.max_size - self.size) // 4)
        self.size += growth_step
        if self.size > self.max_size:
            self.size = self.max_size
        self.duck_frames = self.load_duck_frames()
        self.duck_label.configure(image=self.duck_frames[self.current_frame])

    def move_duck(self):
        x = random.randint(0, max(0, self.screen_width - self.size))
        y = random.randint(0, max(0, self.screen_height - self.size))
        self.duck_label.place(x=x, y=y)
        self.update_health_bar_position()

    def lay_egg(self):
        egg = tk.Label(self.root, image=self.egg_image, bg="white", bd=0)
        egg.place(x=random.randint(0, self.screen_width - 32), y=random.randint(0, self.screen_height - 32))
        self.eggs.append(egg)

    def start_chaos_mode(self):
        self.chaotic_movement()
        if not self.egg_loop_running:
            self.egg_loop_running = True
            self.exponential_egg_drop()

    def chaotic_movement(self):
        self.move_duck()
        if not self.prompt_shown and self.size >= self.max_size:
            self.prompt_exit()
            self.prompt_shown = True
        self.root.after(150, self.chaotic_movement)

    def exponential_egg_drop(self):
        self.lay_egg()
        self.egg_drop_rate = max(50, int(self.egg_drop_rate * 0.6))
        self.root.after(self.egg_drop_rate, self.exponential_egg_drop)

    def toggle_button_color(self):
        if self.feed_button.winfo_ismapped():
            current = self.feed_button.cget("bg")
            new_color = "red" if current == "white" else "yellow"
            fg_color = "white" if new_color == "red" else "black"
            self.feed_button.config(bg=new_color, fg=fg_color, activebackground=new_color, activeforeground=fg_color)
        self.root.after(400, self.toggle_button_color)

    def prompt_exit(self):
        prompt = tk.Toplevel(self.root)
        prompt.overrideredirect(True)
        prompt.geometry("400x150+500+300")
        prompt.attributes("-topmost", True)

        tk.Label(prompt, text="So you won't feed me?").pack(pady=(10, 2))
        entry = tk.Entry(prompt, font=("Arial", 12), width=40)
        entry.pack(pady=2)
        output_label = tk.Label(prompt, text="", fg="blue", font=("Arial", 10))
        output_label.pack(pady=5)

        responses = {
            "please": "Fine, I’ll leave... but next time, don’t make me ask!",
            "pls": "Spell it out next time, maybe? I’ll let this slide.",
            "poda tharave": "Aa tone nalla irunnu... valare cute!",
        }

        def check_input():
            user_input = entry.get().lower()
            for keyword, reply in responses.items():
                if keyword in user_input:
                    if keyword in ("please", "pls"):
                        output_label.config(text=reply)
                        self.root.after(2000, self.root.destroy)
                        return
                    else:
                        output_label.config(text=reply)
                        return
            output_label.config(text="Try being nice, maybe?")

        tk.Button(prompt, text="Submit", command=check_input).pack(pady=(2, 5))

    def update_streamlit_status(self):
        elapsed = int(time.time() - self.last_fed)
        with open("duck_status.txt", "w") as f:
            f.write(f"last_fed={elapsed}\n")
            f.write(f"eggs={len(self.eggs)}\n")
            f.write(f"chaos={self.chaos_mode_active}\n")
        self.root.after(1000, self.update_streamlit_status)


root = tk.Tk()
app = DuckApp(root)
root.mainloop()