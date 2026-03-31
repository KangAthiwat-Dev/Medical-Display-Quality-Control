import customtkinter as ctk
from datetime import datetime

from constants.evaluation_questions import TEST_CONFIG
from styles.base_colors import (
    DIVIDER_COLOR,
    HISTORY_ACCENT,
    HISTORY_ACCENT_HOVER,
    HISTORY_BUTTON_GRAY,
    HISTORY_BUTTON_GRAY_HOVER,
    HISTORY_CARD_COLOR,
    HISTORY_LINE_COLOR,
    HISTORY_ROW_HOVER,
    HISTORY_ROW_SELECTED,
    HISTORY_TEXT_GRAY,
    TRANSPARENT,
    WHITE,
)
from widgets.side_bar import SideBarWidget


DISPLAY_TYPE_LABELS = {
    "diagnostic": "Diagnostic",
    "modality": "Modality",
    "clinic": "Clinical",
    "clinical": "Clinical",
}

PERIOD_LABELS = {
    "monthly": "การประเมินรายเดือน",
    "quarterly": "การประเมินราย 3 เดือน",
    "annual": "การประเมินประจำปี",
}

SECTION_BLUE = "#79A7FF"
PASS_GREEN = "#61B35C"
FAIL_RED = "#E05A5A"
HEADER_BG = ("#5B5E64", "#5B5E64")


