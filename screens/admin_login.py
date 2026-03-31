import os
import customtkinter as ctk
from PIL import Image

from widgets.nav_bar import NavBarWidget
from widgets.side_bar import SideBarWidget


class AdminLoginScreen(ctk.CTkFrame):
    def __init__(self, master, login_command=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self.login_command = login_command
        self._assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
        )

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.navbar = NavBarWidget(self)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.navbar_separator = ctk.CTkFrame(self, height=1, fg_color=("#cccccc", "#333333"))
        self.navbar_separator.grid(row=0, column=0, columnspan=2, sticky="sew")

        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=1, column=0, sticky="nsew")

        self.separator = ctk.CTkFrame(self, width=1, fg_color="transparent")
        self.separator.grid(row=1, column=0, sticky="nse")

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.card = ctk.CTkFrame(
            self.main_frame,
            fg_color="#2B2B2B",
            corner_radius=26,
            border_width=1,
            border_color="#383838",
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.76, relheight=0.82)
        self.card.grid_propagate(False)

        self._build_form()

    def _load_icon(self, filename, size):
        path = os.path.join(self._assets_dir, "icons", filename)
        try:
            image = Image.open(path)
            return ctk.CTkImage(light_image=image, dark_image=image, size=size)
        except Exception:
            return None

    def _build_form(self):
        FONT_TITLE = ("TH Sarabun New", 38, "bold")
        FONT_LABEL = ("TH Sarabun New", 21, "bold")
        FONT_ENTRY = ("TH Sarabun New", 20)
        FONT_BTN = ("TH Sarabun New", 24, "bold")
        ENTRY_COLOR = ("#F4F4F4", "#F4F4F4")
        TEXT_DARK = ("#1A1A1A", "#1A1A1A")
        ACCENT = "#3F67C6"

        wrapper = ctk.CTkFrame(self.card, fg_color="transparent")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        admin_icon = self._load_icon("admin-panel_d.png", (58, 58))
        icon_label = ctk.CTkLabel(wrapper, text="", image=admin_icon)
        icon_label.image = admin_icon
        icon_label.pack(pady=(0, 14))

        ctk.CTkLabel(
            wrapper,
            text="Admin Login",
            font=FONT_TITLE,
            text_color="white",
        ).pack(pady=(0, 20))

        ctk.CTkLabel(
            wrapper,
            text="Username",
            font=FONT_LABEL,
            text_color="#F0F0F0",
            anchor="w",
        ).pack(fill="x", padx=20)

        self.username_entry = ctk.CTkEntry(
            wrapper,
            placeholder_text="Username",
            font=FONT_ENTRY,
            height=58,
            width=720,
            corner_radius=29,
            fg_color=ENTRY_COLOR,
            text_color=TEXT_DARK,
            placeholder_text_color="#B0B0B0",
            border_width=2,
            border_color="#D6D6D6",
        )
        self.username_entry.pack(fill="x", padx=20, pady=(6, 14))

        ctk.CTkLabel(
            wrapper,
            text="Password",
            font=FONT_LABEL,
            text_color="#F0F0F0",
            anchor="w",
        ).pack(fill="x", padx=20)

        self.password_entry = ctk.CTkEntry(
            wrapper,
            placeholder_text="Password",
            font=FONT_ENTRY,
            height=58,
            width=720,
            corner_radius=29,
            fg_color=ENTRY_COLOR,
            text_color=TEXT_DARK,
            placeholder_text_color="#B0B0B0",
            border_width=2,
            border_color="#D6D6D6",
            show="•",
        )
        self.password_entry.pack(fill="x", padx=20, pady=(6, 12))

        self.error_label = ctk.CTkLabel(
            wrapper,
            text="",
            font=("TH Sarabun New", 16),
            text_color="#E05A5A",
        )
        self.error_label.pack(pady=(2, 20))

        self.login_btn = ctk.CTkButton(
            wrapper,
            text="เข้าสู่ระบบ",
            font=FONT_BTN,
            height=58,
            width=720,
            corner_radius=12,
            fg_color=ACCENT,
            hover_color="#355AB0",
            text_color="white",
            command=self._on_login,
        )
        self.login_btn.pack(fill="x", padx=20)

        self.username_entry.bind("<Return>", lambda _e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda _e: self._on_login())

    def _on_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text="⚠ กรุณากรอก Username และ Password")
            return

        self.error_label.configure(text="")

        if self.login_command:
            self.login_command(username, password)
        else:
            print(f"Login: {username} / {password}")

    def show_error(self, message: str):
        self.error_label.configure(text=f"⚠ {message}")

    def on_hide(self):
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")
