try:
    import customtkinter as CTk
    import tkinter as tk
    from PIL import Image, ImageTk
except ImportError:
    import os
    os.system("pip install customtkinter tkinter pillow")
    del os
    import customtkinter as CTk
    import tkinter as tk
    from PIL import Image, ImageTk

class CanvasHandler:
    def __init__(self, log_handler, root_window = None, canvas_color: str = "#ffffff", arrow_color: str = "#000000"):
        self.root_window = root_window
        self.log_handler = log_handler

        self.canvas: tk.Canvas = tk.Canvas(self.root_window, bg=canvas_color)
        self.arrow_color: str = arrow_color

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_left_button_press)
        self.canvas.bind("<ButtonPress-3>", self.on_right_button_press)

        self.canvas.bind("<B1-Motion>", self.on_left_mouse_drag)
        self.canvas.bind("<B3-Motion>", self.on_right_mouse_drag)

        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        # Initialize variables
        self.scale: float = 1.0
        self.images: list[Image.Image] = [[ ], [ ], [ ]] # full size, small size, cropped size

    def add_image_to_list(self, image_path):
        """
        Adds a Pillow Image object to the list of images to be displayed on the canvas.

        params: image_path: str - The path to the image file.
        return: None	
        """
        if "cards" in image_path: self.images[0].append(Image.open(image_path))
        elif "cards_small" in image_path: self.images[1].append(Image.open(image_path))
        elif "cards_cropped" in image_path: self.images[2].append(Image.open(image_path))

    def set_root_window(self, root_window):
        """
        Sets the root window of the canvas.
        Should be called before once before calling the show method.
        Necessary because trying to set the root window in the constructor of app.py causes the program to crash (recursion limit).

        params: root_window: tk.Tk - The root window of the canvas.
        return: None
        """
        self.root_window = root_window

    def set_canvas_color(self, color: str):
        """
        Sets the color of the canvas.

        params: color: str - The color of the canvas.
        return: None
        """
        self.canvas.configure(bg=color)

    def set_arrow_color(self, color: str):
        """
        Sets the color of the arrows.

        params: color: str - The color of the arrows.
        return: None
        """
        self.arrow_color = color

    def on_left_button_press(self, event):
        """
        Marks the position of the canvas when the left mouse button is pressed.
        """

        self.canvas.scan_mark(event.x, event.y)

    def on_left_mouse_drag(self, event):
        """
        Drags the canvas when the left mouse button is pressed.
        """

        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_mouse_wheel(self, event):
        """
        Zooms in or out of the canvas when the mouse wheel is scrolled.
        """

        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.scale *= scale_factor
        self.canvas.scale("all", event.x, event.y, scale_factor, scale_factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_right_button_press(self, event):
        """
        Marks the position of the canvas when the right mouse button is pressed.
        """

        self.canvas.scan_mark(event.x, event.y)

    def on_right_mouse_drag(self, event):
        """
        Drags the canvas when the right mouse button is pressed.
        """

        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def add_image(self, image_path, x, y):
        """
        Adds an image to the canvas.

        params:
            image_path: str - The path to the image file.
            x: int - The x-coordinate of the image.
            y: int - The y-coordinate of the image.

        return: None

        raises: None
        """
        image = Image.open(image_path)
        image = ImageTk.PhotoImage(image)
        self.images.append(image)  # Keep a reference to avoid garbage collection
        self.canvas.create_image(x, y, image=image, anchor=tk.CENTER)

    def show(self):
        """
        Shows the canvas.
        """
        self.canvas.pack(fill=tk.BOTH, expand=True)