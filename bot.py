import tkinter as tk
from PIL import Image, ImageTk, ImageGrab

class ScreenSelector:
    def __init__(self, prompt):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.config(cursor="cross")
        
        # Take a background screenshot to "freeze" the screen for selection
        self.bg_img = ImageGrab.grab()
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

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline="red", width=2)

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        self.ok_btn.config(state="normal")

    def confirm(self):
        # Get final coordinates
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.coords = {
            "top": int(min(y1, y2)),
            "left": int(min(x1, x2)),
            "width": int(abs(x2 - x1)),
            "height": int(abs(y2 - y1))
        }
        self.root.destroy()

# Run for Window then Character
game_region = ScreenSelector("Select the Entire Game Window").coords
char_region = ScreenSelector("Select the Character").coords

print(f"Game: {game_region}\nCharacter: {char_region}")
