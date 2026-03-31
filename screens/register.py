import customtkinter as ctk
import tkinter.messagebox
from widgets.side_bar import SideBarWidget


class RegisterScreen(ctk.CTkFrame):
    def __init__(self, master,
                 back_command=None,
                 save_hospital_command=None,
                 add_evaluator_command=None,
                 view_evaluators_command=None,
                 **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self.back_command = back_command
        self.save_hospital_command = save_hospital_command
        self.add_evaluator_command = add_evaluator_command
        self.view_evaluators_command = view_evaluators_command

        # ── Color Constants ──
        self.ENTRY_COLOR  = ("#3d3d3d", "#3d3d3d")
        self.ACCENT       = "#1d5bbf"
        self.ACCENT_HOVER = "#174fa3"
        self.GRAY_BTN     = ("#4a4a4a", "#4a4a4a")
        self.GRAY_HOVER   = ("#3a3a3a", "#3a3a3a")

        # ── Layout ──
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Sidebar ── (ดักการกด Sidebar ไปหน้าอื่นด้วย)
        self.sidebar = SideBarWidget(self, navigate_command=self._on_sidebar_navigate)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkFrame(self, width=1, fg_color=("#cccccc", "#333333")).grid(row=0, column=0, sticky="nse")

        # ── Main ──
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self._build_ui()

    # ────────────────────────────────────────────
    def _build_ui(self):
        FONT_TH      = "TH Sarabun New"
        FONT_TITLE   = (FONT_TH, 28, "bold")
        FONT_SECTION = (FONT_TH, 22, "bold")
        FONT_LABEL   = (FONT_TH, 18)
        FONT_ENTRY   = (FONT_TH, 18)
        FONT_BTN     = (FONT_TH, 18, "bold")

        CARD_COLOR   = ("#2b2b2b", "#2b2b2b")
        ENTRY_TEXT   = ("white", "white")
        PLACEHOLDER  = ("#888888", "#888888")
        LABEL_COLOR  = ("white", "white")
        SECTION_LINE = ("#444444", "#444444")

        # ── Card ──
        card = ctk.CTkFrame(self.main_frame, corner_radius=16,
                            fg_color=CARD_COLOR, border_width=2,
                            border_color=("#3a3a3a", "#3a3a3a"))
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)

        # ── Back + Title row ──
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=28, pady=(22, 4))

        ctk.CTkButton(
            top_row, text="↩", font=(FONT_TH, 20, "bold"),
            width=52, height=38, corner_radius=19,
            fg_color=self.GRAY_BTN, hover_color=self.GRAY_HOVER,
            text_color="white", command=self._on_back,
        ).pack(side="left")

        ctk.CTkLabel(
            top_row, text="ลงทะเบียน",
            font=FONT_TITLE, text_color="white"
        ).pack(side="left", expand=True)

        # ── Body (เปลี่ยนจาก ScrollableFrame เป็น CTkFrame ธรรมดาตามที่ขอ) ──
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        def section_header(parent, text):
            ctk.CTkLabel(parent, text=text, font=FONT_SECTION,
                         text_color="white", anchor="w").pack(fill="x", pady=(18, 2))
            ctk.CTkFrame(parent, height=1, fg_color=SECTION_LINE).pack(fill="x", pady=(0, 12))

        def labeled_entry(parent, label, placeholder, show=None):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=6)
            ctk.CTkLabel(row, text=label, font=FONT_LABEL,
                         text_color=LABEL_COLOR, width=160, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(
                row, placeholder_text=placeholder,
                font=FONT_ENTRY, height=44, corner_radius=22,
                fg_color=self.ENTRY_COLOR, text_color=ENTRY_TEXT,
                placeholder_text_color=PLACEHOLDER,
                border_width=0, show=show or "",
            )
            entry.pack(side="left", fill="x", expand=True)
            return entry

        # ════ Section 1: Hospital ════
        section_header(body, "ข้อมูลโรงพยาบาล และอุปกรณ์")

        self.hospital_name_entry  = labeled_entry(body, "ชื่อโรงพยาบาล",  "โรงพยาบาล")
        self.hospital_serial_entry = labeled_entry(body, "หมายเลขครุภัณฑ์", "หมายเลขครุภัณฑ์")

        self.hospital_error = ctk.CTkLabel(body, text="", font=(FONT_TH, 15), text_color="#e05a5a")
        self.hospital_error.pack(anchor="e", pady=(0, 4))

        self.save_hosp_btn = ctk.CTkButton(
            body, text="บันทึก", font=FONT_BTN,
            height=44, corner_radius=22, width=180,
            fg_color=self.ACCENT, hover_color=self.ACCENT_HOVER, text_color="white",
            command=self._on_save_hospital,
        )
        self.save_hosp_btn.pack(anchor="e", pady=(0, 8))

        # ════ Section 2: Evaluator ════
        section_header(body, "เพิ่มผู้ประเมิน")

        self.eval_first_entry    = labeled_entry(body, "ชื่อ",      "ชื่อจริง")
        self.eval_last_entry     = labeled_entry(body, "นามสกุล",   "นามสกุล")
        self.eval_password_entry = labeled_entry(body, "รหัสผ่าน",  "รหัสผ่าน", show="•")

        # toggle show/hide password
        self._pw_visible = False
        self._add_pw_toggle(self.eval_password_entry)

        self.eval_error = ctk.CTkLabel(body, text="", font=(FONT_TH, 15), text_color="#e05a5a")
        self.eval_error.pack(anchor="e", pady=(0, 4))

        # bottom row: ดูรายชื่อ | เพิ่มผู้ประเมิน
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x", pady=(4, 12))

        ctk.CTkButton(
            btn_row, text="ดูรายชื่อผู้ประเมิน", font=FONT_BTN,
            height=44, corner_radius=22, width=200,
            fg_color=self.GRAY_BTN, hover_color=self.GRAY_HOVER, text_color="white",
            command=self._on_view_evaluators,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row, text="เพิ่มผู้ประเมิน", font=FONT_BTN,
            height=44, corner_radius=22, width=200,
            fg_color=self.ACCENT, hover_color=self.ACCENT_HOVER, text_color="white",
            command=self._on_add_evaluator,
        ).pack(side="right")

    # ── password eye toggle ──
    def _add_pw_toggle(self, entry: ctk.CTkEntry):
        def toggle():
            self._pw_visible = not self._pw_visible
            entry.configure(show="" if self._pw_visible else "•")
            eye_btn.configure(text="🙈" if self._pw_visible else "👁")

        # วาง eye button ทับบน entry ด้านขวา
        eye_btn = ctk.CTkButton(
            entry, text="👁", font=("Segoe UI Emoji", 14),
            width=32, height=30, corner_radius=15,
            fg_color="transparent", hover_color="#555555",
            text_color="white", command=toggle,
        )
        eye_btn.place(relx=1.0, rely=0.5, anchor="e", x=-6)

    # ── Callbacks ──
    def _prompt_exit(self, exit_func):
        """โชว์ Alert ถามว่าแน่ใจหรือไม่ที่จะออก"""
        ans = tkinter.messagebox.askyesno("ยืนยันการออก", "แน่ใจหรือไม่ว่าจะออกจากหน้าลงทะเบียน?\n\nหากออกจากหน้านี้แล้ว คุณจะต้องเข้าสู่ระบบบัญชี Admin ใหม่อีกครั้งเพื่อกลับเข้ามา")
        if ans:
            exit_func()

    def _on_sidebar_navigate(self, screen_name):
        self._prompt_exit(lambda: self.master.show_screen(screen_name))

    def _on_back(self):
        if self.back_command:
            self._prompt_exit(self.back_command)

    def _on_save_hospital(self):
        # ถ้าอยู่ในสถานะ แก้ไขข้อมูล ให้เปลี่ยนกลับมาเป็นกล่องกรอก
        if self.save_hosp_btn.cget("text") == "แก้ไขข้อมูล":
            self.hospital_name_entry.configure(state="normal", fg_color=self.ENTRY_COLOR)
            self.hospital_serial_entry.configure(state="normal", fg_color=self.ENTRY_COLOR)
            self.save_hosp_btn.configure(text="บันทึก", fg_color=self.ACCENT, hover_color=self.ACCENT_HOVER)
            return

        # ถ้าอยู่ในสถานะ บันทึก ให้ดึงข้อมูลมาเซฟ
        name   = self.hospital_name_entry.get().strip()
        serial = self.hospital_serial_entry.get().strip()
        if not name or not serial:
            self.hospital_error.configure(text="⚠ กรุณากรอกข้อมูลให้ครบ")
            return
            
        self.hospital_error.configure(text="")
        if self.save_hospital_command:
            self.save_hospital_command(name, serial)
            
        # พอเซฟเสร็จ ปรับกล่องกรอกให้กลืนไปกับพื้นหลัง (ทำหน้าที่เหมือน Label)
        self.hospital_name_entry.configure(state="disabled", fg_color=("#2b2b2b", "#2b2b2b"))
        self.hospital_serial_entry.configure(state="disabled", fg_color=("#2b2b2b", "#2b2b2b"))
        self.save_hosp_btn.configure(text="แก้ไขข้อมูล", fg_color=self.GRAY_BTN, hover_color=self.GRAY_HOVER)

    def _on_add_evaluator(self):
        first = self.eval_first_entry.get().strip()
        last  = self.eval_last_entry.get().strip()
        pw    = self.eval_password_entry.get().strip()
        if not first or not last or not pw:
            self.eval_error.configure(text="⚠ กรุณากรอกข้อมูลให้ครบ")
            return
            
        self.eval_error.configure(text="")
        if self.add_evaluator_command:
            self.add_evaluator_command(first, last, pw)
            
    def clear_evaluator_fields(self):
        """ถูกเรียกมาจาก app.py เมื่อบันทึกสำเร็จ เพื่อเคลียร์ช่องสำหรับกรอกคนต่อไป"""
        self.eval_first_entry.delete(0, "end")
        self.eval_last_entry.delete(0, "end")
        self.eval_password_entry.delete(0, "end")
        self.eval_error.configure(text_color="#4de05a", text="✓ เพิ่มข้อมูลผู้ประเมินสำเร็จ")

    def _on_view_evaluators(self):
        if self.view_evaluators_command:
            self.view_evaluators_command()

    # ── เรียกจากภายนอกเพื่อแสดง error ──
    def show_hospital_error(self, msg: str):
        self.hospital_error.configure(text_color="#e05a5a", text=f"⚠ {msg}")

    def show_eval_error(self, msg: str):
        self.eval_error.configure(text_color="#e05a5a", text=f"⚠ {msg}")