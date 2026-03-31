import customtkinter as ctk
import datetime
from widgets.side_bar import SideBarWidget


class AssessorLoginScreen(ctk.CTkFrame):
    def __init__(self, master,
                 back_command=None,
                 next_command=None,
                 display_type: str = "Diagnostic",
                 hospital_name: str = "",
                 serial_number: str = "",
                 evaluator_name: str = "",
                 **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self.back_command    = back_command
        self.next_command    = next_command
        self.display_type    = display_type
        self.hospital_name   = hospital_name
        self.serial_number   = serial_number
        self.evaluator_name  = evaluator_name
        self._clock_after_id = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Sidebar ──
        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkFrame(self, width=1, fg_color=("#cccccc", "#333333")).grid(
            row=0, column=0, sticky="nse")

        # ── Main ──
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self._build_ui()
        self._tick()   # start live clock

    # ──────────────────────────────────────────────
    def _build_ui(self):
        FONT_TH      = "TH Sarabun New"
        FONT_TITLE   = (FONT_TH, 28, "bold")
        FONT_SECTION = (FONT_TH, 22, "bold")
        FONT_LABEL   = (FONT_TH, 18)
        FONT_VALUE   = (FONT_TH, 18, "bold")
        FONT_ENTRY   = (FONT_TH, 18)
        FONT_BTN     = (FONT_TH, 18, "bold")
        FONT_CLOCK   = (FONT_TH, 17)

        CARD_COLOR   = ("#222222", "#222222")
        LINE_COLOR   = ("#3a3a3a", "#3a3a3a")
        ENTRY_COLOR  = ("#f0f0f0", "#f0f0f0")
        ENTRY_TEXT   = ("#1a1a1a", "#1a1a1a")
        CLOCK_BG     = ("#2e2e2e", "#2e2e2e")
        GRAY_BTN     = ("#4a4a4a", "#4a4a4a")
        GRAY_HOVER   = ("#3a3a3a", "#3a3a3a")
        ACCENT       = "#1d5bbf"
        ACCENT_HOVER = "#174fa3"
        TEXT_WHITE   = ("white", "white")
        TEXT_GRAY    = ("#aaaaaa", "#aaaaaa")
        TEXT_SUB     = ("#cccccc", "#cccccc")

        # ── Card ──
        card = ctk.CTkFrame(
            self.main_frame, corner_radius=16,
            fg_color=CARD_COLOR, border_width=0,
        )
        card.place(relx=0.5, rely=0.5, anchor="center",
                   relwidth=0.88, relheight=0.90)
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        # ── Top: back + title ──
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 8))

        ctk.CTkButton(
            top, text="↩", font=(FONT_TH, 20, "bold"),
            width=52, height=38, corner_radius=19,
            fg_color=GRAY_BTN, hover_color=GRAY_HOVER,
            text_color="white", command=self._on_back,
        ).pack(side="left")

        ctk.CTkLabel(
            top, text="ยืนยันข้อมูล",
            font=FONT_TITLE, text_color="white",
        ).pack(side="left", expand=True)

        # ── Scrollable body ──
        body = ctk.CTkScrollableFrame(
            card, fg_color="transparent",
            scrollbar_button_color=GRAY_BTN,
        )
        body.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 8))
        body.grid_columnconfigure(1, weight=1)

        def divider(parent, row):
            ctk.CTkFrame(parent, height=1, fg_color=LINE_COLOR).grid(
                row=row, column=0, columnspan=2, sticky="ew", pady=(2, 8))

        def info_row(parent, row, label, value):
            ctk.CTkLabel(parent, text=label, font=FONT_LABEL,
                         text_color=TEXT_GRAY, anchor="w", width=180,
                         ).grid(row=row, column=0, sticky="w", pady=10)
            ctk.CTkLabel(parent, text=value, font=FONT_VALUE,
                         text_color="white", anchor="w",
                         ).grid(row=row, column=1, sticky="w", padx=20)

        # ════ Section 1: Hospital info ════
        ctk.CTkLabel(
            body,
            text=self.display_type,
            font=FONT_SECTION, text_color="white", anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(8, 2))
        divider(body, 1)

        info_row(body, 2, "ชื่อโรงพยาบาล",   self.hospital_name or "—")
        info_row(body, 3, "หมายเลขครุภัณฑ์", self.serial_number or "—")

        # ════ Section 2: Evaluator ════
        ctk.CTkLabel(
            body, text="ผู้ประเมิน",
            font=FONT_SECTION, text_color="white", anchor="w",
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(20, 2))
        divider(body, 5)

        info_row(body, 6, "ชื่อ-นามสกุล", self.evaluator_name or "—")

        # spacer
        ctk.CTkFrame(body, height=12, fg_color="transparent").grid(row=10, column=0)

        # ── Clock badge ──
        clock_frame = ctk.CTkFrame(body, corner_radius=22, fg_color=CLOCK_BG)
        clock_frame.grid(row=11, column=0, columnspan=2, sticky="w", pady=(4, 8))

        ctk.CTkLabel(clock_frame, text="วันที่และเวลาในการทดสอบ : ",
                     font=FONT_CLOCK, text_color=TEXT_SUB,
                     ).pack(side="left", padx=(16, 0), pady=10)

        self._date_lbl = ctk.CTkLabel(clock_frame, text="",
                                      font=(FONT_TH, 17, "bold"), text_color="white")
        self._date_lbl.pack(side="left", padx=8)

        self._time_lbl = ctk.CTkLabel(clock_frame, text="",
                                      font=(FONT_TH, 17, "bold"), text_color="white")
        self._time_lbl.pack(side="left", padx=(0, 16))

        # ── Bottom: ถัดไป ──
        bottom = ctk.CTkFrame(card, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="e", padx=28, pady=(4, 20))

        ctk.CTkButton(
            bottom, text="เริ่มการทดสอบ", font=FONT_BTN,
            width=160, height=46, corner_radius=23,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="white", command=self._on_next,
        ).pack()

    # ──────────────────────────────────────────────
    def _tick(self):
        now = datetime.datetime.now()
        self._date_lbl.configure(text=now.strftime("%d/%m/%Y"))
        self._time_lbl.configure(text=now.strftime("%H:%M:%S"))
        self._clock_after_id = self.after(1000, self._tick)

    def destroy(self):
        if self._clock_after_id:
            self.after_cancel(self._clock_after_id)
        super().destroy()

    # ── Callbacks ──
    def _on_back(self):
        if self.back_command:
            self.back_command()

    def _on_next(self):
        if self.next_command:
            self.next_command()

    # ── Public ──
    def update_info(self, display_type="", hospital_name="",
                    serial_number="", evaluator_name=""):
        """อัปเดตข้อมูลจากภายนอกโดยไม่ต้องสร้างหน้าใหม่"""
        self.display_type   = display_type
        self.hospital_name  = hospital_name
        self.serial_number  = serial_number
        self.evaluator_name = evaluator_name
        # rebuild UI ใหม่
        for w in self.main_frame.winfo_children():
            w.destroy()
        self._build_ui()
        self._tick()