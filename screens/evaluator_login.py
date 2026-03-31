import customtkinter as ctk

from widgets.side_bar import SideBarWidget


class EvaluatorLoginScreen(ctk.CTkFrame):
    def __init__(self, master, login_command=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self.login_command = login_command
        self._user_names = []

        # =============== LAYOUT ===============
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # =============== 1. SIDEBAR ===============
        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.separator = ctk.CTkFrame(self, width=1, fg_color=("#cccccc", "#333333"))
        self.separator.grid(row=0, column=0, sticky="nse")

        # =============== 2. MAIN CONTENT ===============
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        # Card กลางหน้าจอ
        self.card = ctk.CTkFrame(
            self.main_frame,
            width=480,
            corner_radius=20,
            fg_color=("#2b2b2b", "#2b2b2b"),
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a"),
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.45, relheight=0.8)
        self.card.grid_propagate(False)

        self._build_form()

    def _build_form(self):
        font_title = ("TH Sarabun New", 36, "bold")
        font_label = ("TH Sarabun New", 18)
        font_entry = ("TH Sarabun New", 18)
        font_btn = ("TH Sarabun New", 20, "bold")
        entry_color = ("#f2f2f2", "#f2f2f2")
        text_dark = ("#1a1a1a", "#1a1a1a")
        accent = "#1d5bbf"

        pad = {"padx": 48}

        ctk.CTkLabel(
            self.card,
            text="เข้าสู่ระบบผู้ประเมิน",
            font=font_title,
            text_color="white",
        ).pack(pady=(48, 32), **pad)

        ctk.CTkLabel(
            self.card,
            text="ชื่อ-นามสกุล",
            font=font_label,
            text_color=("#aaaaaa", "#aaaaaa"),
            anchor="w",
        ).pack(fill="x", **pad)

        self.username_entry = ctk.CTkComboBox(
            self.card,
            values=["กำลังโหลด..."],
            font=font_entry,
            dropdown_font=font_entry,
            height=52,
            corner_radius=26,
            fg_color=entry_color,
            text_color=text_dark,
            button_color=entry_color,
            button_hover_color="#e0e0e0",
            border_width=0,
            state="readonly",
        )
        self.username_entry.pack(fill="x", pady=(6, 20), **pad)

        ctk.CTkLabel(
            self.card,
            text="รหัสผ่าน",
            font=font_label,
            text_color=("#aaaaaa", "#aaaaaa"),
            anchor="w",
        ).pack(fill="x", **pad)

        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="รหัสผ่าน",
            font=font_entry,
            height=52,
            corner_radius=26,
            fg_color=entry_color,
            text_color=text_dark,
            placeholder_text_color=("#999999", "#999999"),
            border_width=0,
            show="•",
        )
        self.password_entry.pack(fill="x", pady=(6, 0), **pad)

        self.error_label = ctk.CTkLabel(
            self.card,
            text="",
            font=("TH Sarabun New", 15),
            text_color="#e05a5a",
        )
        self.error_label.pack(pady=(8, 0))

        self.login_btn = ctk.CTkButton(
            self.card,
            text="เข้าสู่ระบบ",
            font=font_btn,
            height=56,
            corner_radius=28,
            fg_color=accent,
            hover_color="#174fa3",
            text_color="white",
            command=self._on_login,
        )
        self.login_btn.pack(side="bottom", fill="x", pady=48, **pad)

        self.username_entry.bind("<Return>", lambda _e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda _e: self._on_login())

    def _set_usernames(self, names):
        self._user_names = list(names)
        if not self._user_names:
            placeholder = "ยังไม่มีรายชื่อในระบบ"
            self.username_entry.configure(values=[placeholder])
            self.username_entry.set(placeholder)
            return

        self.username_entry.configure(values=self._user_names)
        current = self.username_entry.get().strip()
        if current in self._user_names:
            self.username_entry.set(current)
        else:
            self.username_entry.set(self._user_names[0])

    def _clear_form(self, keep_users=True):
        if not keep_users:
            self._set_usernames([])
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")

    def _on_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not self._user_names:
            self.error_label.configure(text="⚠ ยังไม่มีรายชื่อผู้ประเมินในระบบ")
            return

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
        self.password_entry.focus()

    def on_show(self, **kwargs):
        from database.database import get_all_users

        users = get_all_users()
        names = [f"{u['name']} {u['lastname']}".strip() for u in users]
        self._set_usernames(names)
        self._clear_form(keep_users=True)
        self.after(10, self.username_entry.focus)

    def on_hide(self):
        self._clear_form(keep_users=True)
