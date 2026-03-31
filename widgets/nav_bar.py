import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image


class NavBarWidget(ctk.CTkFrame):
    def __init__(self, master, title="TG270-sQC", **kwargs):
        super().__init__(master, **kwargs)

        self._title = title
        self._assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
        )

        self.configure(
            fg_color=("#1A1A1A", "#1A1A1A"),
            corner_radius=0,
            height=80,
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_left()
        self._build_center()
        self._build_right()

    def _load_image(self, relative_path: str, size):
        path = os.path.join(self._assets_dir, relative_path)
        try:
            image = Image.open(path)
            return ctk.CTkImage(light_image=image, dark_image=image, size=size)
        except Exception:
            return None

    def _build_left(self):
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="w", padx=(18, 12), pady=10)

        uni_logo = self._load_image(os.path.join("logo", "NULOGO.png"), (54, 54))
        uni_logo_label = ctk.CTkLabel(left_frame, text="", image=uni_logo)
        uni_logo_label.image = uni_logo
        uni_logo_label.pack(side="left", padx=(0, 10))

        text_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        text_frame.pack(side="left")

        ctk.CTkLabel(
            text_frame,
            text="มหาวิทยาลัยนเรศวร",
            font=("TH Sarabun New", 20, "bold"),
            text_color="#FFFFFF",
        ).pack(anchor="w")

        ctk.CTkFrame(
            text_frame,
            fg_color="#C06B5A",
            width=132,
            height=1,
            corner_radius=0,
        ).pack(anchor="w", pady=(0, 2))

        ctk.CTkLabel(
            text_frame,
            text="Naresuan University",
            font=("TH Sarabun New", 18),
            text_color="#F1F1F1",
        ).pack(anchor="w")

    def _build_center(self):
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=1, pady=6)

        ctk.CTkLabel(
            center_frame,
            text=self._title,
            font=("TH Sarabun New", 30, "bold"),
            text_color="#FFFFFF",
        ).pack()

        ctk.CTkLabel(
            center_frame,
            text="โปรแกรมตรวจสอบมาตรฐานคุณภาพจอภาพทางการแพทย์",
            font=("TH Sarabun New", 20),
            text_color="#F3F3F3",
        ).pack()

    def _build_right(self):
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="e", padx=(12, 18))

        account_icon = self._load_image(os.path.join("icons", "account_d.png"), (38, 38))
        self.profile_btn = ctk.CTkButton(
            right_frame,
            text="",
            image=account_icon,
            width=48,
            height=48,
            corner_radius=24,
            fg_color="transparent",
            hover_color="#676767",
            border_width=0,
            command=self._show_dropdown,
        )
        self.profile_btn.image = account_icon
        self.profile_btn.pack()

    def _show_dropdown(self):
        from services.session import get_session, is_evaluator_logged_in

        menu = tk.Menu(
            self,
            tearoff=0,
            bg="#2B2B2B",
            fg="white",
            activebackground="#1D5BBF",
            activeforeground="white",
            font=("TH Sarabun New", 18),
        )

        is_logged_in = is_evaluator_logged_in()
        if is_logged_in:
            user = get_session()
            name = f"{user.get('name', 'User')} {user.get('lastname', '')}".strip()
            menu.add_command(label=f"👤 {name}", state="disabled")
            menu.add_separator()
        else:
            menu.add_command(label="🔓 Sign in", command=self._on_sign_in)

        theme_menu = tk.Menu(
            menu,
            tearoff=0,
            bg="#2B2B2B",
            fg="white",
            activebackground="#1D5BBF",
            activeforeground="white",
            font=("TH Sarabun New", 16),
        )
        theme_menu.add_command(label="☀️ Light Mode", command=lambda: self.theme_mode_switch("Light"))
        theme_menu.add_command(label="🌙 Dark Mode", command=lambda: self.theme_mode_switch("Dark"))
        theme_menu.add_command(label="💻 System Default", command=lambda: self.theme_mode_switch("System"))
        menu.add_cascade(label="🎨 Theme", menu=theme_menu)

        if is_logged_in:
            menu.add_separator()
            menu.add_command(label="🚪 Sign out", command=self.on_logout_click)

        x = self.profile_btn.winfo_rootx()
        y = self.profile_btn.winfo_rooty() + self.profile_btn.winfo_height()
        menu.post(x, y)

    def _on_sign_in(self):
        toplevel = self.winfo_toplevel()
        if hasattr(toplevel, "show_screen"):
            toplevel.show_screen("evaluator_login")

    def theme_mode_switch(self, mode: str):
        ctk.set_appearance_mode(mode)

    def on_logout_click(self):
        import tkinter.messagebox
        from services.session import clear_session

        ans = tkinter.messagebox.askyesno("ออกจากระบบ", "แน่ใจหรือไม่ว่าจะออกจากระบบที่รันอยู่?")
        if ans:
            clear_session()
            toplevel = self.winfo_toplevel()
            if hasattr(toplevel, "show_screen"):
                toplevel.show_screen("evaluator_login")
