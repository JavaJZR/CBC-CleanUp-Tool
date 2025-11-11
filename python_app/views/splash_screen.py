"""
Splash Screen View
Displays a short splash image before the main application loads.
"""

import tkinter as tk
from tkinter import ttk


class SplashScreen:
    """Simple splash screen with logo and brand colors."""

    WIDTH = 560
    HEIGHT = 340
    BG_COLOR = "#9B1313"
    ACCENT_COLOR = "#CD1C18"
    LIGHT_COLOR = "#FCE6E2"

    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.configure(bg=self.BG_COLOR)

        # Position the window at the center of the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coord = int((screen_width / 2) - (self.WIDTH / 2))
        y_coord = int((screen_height / 2) - (self.HEIGHT / 2))
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x_coord}+{y_coord}")

        container = tk.Frame(self.root, bg=self.BG_COLOR, padx=24, pady=24)
        container.pack(fill="both", expand=True)

        self.progress_bar = None

        self._create_logo(container)
        self._create_text(container)
        self._create_progress(container)

    def _create_logo(self, parent: tk.Frame):
        canvas = tk.Canvas(
            parent,
            width=120,
            height=120,
            highlightthickness=0,
            bg=self.BG_COLOR,
        )
        canvas.pack(pady=(0, 12))

        # Outer circle
        canvas.create_oval(5, 5, 115, 115, fill=self.ACCENT_COLOR, outline="")
        # Inner subtle ring
        canvas.create_oval(20, 20, 100, 100, fill=self.BG_COLOR, outline=self.LIGHT_COLOR, width=3)
        # Bank initials
        canvas.create_text(
            60,
            60,
            text="CBC",
            fill=self.LIGHT_COLOR,
            font=("Segoe UI", 26, "bold"),
        )

    def _create_text(self, parent: tk.Frame):
        title = tk.Label(
            parent,
            text="Employee Data Clean-Up Tool",
            font=("Segoe UI", 18, "bold"),
            bg=self.BG_COLOR,
            fg=self.LIGHT_COLOR,
        )
        title.pack()

        subtitle = tk.Label(
            parent,
            text=f"China Banking Corporation",
            font=("Segoe UI", 11),
            bg=self.BG_COLOR,
            fg="#FFE5E0",
        )
        subtitle.pack(pady=(4, 12))

    def _create_progress(self, parent: tk.Frame):
        progress_frame = tk.Frame(parent, bg=self.BG_COLOR)
        progress_frame.pack(fill="x", pady=(10, 0))

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Splash.Horizontal.TProgressbar",
            troughcolor=self.BG_COLOR,
            background=self.LIGHT_COLOR,
            bordercolor=self.BG_COLOR,
            lightcolor=self.LIGHT_COLOR,
            darkcolor=self.LIGHT_COLOR,
            thickness=6,
        )

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="indeterminate",
            length=320,
            style="Splash.Horizontal.TProgressbar",
        )
        self.progress_bar.pack()
        self.progress_bar.start(18)

        loading_label = tk.Label(
            parent,
            text="Preparing your workspace…",
            font=("Segoe UI", 10, "bold"),
            bg=self.BG_COLOR,
            fg="#FFE5E0",
        )
        loading_label.pack(pady=(8, 0))

    def show(self):
        """Display the splash screen until closed manually."""
        self.root.update_idletasks()
        self.root.deiconify()
        self.root.update()
    
    def close(self, new_default_root=None):
        """Destroy the splash window and update default root if provided."""
        if self.root:
            try:
                if self.progress_bar:
                    self.progress_bar.stop()
                self.root.destroy()
                if new_default_root is not None:
                    tk._default_root = new_default_root
                else:
                    tk._default_root = None
            except tk.TclError:
                pass

