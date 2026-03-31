import customtkinter as ctk


class EvaluatorEditScreen(ctk.CTkFrame):
    def __init__(self, master, back_command=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self.back_command = back_command
        self.evaluator_data = None
        self.confirmed_pw = None
        self._ui_built = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        from widgets.side_bar import SideBarWidget
        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkFrame(self, width=1, fg_color=("#cccccc", "#333333")).grid(row=0, column=0, sticky="nse")

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.FONT_TH = "TH Sarabun New"
        self.FONT_TITLE = (self.FONT_TH, 28, "bold")
        self.FONT_ROW = (self.FONT_TH, 18)
        self.GRAY_BTN = ("#4a4a4a", "#4a4a4a")
        self.GRAY_HOVER = ("#3a3a3a", "#3a3a3a")
        self.ACCENT = "#1d5bbf"
        self.ACCENT_HOVER = "#174fa3"

        self._build_ui()

    def _build_ui(self):
        if self._ui_built:
            return

        self.card = ctk.CTkFrame(
            self.main_frame,
            corner_radius=16,
            fg_color=("#2b2b2b", "#2b2b2b"),
            border_width=2,
            border_color=("#3a3a3a", "#3a3a3a"),
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.88, relheight=0.88)

        self._step1_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self._step2_frame = ctk.CTkFrame(self.card, fg_color="transparent")

        self._build_step1()
        self._build_step2()

        self._ui_built = True
        self._show_step(1)

    def _build_step1(self):
        pad = {"padx": 48}

        top = ctk.CTkFrame(self._step1_frame, fg_color="transparent")
        top.pack(fill="x", padx=28, pady=(22, 0))

        ctk.CTkButton(
            top,
            text="↩",
            font=(self.FONT_TH, 20, "bold"),
            width=52,
            height=38,
            corner_radius=19,
            fg_color=self.GRAY_BTN,
            hover_color=self.GRAY_HOVER,
            text_color="white",
            command=self.back_command,
        ).pack(side="left")

        ctk.CTkLabel(
            self._step1_frame,
            text="กรุณายืนยันรหัสผ่านเพื่อแก้ไข",
            font=self.FONT_TITLE,
            text_color="white",
        ).pack(pady=(40, 10), **pad)

        self._step1_name_label = ctk.CTkLabel(
            self._step1_frame,
            text="",
            font=(self.FONT_ROW[0], 20),
            text_color="#cccccc",
        )
        self._step1_name_label.pack(pady=(0, 24), **pad)

        row_frame = ctk.CTkFrame(self._step1_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 8), **pad)
        row_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row_frame,
            text="ยืนยันรหัสผ่าน",
            font=self.FONT_ROW,
            text_color="white",
        ).grid(row=0, column=0, sticky="w", padx=(0, 16))

        self._step1_pw_entry = ctk.CTkEntry(
            row_frame,
            placeholder_text="Password",
            font=self.FONT_ROW,
            height=48,
            corner_radius=24,
            fg_color="#f2f2f2",
            text_color="#1a1a1a",
            show="*",
            border_width=0,
        )
        self._step1_pw_entry.grid(row=0, column=1, sticky="ew")
        self._step1_pw_entry.bind("<Return>", lambda _e: self._confirm_password())

        self._step1_error_label = ctk.CTkLabel(
            self._step1_frame,
            text="",
            font=(self.FONT_ROW[0], 16),
            text_color="#e05a5a",
        )
        self._step1_error_label.pack(pady=(0, 20))

        btn_frame = ctk.CTkFrame(self._step1_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 40), **pad)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_frame,
            text="ยกเลิก",
            font=(self.FONT_ROW[0], 20, "bold"),
            height=52,
            corner_radius=26,
            fg_color="#f2f2f2",
            hover_color="#e0e0e0",
            text_color="#1a1a1a",
            command=self.back_command,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="ยืนยัน",
            font=(self.FONT_ROW[0], 20, "bold"),
            height=52,
            corner_radius=26,
            fg_color=self.ACCENT,
            hover_color=self.ACCENT_HOVER,
            text_color="white",
            command=self._confirm_password,
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _build_step2(self):
        pad = {"padx": 48}

        top = ctk.CTkFrame(self._step2_frame, fg_color="transparent")
        top.pack(fill="x", padx=28, pady=(22, 0))

        ctk.CTkButton(
            top,
            text="↩",
            font=(self.FONT_TH, 20, "bold"),
            width=52,
            height=38,
            corner_radius=19,
            fg_color=self.GRAY_BTN,
            hover_color=self.GRAY_HOVER,
            text_color="white",
            command=self.back_command,
        ).pack(side="left")

        ctk.CTkLabel(
            self._step2_frame,
            text="แก้ไขข้อมูล",
            font=self.FONT_TITLE,
            text_color="white",
        ).pack(pady=(10, 10), **pad)

        self._step2_name_label = ctk.CTkLabel(
            self._step2_frame,
            text="",
            font=(self.FONT_ROW[0], 20),
            text_color="#cccccc",
        )
        self._step2_name_label.pack(pady=(0, 24), **pad)

        form = ctk.CTkFrame(self._step2_frame, fg_color="transparent")
        form.pack(fill="x", pady=(0, 8), **pad)
        form.grid_columnconfigure(1, weight=1)

        self._first_entry = self._make_form_row(form, 0, "ชื่อ", "ชื่อจริง")
        self._last_entry = self._make_form_row(form, 1, "นามสกุล", "นามสกุล")
        self._new_pw_entry = self._make_form_row(
            form,
            2,
            "รหัสผ่านใหม่",
            "รหัสผ่านใหม่ (ปล่อยว่างถ้าไม่เปลี่ยน)",
            is_pw=True,
        )
        self._new_pw_entry.bind("<Return>", lambda _e: self._save_changes())

        self._step2_error_label = ctk.CTkLabel(
            self._step2_frame,
            text="",
            font=(self.FONT_ROW[0], 16),
            text_color="#e05a5a",
        )
        self._step2_error_label.pack(pady=(0, 20))

        btn_frame = ctk.CTkFrame(self._step2_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 16), **pad)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_frame,
            text="ยกเลิก",
            font=(self.FONT_ROW[0], 20, "bold"),
            height=52,
            corner_radius=26,
            fg_color="#f2f2f2",
            hover_color="#e0e0e0",
            text_color="#1a1a1a",
            command=self.back_command,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="บันทึก",
            font=(self.FONT_ROW[0], 20, "bold"),
            height=52,
            corner_radius=26,
            fg_color=self.ACCENT,
            hover_color=self.ACCENT_HOVER,
            text_color="white",
            command=self._save_changes,
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _make_form_row(self, parent, row, label_text, placeholder, is_pw=False):
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=self.FONT_ROW,
            text_color="white",
        ).grid(row=row, column=0, sticky="w", padx=(0, 16), pady=8)

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            font=self.FONT_ROW,
            height=48,
            corner_radius=24,
            fg_color="#f2f2f2",
            text_color="#1a1a1a",
            border_width=0,
            show="*" if is_pw else "",
        )
        entry.grid(row=row, column=1, sticky="ew", pady=8)

        if is_pw:
            def toggle():
                entry.configure(show="" if entry.cget("show") == "*" else "*")

            eye = ctk.CTkButton(
                entry,
                text="👁",
                font=("Segoe UI Emoji", 14),
                width=32,
                height=32,
                corner_radius=16,
                fg_color="#f2f2f2",
                hover_color="#e0e0e0",
                text_color="#666666",
                command=toggle,
            )
            eye.place(relx=1.0, rely=0.5, anchor="e", x=-8)

        return entry

    def _show_step(self, step: int):
        self._step1_frame.pack_forget()
        self._step2_frame.pack_forget()
        if step == 1:
            self._step1_frame.pack(fill="both", expand=True)
            self._step1_pw_entry.focus_set()
        else:
            self._step2_frame.pack(fill="both", expand=True)
            self._first_entry.focus_set()

    def on_show(self, evaluator_data=None, **kwargs):
        if evaluator_data:
            self.evaluator_data = evaluator_data

        self.confirmed_pw = None
        ev = self.evaluator_data or {}
        fname = f"{ev.get('first', '')} {ev.get('last', '')}".strip()
        self._step1_name_label.configure(text=f'แก้ไขข้อมูลของคุณ "{fname}"')
        self._step2_name_label.configure(text=f'แก้ไขข้อมูลของคุณ "{fname}"')

        self._step1_pw_entry.delete(0, "end")
        self._step1_error_label.configure(text="")
        self._step2_error_label.configure(text="")

        self._first_entry.delete(0, "end")
        self._first_entry.insert(0, ev.get("first", ""))
        self._last_entry.delete(0, "end")
        self._last_entry.insert(0, ev.get("last", ""))
        self._new_pw_entry.delete(0, "end")
        self._new_pw_entry.configure(show="*")

        self._show_step(1)

    def on_hide(self, **kwargs):
        self.confirmed_pw = None
        self._step1_pw_entry.delete(0, "end")
        self._step1_error_label.configure(text="")
        self._step2_error_label.configure(text="")
        self._new_pw_entry.delete(0, "end")
        self._new_pw_entry.configure(show="*")

    def _confirm_password(self):
        ev = self.evaluator_data or {}
        pw = self._step1_pw_entry.get().strip()
        if not pw:
            self._step1_error_label.configure(text="⚠ กรุณากรอกรหัสผ่าน")
            return

        from database.database import verify_user_password

        if verify_user_password(ev.get("id", 0), pw):
            self.confirmed_pw = pw
            self._step1_error_label.configure(text="")
            self._show_step(2)
        else:
            self._step1_error_label.configure(text="⚠ รหัสผ่านไม่ถูกต้อง")

    def _save_changes(self):
        ev = self.evaluator_data or {}
        new_first = self._first_entry.get().strip()
        new_last = self._last_entry.get().strip()
        new_pw = self._new_pw_entry.get().strip()

        if not new_first:
            self._step2_error_label.configure(text="⚠ กรุณากรอกชื่ออย่างน้อย 1 ตัวอักษร")
            return

        final_pw = new_pw if new_pw else self.confirmed_pw

        from database.database import update_user

        err = update_user(ev["id"], new_first, new_last, final_pw)
        if err:
            self._step2_error_label.configure(text=f"⚠ {err}")
            return

        self._step2_error_label.configure(text="")
        if hasattr(self.master, "handle_view_evaluators"):
            self.master.handle_view_evaluators(bypass_auth=True)
        elif self.back_command:
            self.back_command()
