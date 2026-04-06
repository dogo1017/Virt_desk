import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import mss
import subprocess
import os
import sys

class ScreenSelector:
    def __init__(self, prompt):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.config(cursor="cross")
        
        # --- TRIPLE FAIL-SAFE CAPTURE ---
        self.bg_img = self.capture_screen_logic()
        
        self.tk_bg = ImageTk.PhotoImage(self.bg_img)
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.tk_bg, anchor="nw")
        
        # Selection state
        self.rect = None
        self.start_x = self.start_y = 0
        self.coords = None

        # UI Label and OK Button
        self.label = tk.Label(self.root, text=prompt, bg="yellow", fg="black", font=("Arial", 14))
        self.label.place(x=10, y=10)
        
        self.ok_btn = tk.Button(self.root, text="OK", command=self.confirm, state="disabled", width=10, height=2)
        self.ok_btn.place(relx=0.5, rely=0.9, anchor="center")

        # Mouse Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        
        self.root.mainloop()

    def capture_screen_logic(self):
        """Attempts the fastest capture methods first, then falls back to system tools."""
        
        # 1. Attempt MSS (Fastest, usually fails on 16-bit)
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[0]
                sct_img = sct.grab(monitor)
                print("Capture: MSS Success (Fastest)")
                return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        except Exception:
            print("Capture: MSS Failed. Trying Pillow...")

        # 2. Attempt Pillow ImageGrab (Standard)
        try:
            img = ImageGrab.grab()
            print("Capture: Pillow Success")
            return img
        except Exception:
            print("Capture: Pillow Failed. Trying Scrot (System Fallback)...")

        # 3. Attempt Scrot (Slowest, but works on almost all Linux environments)
        temp_file = "fallback_shot.png"
        try:
            # -z is silent, -o is overwrite
            subprocess.run(["scrot", "-z", "-o", temp_file], check=True)
            img = Image.open(temp_file).convert("RGB")
            img.load() # Load into memory
            os.remove(temp_file) # Clean up
            print("Capture: Scrot Success (System Tool)")
            return img
        except Exception as e:
            print(f"CRITICAL ERROR: All capture methods failed. {e}")
            sys.exit(1)

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        self.ok_btn.config(state="normal")

    def confirm(self):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.coords = {
            "top": int(min(y1, y2)),
            "left": int(min(x1, x2)),
            "width": int(abs(x2 - x1)),
            "height": int(abs(y2 - y1))
        }
        self.root.destroy()

# Execution Flow
print("Starting Selection Process...")
game_region = ScreenSelector("Select the Entire Game Window").coords
char_region = ScreenSelector("Select the Character").coords

print("\n--- SELECTION COMPLETE ---")
print(f"Game Region: {game_region}")
print(f"Char Region: {char_region}")
