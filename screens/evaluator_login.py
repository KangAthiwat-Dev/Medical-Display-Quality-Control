import customtkinter as ctk

from widgets.side_bar import SideBarWidget

class EvaluatorLoginScreen(ctk.CTkFrame):
    def __init__(self, master, login_command=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self.login_command = login_command

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
        FONT_TITLE  = ("TH Sarabun New", 36, "bold")
        FONT_LABEL  = ("TH Sarabun New", 18)
        FONT_ENTRY  = ("TH Sarabun New", 18)
        FONT_BTN    = ("TH Sarabun New", 20, "bold")
        ENTRY_COLOR = ("#f2f2f2", "#f2f2f2")
        TEXT_DARK   = ("#1a1a1a", "#1a1a1a")
        ACCENT      = "#1d5bbf"

        pad = {"padx": 48}

        # ── หัวข้อ ──
        ctk.CTkLabel(
            self.card, text="เข้าสู่ระบบผู้ประเมิน",
            font=FONT_TITLE, text_color="white"
        ).pack(pady=(48, 32), **pad)

        # ── Username ──
        ctk.CTkLabel(
            self.card, text="ชื่อ-นามสกุล",
            font=FONT_LABEL, text_color=("#aaaaaa", "#aaaaaa"), anchor="w"
        ).pack(fill="x", **pad)

        self.username_entry = ctk.CTkComboBox(
            self.card,
            values=["กำลังโหลด..."],
            font=FONT_ENTRY,
            dropdown_font=FONT_ENTRY,
            height=52,
            corner_radius=26,
            fg_color=ENTRY_COLOR,
            text_color=TEXT_DARK,
            button_color=ENTRY_COLOR,
            button_hover_color="#e0e0e0",
            border_width=0,
            state="readonly",
        )
        self.username_entry.pack(fill="x", pady=(6, 20), **pad)

        # ── Password ──
        ctk.CTkLabel(
            self.card, text="รหัสผ่าน",
            font=FONT_LABEL, text_color=("#aaaaaa", "#aaaaaa"), anchor="w"
        ).pack(fill="x", **pad)

        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="รหัสผ่าน",
            font=FONT_ENTRY,
            height=52,
            corner_radius=26,
            fg_color=ENTRY_COLOR,
            text_color=TEXT_DARK,
            placeholder_text_color=("#999999", "#999999"),
            border_width=0,
            show="•",
        )
        self.password_entry.pack(fill="x", pady=(6, 0), **pad)

        # ── Error label (ซ่อนไว้ก่อน) ──
        self.error_label = ctk.CTkLabel(
            self.card, text="",
            font=("TH Sarabun New", 15),
            text_color="#e05a5a"
        )
        self.error_label.pack(pady=(8, 0))

        # ── ปุ่มเข้าสู่ระบบ ──
        self.login_btn = ctk.CTkButton(
            self.card,
            text="เข้าสู่ระบบ",
            font=FONT_BTN,
            height=56,
            corner_radius=28,
            fg_color=ACCENT,
            hover_color="#174fa3",
            text_color="white",
            command=self._on_login,
        )
        self.login_btn.pack(side="bottom", fill="x", pady=48, **pad)

        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self._on_login())

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
            # fallback: แค่ print ถ้ายังไม่มี command ส่งมา
            print(f"Login: {username} / {password}")

    def show_error(self, message: str):
        """เรียกจากภายนอกเพื่อแสดง error เช่น 'รหัสผ่านไม่ถูกต้อง'"""
        self.error_label.configure(text=f"⚠ {message}")

    def on_show(self, **kwargs):
        """ถูกเรียกอัตโนมัติจาก app.py เมื่อหน้านี้แสดงขึ้นมา เพื่อโหลดรายชื่อล่าสุดเสมอ"""
        from database.database import get_all_users
        users = get_all_users()
        
        # จัดรูปแบบชื่อ นามสกุลรวมกัน
        names = [f"{u['name']} {u['lastname']}".strip() for u in users]
        
        if not names:
            self.username_entry.configure(values=["ยังไม่มีรายชื่อในระบบ"])
            self.username_entry.set("ยังไม่มีรายชื่อในระบบ")
        else:
            self.username_entry.configure(values=names)
            self.username_entry.set(names[0]) # เลือกคนแรกอัตโนมัติ

    def on_hide(self):
        """ถูกเรียกอัตโนมัติจาก app.py เมื่อสลับไปหน้าอื่น เพื่อล้างค่านอกจากลิสต์ที่ปลอดภัยทิ้งทั้งหมด"""
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")