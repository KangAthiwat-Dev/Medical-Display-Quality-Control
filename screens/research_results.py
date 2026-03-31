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

        self._ui_built = False
        self._meta_value_labels = {}
        self._body = None
        self._table_entries = []
        self._empty_label = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkFrame(self, width=1, fg_color=DIVIDER_COLOR).grid(row=0, column=0, sticky="nse")

        self.main_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self._build_ui()

    def _build_ui(self):
        if self._ui_built:
            return

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
        self._section_blue = "#4a90d9"
        self._pass_green = "#4caf50"
        self._fail_red = "#e05a5a"
        self._note_gray = ("#bbbbbb", "#bbbbbb")
        self._text_gray = ("#aaaaaa", "#aaaaaa")

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

        row1 = ctk.CTkFrame(meta, fg_color=TRANSPARENT)
        row1.pack(fill="x", pady=1)
        row2 = ctk.CTkFrame(meta, fg_color=TRANSPARENT)
        row2.pack(fill="x", pady=1)

        def meta_pair(parent, label, key, side="left", padx=(0, 32)):
            wrap = ctk.CTkFrame(parent, fg_color=TRANSPARENT)
            wrap.pack(side=side, padx=padx)
            ctk.CTkLabel(wrap, text=label, font=FONT_META, text_color=self._text_gray).pack(side="left", padx=(0, 6))
            value_lbl = ctk.CTkLabel(wrap, text="", font=FONT_META_B, text_color=WHITE)
            value_lbl.pack(side="left")
            self._meta_value_labels[key] = value_lbl

        meta_pair(row1, "โรงพยาบาล", "hospital_name")
        meta_pair(row1, "ชื่อ-นามสกุล", "evaluator_name")

        meta_pair(row2, "", "display_type")
        meta_pair(row2, "หมายเลขครุภัณฑ์", "serial_number")
        meta_pair(row2, "", "test_date")
        meta_pair(row2, "", "test_time")

        ctk.CTkFrame(card, height=1, fg_color=HISTORY_LINE_COLOR).grid(
            row=2, column=0, sticky="ew", padx=28, pady=(6, 0)
        )

        table_outer = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        table_outer.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 4))
        table_outer.grid_rowconfigure(1, weight=1)
        table_outer.grid_columnconfigure(0, weight=1)

        self._col_weights = [5, 2, 2]

        thead = ctk.CTkFrame(table_outer, corner_radius=10, fg_color=HEADER_BG)
        thead.grid(row=0, column=0, sticky="ew", pady=(8, 0))
        for i, w in enumerate(self._col_weights):
            thead.grid_columnconfigure(i, weight=w)

        for ci, txt in enumerate(["หัวข้อการประเมิน", "ผลการประเมิน", "หมายเหตุ"]):
            ctk.CTkLabel(
                thead, text=txt, font=FONT_HEADER, text_color=WHITE
            ).grid(row=0, column=ci, padx=16, pady=10, sticky="ew")

        body = ctk.CTkScrollableFrame(
            table_outer,
            fg_color=TRANSPARENT,
            scrollbar_button_color=HISTORY_BUTTON_GRAY,
            scrollbar_button_hover_color=HISTORY_BUTTON_GRAY_HOVER,
        )
        body.grid(row=1, column=0, sticky="nsew")
        for i, w in enumerate(self._col_weights):
            body.grid_columnconfigure(i, weight=w)
        body.grid_anchor("nw")
        self._body = body

        self._empty_label = ctk.CTkLabel(
            body,
            text="ยังไม่มีผลการประเมินสำหรับแสดงผล",
            font=FONT_ITEM,
            text_color=self._text_gray,
            anchor="w",
            justify="left",
        )
        self._empty_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=8, pady=(14, 2))
        self._empty_label.grid_remove()

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

        self._font_section = FONT_SECTION
        self._font_item = FONT_ITEM
        self._font_result = FONT_RESULT
        self._font_note = FONT_NOTE

        self._ui_built = True

    def _flatten_results(self):
        entries = []
        for section in self.results or []:
            entries.append(("section", {"title": section.get("section_title", "")}))
            for item in section.get("items", []) or []:
                entries.append(("item", item))
        return entries

    def _ensure_table_entry(self, kind: str, idx: int):
        if self._body is None:
            return None

        while len(self._table_entries) <= idx:
            self._table_entries.append(None)

        if self._table_entries[idx] is not None and self._table_entries[idx].get("kind") == kind:
            return self._table_entries[idx]

        old = self._table_entries[idx]
        if old:
            for w in old.get("widgets", []):
                w.destroy()

        widgets = []
        if kind == "section":
            title_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=self._font_section,
                text_color=self._section_blue,
                anchor="w",
                wraplength=480,
                justify="left",
            )
            widgets = [title_lbl]
            entry = {"kind": "section", "title": title_lbl, "widgets": widgets}
        else:
            title_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=self._font_item,
                text_color=WHITE,
                anchor="w",
                wraplength=420,
                justify="left",
            )
            result_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=self._font_result,
                text_color=self._text_gray[0],
                anchor="w",
            )
            note_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=self._font_note,
                text_color=self._note_gray,
                anchor="w",
                wraplength=180,
                justify="left",
            )
            divider = ctk.CTkFrame(self._body, height=1, fg_color=HISTORY_LINE_COLOR)
            widgets = [title_lbl, result_lbl, note_lbl, divider]
            entry = {
                "kind": "item",
                "title": title_lbl,
                "result": result_lbl,
                "note": note_lbl,
                "divider": divider,
                "widgets": widgets,
            }

        self._table_entries[idx] = entry
        return entry

    def _update_view(self):
        self._build_ui()

        values = {
            "hospital_name": self.hospital_name,
            "evaluator_name": self.evaluator_name,
            "display_type": self.display_type,
            "serial_number": self.serial_number,
            "test_date": self.test_date,
            "test_time": self.test_time,
        }
        for key, lbl in self._meta_value_labels.items():
            lbl.configure(text=values.get(key, ""))

        entries = self._flatten_results()

        if not entries:
            self._empty_label.grid()
        else:
            self._empty_label.grid_remove()

        row_cursor = 0
        for idx, (kind, payload) in enumerate(entries):
            entry = self._ensure_table_entry(kind, idx)
            if kind == "section":
                entry["title"].configure(text=payload.get("title", ""))
                entry["title"].grid(row=row_cursor, column=0, columnspan=3, sticky="w", padx=8, pady=(14, 2))
                row_cursor += 1
            else:
                passed = payload.get("passed")
                note = payload.get("note", "")

                if passed is True:
                    res_text = "✔  ผ่าน"
                    res_color = self._pass_green
                elif passed is False:
                    res_text = "✘  ไม่ผ่าน"
                    res_color = self._fail_red
                else:
                    res_text = "—"
                    res_color = self._text_gray[0]

                entry["title"].configure(text=payload.get("title", ""))
                entry["result"].configure(text=res_text, text_color=res_color)
                entry["note"].configure(text=note)

                entry["title"].grid(row=row_cursor, column=0, sticky="w", padx=(24, 8), pady=4)
                entry["result"].grid(row=row_cursor, column=1, sticky="w", padx=8, pady=4)
                entry["note"].grid(row=row_cursor, column=2, sticky="w", padx=8, pady=4)
                row_cursor += 1
                entry["divider"].grid(row=row_cursor, column=0, columnspan=3, sticky="ew", padx=4)
                row_cursor += 1

        for idx in range(len(entries), len(self._table_entries)):
            entry = self._table_entries[idx]
            if not entry:
                continue
            for w in entry.get("widgets", []):
                w.grid_remove()

        if self._body is not None:
            self.after(0, lambda: self._body._parent_canvas.yview_moveto(0))

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

        self._update_view()

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
        self._update_view()