class HistoryDetailScreen(ctk.CTkFrame):
    def __init__(self, master, back_command=None, baseline_command=None, export_command=None, **kwargs):
        kwargs.setdefault("fg_color", TRANSPARENT)
        super().__init__(master, **kwargs)

        self.back_command = back_command
        self.baseline_command = baseline_command
        self.export_command = export_command

        self.evaluation = None
        self.results = []
        self._has_answer_data = False
        self._baseline_dialog = None
        self._baseline_selected = None
        self._baseline_rows = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkFrame(self, width=1, fg_color=DIVIDER_COLOR).grid(row=0, column=0, sticky="nse")

        self.main_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self._build_ui()

    def on_show(self, evaluation_id=None, **kwargs):
        if evaluation_id is not None:
            from database.database import get_evaluation

            self.evaluation = get_evaluation(evaluation_id)
            self.results = self._build_results()

        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self._build_ui()

    def _build_results(self):
        if not self.evaluation:
            self._has_answer_data = False
            return []

        dtype = self.evaluation.get("screen_type", "")
        period = self.evaluation.get("period", "")
        answers = self.evaluation.get("answers", {})
        self._has_answer_data = bool(answers)
        groups = TEST_CONFIG.get(dtype, {}).get(period, [])

        results = []
        for group in groups:
            items = group.get("items")
            if not items:
                continue

            section = {
                "section_title": group.get("group_title", ""),
                "items": [],
            }

            for item in items:
                item_id = item.get("item_id", "")
                answer = answers.get(item_id, {})
                passed = answer.get("passed")
                failed_channels = answer.get("failed_channels", [])
                notes = answer.get("notes", "") or ""
                question_type = item.get("question_type", "")

                if failed_channels:
                    failed_text = ", ".join(map(str, failed_channels))
                    if question_type == "yes_no_channels_text":
                        notes = f"ค่า pixel ที่ไม่ผ่าน: {failed_text}" if not notes else f"ค่า pixel ที่ไม่ผ่าน: {failed_text} | {notes}"
                    else:
                        notes = f"ช่องที่ไม่เห็น: {failed_text}" if not notes else f"ช่องที่ไม่เห็น: {failed_text} | {notes}"

                section["items"].append(
                    {
                        "title": item.get("title", ""),
                        "passed": passed,
                        "note": notes,
                    }
                )

            results.append(section)

        return results

    def _format_datetime(self, value: str):
        if not value:
            return "", ""

        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M:%S")
            except ValueError:
                continue

        return value, ""

    def _build_ui(self):
        FONT_TH = "TH Sarabun New"
        FONT_TITLE = (FONT_TH, 30, "bold")
        FONT_META = (FONT_TH, 20, "bold")
        FONT_HEADER = (FONT_TH, 20, "bold")
        FONT_SECTION = (FONT_TH, 19, "bold")
        FONT_ITEM = (FONT_TH, 17, "bold")
        FONT_RESULT = (FONT_TH, 17, "bold")
        FONT_NOTE = (FONT_TH, 16)
        FONT_BTN = (FONT_TH, 18, "bold")

        evaluation = self.evaluation or {}
        test_date, test_time = self._format_datetime(evaluation.get("eval_datetime", ""))
        display_label = DISPLAY_TYPE_LABELS.get(evaluation.get("screen_type", ""), evaluation.get("screen_type", ""))
        period_label = PERIOD_LABELS.get(evaluation.get("period", ""), evaluation.get("period", ""))

        card = ctk.CTkFrame(self.main_frame, corner_radius=16, fg_color=HISTORY_CARD_COLOR)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)
        card.grid_rowconfigure(3, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="ผลการประเมินคุณภาพหน้าจอ",
            font=FONT_TITLE,
            text_color=WHITE,
        ).grid(row=0, column=0, pady=(18, 10))

        meta_box = ctk.CTkFrame(card, corner_radius=18, fg_color=HEADER_BG)
        meta_box.grid(row=1, column=0, sticky="ew", padx=34, pady=(0, 14))
        for i in range(4):
            meta_box.grid_columnconfigure(i, weight=1)

        top_meta = (
            ("โรงพยาบาล", evaluation.get("hospital_name", "")),
            ("ผู้ประเมิน", evaluation.get("evaluator_name", "")),
        )
        bottom_meta = (
            ("ประเภทการประเมิน", f"{display_label} {period_label}".strip()),
            ("หมายเลขครุภัณฑ์", evaluation.get("screen_model", "")),
            ("วันที่", test_date),
            ("เวลา", test_time),
        )

        for idx, (label, value) in enumerate(top_meta):
            wrap = ctk.CTkFrame(meta_box, fg_color=TRANSPARENT)
            wrap.grid(row=0, column=idx, sticky="w", padx=24, pady=(14, 8))
            ctk.CTkLabel(wrap, text=label, font=FONT_META, text_color=WHITE).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(wrap, text=value, font=FONT_META, text_color=WHITE).pack(side="left")

        for idx, (label, value) in enumerate(bottom_meta):
            wrap = ctk.CTkFrame(meta_box, fg_color=TRANSPARENT)
            wrap.grid(row=1, column=idx, sticky="w", padx=24, pady=(0, 14))
            ctk.CTkLabel(wrap, text=label, font=FONT_META, text_color=WHITE).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(wrap, text=value, font=FONT_META, text_color=WHITE).pack(side="left")

        header = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        header.grid(row=2, column=0, sticky="ew", padx=34)
        header.grid_columnconfigure(0, weight=5)
        header.grid_columnconfigure(1, weight=2)
        header.grid_columnconfigure(2, weight=2)

        for ci, text in enumerate(["หัวข้อการประเมิน", "ผลการประเมิน", "หมายเหตุ"]):
            ctk.CTkLabel(
                header,
                text=text,
                font=FONT_HEADER,
                text_color=WHITE,
                anchor="center",
            ).grid(row=0, column=ci, sticky="ew", pady=(0, 8))

        ctk.CTkFrame(card, height=1, fg_color=HISTORY_LINE_COLOR).grid(row=3, column=0, sticky="new", padx=34)

        body = ctk.CTkScrollableFrame(
            card,
            fg_color=TRANSPARENT,
            scrollbar_button_color=HISTORY_BUTTON_GRAY,
            scrollbar_button_hover_color=HISTORY_BUTTON_GRAY_HOVER,
        )
        body.grid(row=3, column=0, sticky="nsew", padx=34, pady=(10, 8))
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=2)
        body.grid_columnconfigure(2, weight=2)
        body.grid_anchor("nw")

        r = 0
        if not self._has_answer_data:
            ctk.CTkLabel(
                body,
                text="รายการนี้ยังไม่มีข้อมูลผลรายข้อที่บันทึกไว้ในฐานข้อมูล",
                font=FONT_ITEM,
                text_color=HISTORY_TEXT_GRAY,
                anchor="w",
                justify="left",
            ).grid(row=r, column=0, columnspan=3, sticky="w", pady=(6, 12))
            r += 1

        for section in self.results:
            ctk.CTkLabel(
                body,
                text=section.get("section_title", ""),
                font=FONT_SECTION,
                text_color=SECTION_BLUE,
                anchor="w",
                wraplength=600,
                justify="left",
            ).grid(row=r, column=0, columnspan=3, sticky="w", pady=(10, 6))
            r += 1

            for item in section.get("items", []):
                passed = item.get("passed")
                if passed is True:
                    result_text = "✔ ผ่าน"
                    result_color = PASS_GREEN
                elif passed is False:
                    result_text = "✘ ไม่ผ่าน"
                    result_color = FAIL_RED
                else:
                    result_text = "-"
                    result_color = HISTORY_TEXT_GRAY[0]

                ctk.CTkLabel(
                    body,
                    text=item.get("title", ""),
                    font=FONT_ITEM,
                    text_color=WHITE,
                    anchor="w",
                    wraplength=620,
                    justify="left",
                ).grid(row=r, column=0, sticky="w", padx=(22, 8), pady=4)

                ctk.CTkLabel(
                    body,
                    text=result_text,
                    font=FONT_RESULT,
                    text_color=result_color,
                    anchor="w",
                ).grid(row=r, column=1, sticky="w", padx=8, pady=4)

                ctk.CTkLabel(
                    body,
                    text=item.get("note", ""),
                    font=FONT_NOTE,
                    text_color=WHITE,
                    anchor="w",
                    wraplength=260,
                    justify="left",
                ).grid(row=r, column=2, sticky="w", padx=8, pady=4)

                r += 1

        bottom = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        bottom.grid(row=4, column=0, sticky="ew", padx=34, pady=(8, 20))

        ctk.CTkButton(
            bottom,
            text="กลับไปยังหน้าประวัติการทดสอบ",
            font=FONT_BTN,
            width=260,
            height=46,
            corner_radius=23,
            fg_color=HISTORY_BUTTON_GRAY,
            hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE,
            command=self._on_back,
        ).pack(side="left")

        ctk.CTkButton(
            bottom,
            text="ส่งออก",
            font=FONT_BTN,
            width=180,
            height=46,
            corner_radius=23,
            fg_color=HISTORY_ACCENT,
            hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE,
            command=self._on_export,
        ).pack(side="right")

        ctk.CTkButton(
            bottom,
            text="เปรียบเทียบ Baseline",
            font=FONT_BTN,
            width=210,
            height=46,
            corner_radius=23,
            fg_color=HISTORY_ACCENT,
            hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE,
            command=self._on_baseline,
        ).pack(side="right", padx=(0, 12))

    def _on_back(self):
        if self.back_command:
            self.back_command()

    def _on_baseline(self):
        if not self.evaluation:
            return
        self._show_baseline_dialog()

    def _on_export(self):
        if self.export_command:
            self.export_command(self.evaluation, self.results)

    def _show_baseline_dialog(self):
        from database.database import get_evaluations_before

        self._close_baseline_dialog()
        current = self.evaluation or {}
        rows = get_evaluations_before(
            current.get("screen_type", ""),
            current.get("period", ""),
            current.get("id", 0),
        )

        dlg = ctk.CTkToplevel(self)
        self._baseline_dialog = dlg
        self._baseline_selected = None
        self._baseline_rows = []

        dlg.title("")
        dlg.attributes("-topmost", True)
        dlg.resizable(False, False)
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.configure(fg_color=HISTORY_CARD_COLOR)

        width, height = 1040, 720
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        dlg.geometry(f"{width}x{height}+{(sw-width)//2}+{(sh-height)//2}")

        FONT_TH = "TH Sarabun New"
        title_font = (FONT_TH, 28, "bold")
        header_font = (FONT_TH, 22, "bold")
        row_font = (FONT_TH, 20, "bold")
        btn_font = (FONT_TH, 20, "bold")

        dlg.grid_columnconfigure(0, weight=1)
        dlg.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            dlg,
            text="เลือกรอบที่ต้องการเทียบ Baseline",
            font=title_font,
            text_color=WHITE,
        ).grid(row=0, column=0, pady=(22, 18))

        list_card = ctk.CTkFrame(dlg, fg_color=HEADER_BG, corner_radius=18)
        list_card.grid(row=1, column=0, sticky="nsew", padx=68, pady=(0, 16))
        list_card.grid_rowconfigure(1, weight=1)
        list_card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(list_card, fg_color=TRANSPARENT)
        header.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 6))
        for idx, text in enumerate(["ครั้งที่", "วัน", "เวลา", "ชื่อ-นามสกุล"]):
            header.grid_columnconfigure(idx, weight=1)
            ctk.CTkLabel(
                header,
                text=text,
                font=header_font,
                text_color=WHITE,
            ).grid(row=0, column=idx, sticky="ew")

        ctk.CTkFrame(list_card, height=1, fg_color=HISTORY_LINE_COLOR).grid(
            row=1, column=0, sticky="new", padx=18
        )

        table = ctk.CTkFrame(list_card, fg_color=TRANSPARENT, corner_radius=16)
        table.grid(row=2, column=0, sticky="nsew", padx=14, pady=(8, 14))
        table.grid_rowconfigure(0, weight=1)
        table.grid_columnconfigure(0, weight=1)

        scroller = ctk.CTkScrollableFrame(
            table,
            fg_color=TRANSPARENT,
            scrollbar_button_color=HISTORY_BUTTON_GRAY,
            scrollbar_button_hover_color=HISTORY_BUTTON_GRAY_HOVER,
        )
        scroller.grid(row=0, column=0, sticky="nsew", padx=16, pady=14)
        scroller.grid_columnconfigure(0, weight=1)
        scroller.grid_anchor("nw")

        if not rows:
            ctk.CTkLabel(
                scroller,
                text="ยังไม่มีประวัติการทดสอบก่อนหน้าสำหรับใช้เทียบ Baseline",
                font=row_font,
                text_color=HISTORY_TEXT_GRAY,
            ).grid(row=0, column=0, sticky="w", padx=18, pady=18)
        else:
            for idx, row in enumerate(rows):
                date_text, time_text = self._format_datetime(row.get("eval_datetime", ""))
                item = ctk.CTkFrame(
                    scroller,
                    fg_color=TRANSPARENT,
                    corner_radius=14,
                    border_width=0,
                )
                item.grid(row=idx * 2, column=0, sticky="ew", pady=(0, 8))
                item.grid_columnconfigure(0, weight=1)
                item.grid_columnconfigure(1, weight=1)
                item.grid_columnconfigure(2, weight=1)
                item.grid_columnconfigure(3, weight=1)
                item.configure(cursor="hand2")

                values = [
                    f"ครั้งที่ {row.get('rank', '-')}",
                    date_text or "-",
                    time_text or "-",
                    row.get("evaluator_name", "-"),
                ]
                labels = []
                for col, text in enumerate(values):
                    lbl = ctk.CTkLabel(
                        item,
                        text=text,
                        font=row_font,
                        text_color=WHITE,
                        anchor="center",
                        cursor="hand2",
                    )
                    lbl.grid(row=0, column=col, sticky="ew", padx=10, pady=12)
                    labels.append(lbl)

                divider = ctk.CTkFrame(item, height=1, fg_color=HISTORY_LINE_COLOR)
                divider.grid(row=1, column=0, columnspan=4, sticky="ew", padx=18, pady=(0, 2))

                self._baseline_rows.append((item, labels, row, divider))
                for widget in [item, *labels, divider]:
                    widget.bind("<Button-1>", lambda _e, rec=row: self._select_baseline_row(rec))
                    widget.bind("<Double-Button-1>", lambda _e, rec=row: self._confirm_baseline(rec))
                    widget.bind("<Enter>", lambda _e, rec=row: self._hover_baseline_row(rec, True))
                    widget.bind("<Leave>", lambda _e, rec=row: self._hover_baseline_row(rec, False))

        btns = ctk.CTkFrame(dlg, fg_color=TRANSPARENT)
        btns.grid(row=3, column=0, sticky="e", padx=68, pady=(0, 18))

        ctk.CTkButton(
            btns,
            text="ยกเลิก",
            font=btn_font,
            width=190,
            height=46,
            corner_radius=23,
            fg_color=HISTORY_BUTTON_GRAY,
            hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE,
            command=self._close_baseline_dialog,
        ).pack(side="left", padx=(0, 12))

        confirm_btn = ctk.CTkButton(
            btns,
            text="ยืนยัน",
            font=btn_font,
            width=190,
            height=46,
            corner_radius=23,
            fg_color=HISTORY_ACCENT,
            hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE,
            state="disabled" if not rows else "normal",
            command=self._confirm_baseline,
        )
        confirm_btn.pack(side="left")
        self._baseline_confirm_btn = confirm_btn

        dlg.protocol("WM_DELETE_WINDOW", self._close_baseline_dialog)

    def _select_baseline_row(self, record):
        self._baseline_selected = record
        for frame, labels, row, divider in self._baseline_rows:
            is_selected = row.get("id") == record.get("id")
            fg = HISTORY_ROW_SELECTED if is_selected else TRANSPARENT
            frame.configure(fg_color=fg)
            divider.configure(fg_color=TRANSPARENT if is_selected else HISTORY_LINE_COLOR)
            for label in labels:
                label.configure(text_color=WHITE)
        if hasattr(self, "_baseline_confirm_btn"):
            self._baseline_confirm_btn.configure(state="normal")

    def _hover_baseline_row(self, record, is_hover):
        for frame, labels, row, divider in self._baseline_rows:
            is_selected = self._baseline_selected and row.get("id") == self._baseline_selected.get("id")
            if row.get("id") != record.get("id") or is_selected:
                continue
            frame.configure(fg_color=HISTORY_ROW_HOVER if is_hover else TRANSPARENT)
            divider.configure(fg_color=HISTORY_LINE_COLOR)
            for label in labels:
                label.configure(text_color=WHITE)

    def _confirm_baseline(self, record=None):
        selected = record or self._baseline_selected
        if not selected or not self.baseline_command:
            return
        self._close_baseline_dialog()
        self.baseline_command(self.evaluation, selected)

    def _close_baseline_dialog(self):
        if self._baseline_dialog and self._baseline_dialog.winfo_exists():
            self._baseline_dialog.grab_release()
            self._baseline_dialog.destroy()
        self._baseline_dialog = None
        self._baseline_selected = None
        self._baseline_rows = []
