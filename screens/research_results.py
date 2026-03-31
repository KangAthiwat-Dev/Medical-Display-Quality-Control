import customtkinter as ctk

from styles.base_colors import (
    DIVIDER_COLOR,
    HISTORY_ACCENT,
    HISTORY_ACCENT_HOVER,
    HISTORY_BUTTON_GRAY,
    HISTORY_BUTTON_GRAY_HOVER,
    HISTORY_CARD_COLOR,
    HISTORY_LINE_COLOR,
    TRANSPARENT,
    WHITE,
)
from widgets.side_bar import SideBarWidget


class ResultScreen(ctk.CTkFrame):
    def __init__(self, master,
                 retry_command=None,
                 discard_command=None,
                 save_command=None,
                 hospital_name: str = "",
                 evaluator_name: str = "",
                 display_type: str = "",
                 serial_number: str = "",
                 test_date: str = "",
                 test_time: str = "",
                 results: list | None = None,
                 **kwargs):
        kwargs.setdefault("fg_color", TRANSPARENT)
        super().__init__(master, **kwargs)

        self.retry_command = retry_command
        self.discard_command = discard_command
        self.save_command = save_command

        self.hospital_name = hospital_name
        self.evaluator_name = evaluator_name
        self.display_type = display_type
        self.serial_number = serial_number
        self.test_date = test_date
        self.test_time = test_time
        self.results = results or []

        self._saved_payload = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkFrame(self, width=1, fg_color=DIVIDER_COLOR).grid(row=0, column=0, sticky="nse")

        self.main_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self._build_ui()

    def _build_ui(self):
        FONT_TH = "TH Sarabun New"
        FONT_TITLE = (FONT_TH, 26, "bold")
        FONT_META = (FONT_TH, 17)
        FONT_META_B = (FONT_TH, 17, "bold")
        FONT_HEADER = (FONT_TH, 18, "bold")
        FONT_SECTION = (FONT_TH, 17, "bold")
        FONT_ITEM = (FONT_TH, 16)
        FONT_RESULT = (FONT_TH, 16, "bold")
        FONT_NOTE = (FONT_TH, 15)
        FONT_BTN = (FONT_TH, 17, "bold")

        HEADER_BG = ("#383838", "#383838")
        SECTION_BLUE = "#4a90d9"
        PASS_GREEN = "#4caf50"
        FAIL_RED = "#e05a5a"
        NOTE_GRAY = ("#bbbbbb", "#bbbbbb")
        TEXT_GRAY = ("#aaaaaa", "#aaaaaa")

        card = ctk.CTkFrame(self.main_frame, corner_radius=16, fg_color=HISTORY_CARD_COLOR)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)
        card.grid_rowconfigure(3, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text="ผลการประเมินคุณภาพหน้าจอ",
            font=FONT_TITLE, text_color=WHITE,
        ).grid(row=0, column=0, pady=(20, 4))

        meta = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        meta.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 4))

        def meta_pair(parent, label, value, side="left", padx=(0, 32)):
            f = ctk.CTkFrame(parent, fg_color=TRANSPARENT)
            f.pack(side=side, padx=padx)
            ctk.CTkLabel(f, text=label, font=FONT_META, text_color=TEXT_GRAY).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(f, text=value, font=FONT_META_B, text_color=WHITE).pack(side="left")

        row1 = ctk.CTkFrame(meta, fg_color=TRANSPARENT)
        row1.pack(fill="x", pady=1)
        meta_pair(row1, "โรงพยาบาล", self.hospital_name)
        meta_pair(row1, "ชื่อ-นามสกุล", self.evaluator_name)

        row2 = ctk.CTkFrame(meta, fg_color=TRANSPARENT)
        row2.pack(fill="x", pady=1)
        meta_pair(row2, self.display_type, "")
        meta_pair(row2, "หมายเลขครุภัณฑ์", self.serial_number)
        meta_pair(row2, "", self.test_date)
        meta_pair(row2, "", self.test_time)

        ctk.CTkFrame(card, height=1, fg_color=HISTORY_LINE_COLOR).grid(
            row=2, column=0, sticky="ew", padx=28, pady=(6, 0)
        )

        table_outer = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        table_outer.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 4))
        table_outer.grid_rowconfigure(1, weight=1)
        table_outer.grid_columnconfigure(0, weight=1)

        col_weights = [5, 2, 2]

        thead = ctk.CTkFrame(table_outer, corner_radius=10, fg_color=HEADER_BG)
        thead.grid(row=0, column=0, sticky="ew", pady=(8, 0))
        for i, w in enumerate(col_weights):
            thead.grid_columnconfigure(i, weight=w)

        for ci, txt in enumerate(["หัวข้อการประเมิน", "ผลการประเมิน", "หมายเหตุ"]):
            ctk.CTkLabel(
                thead, text=txt, font=FONT_HEADER, text_color=WHITE
            ).grid(row=0, column=ci, padx=16, pady=10, sticky="ew")

        scroll = ctk.CTkScrollableFrame(
            table_outer,
            fg_color=TRANSPARENT,
            scrollbar_button_color=HISTORY_BUTTON_GRAY,
            scrollbar_button_hover_color=HISTORY_BUTTON_GRAY_HOVER,
        )
        scroll.grid(row=1, column=0, sticky="nsew")
        for i, w in enumerate(col_weights):
            scroll.grid_columnconfigure(i, weight=w)
        scroll.grid_anchor("nw")

        r = 0
        for section in self.results:
            ctk.CTkLabel(
                scroll,
                text=section.get("section_title", ""),
                font=FONT_SECTION,
                text_color=SECTION_BLUE,
                anchor="w",
                wraplength=480,
                justify="left",
            ).grid(row=r, column=0, columnspan=3, sticky="w", padx=8, pady=(14, 2))
            r += 1

            for item in section.get("items", []):
                passed = item.get("passed")
                note = item.get("note", "")

                ctk.CTkLabel(
                    scroll,
                    text=item.get("title", ""),
                    font=FONT_ITEM,
                    text_color=WHITE,
                    anchor="w",
                    wraplength=420,
                    justify="left",
                ).grid(row=r, column=0, sticky="w", padx=(24, 8), pady=4)

                if passed is True:
                    res_text = "✔  ผ่าน"
                    res_color = PASS_GREEN
                elif passed is False:
                    res_text = "✘  ไม่ผ่าน"
                    res_color = FAIL_RED
                else:
                    res_text = "—"
                    res_color = TEXT_GRAY[0]

                ctk.CTkLabel(
                    scroll,
                    text=res_text,
                    font=FONT_RESULT,
                    text_color=res_color,
                    anchor="w",
                ).grid(row=r, column=1, sticky="w", padx=8, pady=4)

                ctk.CTkLabel(
                    scroll,
                    text=note,
                    font=FONT_NOTE,
                    text_color=NOTE_GRAY,
                    anchor="w",
                    wraplength=180,
                    justify="left",
                ).grid(row=r, column=2, sticky="w", padx=8, pady=4)

                r += 1
                ctk.CTkFrame(scroll, height=1, fg_color=HISTORY_LINE_COLOR).grid(
                    row=r, column=0, columnspan=3, sticky="ew", padx=4
                )
                r += 1

        bottom = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        bottom.grid(row=4, column=0, sticky="ew", padx=28, pady=(4, 20))

        ctk.CTkButton(
            bottom, text="↺  ทดสอบใหม่", font=FONT_BTN,
            width=180, height=46, corner_radius=23,
            fg_color=HISTORY_BUTTON_GRAY, hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE, command=self._on_retry,
        ).pack(side="left")

        ctk.CTkButton(
            bottom, text="บันทึกผล", font=FONT_BTN,
            width=160, height=46, corner_radius=23,
            fg_color=HISTORY_ACCENT, hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE, command=self._on_save,
        ).pack(side="right")

        ctk.CTkButton(
            bottom, text="ไม่บันทึกผล", font=FONT_BTN,
            width=160, height=46, corner_radius=23,
            fg_color=HISTORY_BUTTON_GRAY, hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE, command=self._on_discard,
        ).pack(side="right", padx=(0, 12))

    def on_show(self, results=None, hospital_name="", evaluator_name="",
                display_type="", serial_number="", test_date="", test_time="", **kwargs):
        if results is not None:
            self.results = results
            self._saved_payload = None
        if hospital_name:
            self.hospital_name = hospital_name
        if evaluator_name:
            self.evaluator_name = evaluator_name
        if display_type:
            self.display_type = display_type
        if serial_number:
            self.serial_number = serial_number
        if test_date:
            self.test_date = test_date
        if test_time:
            self.test_time = test_time

        for w in self.main_frame.winfo_children():
            w.destroy()
        self._build_ui()

    def _on_retry(self):
        if self.retry_command:
            self.retry_command()

    def _on_discard(self):
        if self.discard_command:
            self.discard_command()

    def _on_save(self):
        if self._saved_payload:
            self.master.show_screen("after_save", bypass_auth=True, saved_payload=self._saved_payload)
            return
        if self.save_command:
            payload = self.save_command(self.results)
            if payload:
                self._saved_payload = payload
                self.master.show_screen("after_save", bypass_auth=True, saved_payload=payload)

    def set_results(self, results: list):
        self.results = results
        self._saved_payload = None
        for w in self.main_frame.winfo_children():
            w.destroy()
        self._build_ui()
