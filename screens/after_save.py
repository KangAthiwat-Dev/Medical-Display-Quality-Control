import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from styles.base_colors import (
    HISTORY_ACCENT,
    HISTORY_ACCENT_HOVER,
    HISTORY_BUTTON_GRAY,
    HISTORY_BUTTON_GRAY_HOVER,
    HISTORY_CARD_COLOR,
    HISTORY_LINE_COLOR,
    HISTORY_ROW_HOVER,
    HISTORY_ROW_SELECTED,
    TRANSPARENT,
    WHITE,
)


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

BASELINE_FIRST_MESSAGE = (
    "เนื่องจากเป็นการทำการทดสอบครั้งที่ 1 จึงจะนำผลการทดสอบครั้งนี้เป็นค่าพื้นฐานที่วัดได้ในครั้งแรก "
    "(Baseline) ซึ่งจะนำไปใช้ในการเปรียบเทียบผลในครั้งต่อ ๆ ไป"
)


class AfterSaveScreen(ctk.CTkFrame):
    def __init__(self, master, home_command=None, **kwargs):
        kwargs.setdefault("fg_color", TRANSPARENT)
        super().__init__(master, **kwargs)

        self.home_command = home_command
        self.saved_payload = None
        self.evaluation = None

        self._ui_built = False
        self._info_value_labels = {}
        self._title_label = None
        self._subtitle_label = None

        self._baseline_dialog = None
        self._baseline_current_evaluation = None
        self._baseline_selected = None
        self._baseline_rows = []
        self._baseline_table = None
        self._baseline_confirm_btn = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self._build_ui()

    def on_show(self, saved_payload=None, **kwargs):
        if saved_payload is not None:
            self.saved_payload = saved_payload
            self.evaluation = saved_payload.get("evaluation")

        self._build_ui()
        self._update_view()

    def _build_ui(self):
        if self._ui_built:
            return

        FONT_TH = "TH Sarabun New"
        FONT_TITLE = (FONT_TH, 28, "bold")
        FONT_SUB = (FONT_TH, 22, "bold")
        FONT_LABEL = (FONT_TH, 22, "bold")
        FONT_VALUE = (FONT_TH, 22, "bold")
        FONT_BTN = (FONT_TH, 20, "bold")

        card = ctk.CTkFrame(self.main_frame, corner_radius=16, fg_color=HISTORY_CARD_COLOR)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)
        card.grid_columnconfigure(0, weight=1)

        self._title_label = ctk.CTkLabel(
            card,
            text="",
            font=FONT_TITLE,
            text_color=WHITE,
        )
        self._title_label.grid(row=0, column=0, pady=(18, 10))

        ctk.CTkFrame(card, height=1, fg_color=HISTORY_LINE_COLOR).grid(
            row=1, column=0, sticky="ew", padx=90, pady=(0, 18)
        )

        self._subtitle_label = ctk.CTkLabel(
            card,
            text="",
            font=FONT_SUB,
            text_color=WHITE,
        )
        self._subtitle_label.grid(row=2, column=0, pady=(0, 18))

        info = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        info.grid(row=3, column=0, padx=180, sticky="ew")
        info.grid_columnconfigure(0, weight=1)
        info.grid_columnconfigure(1, weight=1)

        pairs = [
            ("โรงพยาบาล", "hospital_name"),
            ("ผู้ประเมิน", "evaluator_name"),
            ("หมายเลขครุภัณฑ์", "screen_model"),
            ("วันที่และเวลาในการทดสอบ", "datetime"),
        ]

        for idx, (label, key) in enumerate(pairs):
            ctk.CTkLabel(info, text=label, font=FONT_LABEL, text_color=WHITE, anchor="w").grid(
                row=idx, column=0, sticky="w", pady=16
            )
            value_lbl = ctk.CTkLabel(info, text="", font=FONT_VALUE, text_color=WHITE, anchor="w")
            value_lbl.grid(row=idx, column=1, sticky="w", pady=16)
            self._info_value_labels[key] = value_lbl

        bottom = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        bottom.grid(row=4, column=0, sticky="ew", padx=28, pady=(120, 24))

        ctk.CTkButton(
            bottom,
            text="กลับหน้าหลัก",
            font=FONT_BTN,
            width=200,
            height=48,
            corner_radius=24,
            fg_color=HISTORY_BUTTON_GRAY,
            hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE,
            command=self._go_home,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            bottom,
            text="เกณฑ์และวิธีการแก้ไขปัญหา",
            font=FONT_BTN,
            width=280,
            height=48,
            corner_radius=24,
            fg_color=HISTORY_BUTTON_GRAY,
            hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE,
            command=self._open_criteria,
        ).pack(side="left")

        ctk.CTkButton(
            bottom,
            text="ทำการเปรียบเทียบกับ base line",
            font=FONT_BTN,
            width=300,
            height=48,
            corner_radius=24,
            fg_color=HISTORY_ACCENT,
            hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE,
            command=self._compare,
        ).pack(side="right")

        self._ui_built = True

    def _update_view(self):
        payload = self.saved_payload or {}
        evaluation = self.evaluation or {}
        rank = payload.get("rank", "-")
        date_text, time_text = self._format_datetime(evaluation.get("eval_datetime", ""))
        display_label = DISPLAY_TYPE_LABELS.get(evaluation.get("screen_type", ""), evaluation.get("screen_type", ""))
        period_label = PERIOD_LABELS.get(evaluation.get("period", ""), evaluation.get("period", ""))

        if self._title_label is not None:
            self._title_label.configure(text=f"บันทึกข้อมูลการทดสอบครั้งที่ {rank} สำเร็จ")
        if self._subtitle_label is not None:
            self._subtitle_label.configure(text=f"{display_label} {period_label}".strip())

        values = {
            "hospital_name": evaluation.get("hospital_name", ""),
            "evaluator_name": evaluation.get("evaluator_name", ""),
            "screen_model": evaluation.get("screen_model", ""),
            "datetime": f"{date_text}      {time_text}".strip(),
        }
        for key, lbl in self._info_value_labels.items():
            lbl.configure(text=values.get(key, ""))

    def _open_criteria(self):
        evaluation = self.evaluation or {}
        self.master.show_screen(
            "criteria",
            bypass_auth=True,
            display_type=evaluation.get("screen_type", ""),
            period=evaluation.get("period", ""),
        )

    def _compare(self):
        payload = self.saved_payload or {}
        if payload.get("is_first"):
            messagebox.showinfo("Baseline", BASELINE_FIRST_MESSAGE)
            return

        if not self.evaluation:
            return
        self._show_baseline_picker_dialog(self.evaluation)

    def _ensure_baseline_dialog(self):
        if self._baseline_dialog is not None and self._baseline_dialog.winfo_exists():
            return

        FONT_TH = "TH Sarabun New"
        title_font = (FONT_TH, 28, "bold")
        header_font = (FONT_TH, 22, "bold")
        btn_font = (FONT_TH, 20, "bold")

        dlg = ctk.CTkToplevel(self)
        self._baseline_dialog = dlg
        dlg.title("")
        dlg.resizable(False, False)
        dlg.transient(self.winfo_toplevel())
        dlg.configure(fg_color=HISTORY_CARD_COLOR)
        dlg.protocol("WM_DELETE_WINDOW", self._close_baseline_dialog)

        width, height = 1040, 720
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        dlg.geometry(f"{width}x{height}+{(sw-width)//2}+{(sh-height)//2}")

        dlg.grid_columnconfigure(0, weight=1)
        dlg.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            dlg,
            text="เลือกรอบที่ต้องการเทียบ Baseline",
            font=title_font,
            text_color=WHITE,
        ).grid(row=0, column=0, pady=(22, 18))

        list_card = ctk.CTkFrame(dlg, fg_color=("#5B5E64", "#5B5E64"), corner_radius=18)
        list_card.grid(row=1, column=0, sticky="nsew", padx=68, pady=(0, 16))
        list_card.grid_rowconfigure(2, weight=1)
        list_card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(list_card, fg_color=TRANSPARENT)
        header.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 6))
        for idx, text in enumerate(["ครั้งที่", "วัน", "เวลา", "ชื่อ-นามสกุล"]):
            header.grid_columnconfigure(idx, weight=1)
            ctk.CTkLabel(header, text=text, font=header_font, text_color=WHITE).grid(
                row=0, column=idx, sticky="ew"
            )

        ctk.CTkFrame(list_card, height=1, fg_color=HISTORY_LINE_COLOR).grid(
            row=1, column=0, sticky="new", padx=18
        )

        table = ctk.CTkScrollableFrame(
            list_card,
            fg_color=TRANSPARENT,
            scrollbar_button_color=HISTORY_BUTTON_GRAY,
            scrollbar_button_hover_color=HISTORY_BUTTON_GRAY_HOVER,
        )
        table.grid(row=2, column=0, sticky="nsew", padx=14, pady=(8, 14))
        table.grid_columnconfigure(0, weight=1)
        table.grid_anchor("nw")
        self._baseline_table = table

        btns = ctk.CTkFrame(dlg, fg_color=TRANSPARENT)
        btns.grid(row=2, column=0, sticky="e", padx=68, pady=(0, 18))

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

        self._baseline_confirm_btn = ctk.CTkButton(
            btns,
            text="ยืนยัน",
            font=btn_font,
            width=190,
            height=46,
            corner_radius=23,
            fg_color=HISTORY_ACCENT,
            hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE,
            state="disabled",
            command=lambda: self._confirm_baseline_selection(self._baseline_current_evaluation),
        )
        self._baseline_confirm_btn.pack(side="left")

    def _ensure_baseline_row_entry(self, idx: int):
        while len(self._baseline_rows) <= idx:
            item = ctk.CTkFrame(self._baseline_table, fg_color=TRANSPARENT, corner_radius=14, border_width=0)
            item.grid_columnconfigure(0, weight=1)
            item.grid_columnconfigure(1, weight=1)
            item.grid_columnconfigure(2, weight=1)
            item.grid_columnconfigure(3, weight=1)
            item.configure(cursor="hand2")

            labels = []
            for col in range(4):
                lbl = ctk.CTkLabel(
                    item,
                    text="",
                    font=("TH Sarabun New", 20, "bold"),
                    text_color=WHITE,
                    anchor="center",
                    cursor="hand2",
                )
                lbl.grid(row=0, column=col, sticky="ew", padx=10, pady=12)
                labels.append(lbl)

            divider = ctk.CTkFrame(item, height=1, fg_color=HISTORY_LINE_COLOR)
            divider.grid(row=1, column=0, columnspan=4, sticky="ew", padx=18, pady=(0, 2))

            self._baseline_rows.append({
                "item": item,
                "labels": labels,
                "divider": divider,
                "record": None,
            })

    def _show_baseline_picker_dialog(self, current_evaluation):
        from database.database import get_evaluations_before

        rows = get_evaluations_before(
            current_evaluation.get("screen_type", ""),
            current_evaluation.get("period", ""),
            current_evaluation.get("id", 0),
        )

        self._baseline_current_evaluation = current_evaluation
        self._baseline_selected = None
        self._ensure_baseline_dialog()

        dlg = self._baseline_dialog
        if dlg is None:
            return

        width, height = 1040, 720
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        dlg.geometry(f"{width}x{height}+{(sw-width)//2}+{(sh-height)//2}")
        dlg.attributes("-topmost", True)
        dlg.deiconify()
        dlg.lift()
        dlg.focus_force()
        dlg.grab_set()

        for idx, row in enumerate(rows):
            self._ensure_baseline_row_entry(idx)
            entry = self._baseline_rows[idx]
            date_text, time_text = self._format_datetime(row.get("eval_datetime", ""))
            values = [
                f"ครั้งที่ {row.get('rank', '-')}",
                date_text or "-",
                time_text or "-",
                row.get("evaluator_name", "-"),
            ]

            entry["record"] = row
            entry["item"].configure(fg_color=TRANSPARENT)
            entry["divider"].configure(fg_color=HISTORY_LINE_COLOR)
            entry["item"].grid(row=idx * 2, column=0, sticky="ew", pady=(0, 8))
            for col, text in enumerate(values):
                entry["labels"][col].configure(text=text, text_color=WHITE)

            widgets = [entry["item"], *entry["labels"], entry["divider"]]
            for widget in widgets:
                widget.bind("<Button-1>", lambda _e, rec=row: self._select_baseline_row(rec))
                widget.bind(
                    "<Double-Button-1>",
                    lambda _e, rec=row: self._confirm_baseline_selection(current_evaluation, rec),
                )
                widget.bind("<Enter>", lambda _e, rec=row: self._hover_baseline_row(rec, True))
                widget.bind("<Leave>", lambda _e, rec=row: self._hover_baseline_row(rec, False))

        for idx in range(len(rows), len(self._baseline_rows)):
            entry = self._baseline_rows[idx]
            entry["record"] = None
            entry["item"].grid_remove()

        if self._baseline_confirm_btn is not None:
            self._baseline_confirm_btn.configure(state="disabled" if not rows else "disabled")

    def _select_baseline_row(self, record):
        self._baseline_selected = record
        for entry in self._baseline_rows:
            row = entry.get("record")
            if not row:
                continue
            is_selected = row.get("id") == record.get("id")
            entry["item"].configure(fg_color=HISTORY_ROW_SELECTED if is_selected else TRANSPARENT)
            entry["divider"].configure(fg_color=TRANSPARENT if is_selected else HISTORY_LINE_COLOR)
            for label in entry["labels"]:
                label.configure(text_color=WHITE)
        if self._baseline_confirm_btn is not None:
            self._baseline_confirm_btn.configure(state="normal")

    def _hover_baseline_row(self, record, is_hover):
        for entry in self._baseline_rows:
            row = entry.get("record")
            if not row:
                continue
            is_selected = self._baseline_selected and row.get("id") == self._baseline_selected.get("id")
            if row.get("id") != record.get("id") or is_selected:
                continue
            entry["item"].configure(fg_color=HISTORY_ROW_HOVER if is_hover else TRANSPARENT)
            entry["divider"].configure(fg_color=HISTORY_LINE_COLOR)
            for label in entry["labels"]:
                label.configure(text_color=WHITE)

    def _confirm_baseline_selection(self, current_evaluation, record=None):
        selected = record or self._baseline_selected
        if not selected:
            return
        self._close_baseline_dialog()
        self.master.handle_open_baseline_comparison(current_evaluation, selected)

    def _go_home(self):
        if self.home_command:
            self.home_command()

    def _close_baseline_dialog(self):
        if self._baseline_dialog and self._baseline_dialog.winfo_exists():
            try:
                self._baseline_dialog.grab_release()
            except Exception:
                pass
            self._baseline_dialog.withdraw()
        self._baseline_selected = None
        if self._baseline_confirm_btn is not None:
            self._baseline_confirm_btn.configure(state="disabled")

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
