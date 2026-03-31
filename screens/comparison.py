import customtkinter as ctk
from datetime import datetime

from constants.evaluation_questions import TEST_CONFIG
from styles.base_colors import (
    HISTORY_ACCENT,
    HISTORY_ACCENT_HOVER,
    HISTORY_BUTTON_GRAY,
    HISTORY_BUTTON_GRAY_HOVER,
    HISTORY_CARD_COLOR,
    HISTORY_LINE_COLOR,
    HISTORY_TEXT_GRAY,
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

HEADER_BG = ("#5B5E64", "#5B5E64")
SECTION_BLUE = "#79A7FF"


class ComparisonScreen(ctk.CTkFrame):
    def __init__(self, master, back_command=None, export_command=None, **kwargs):
        kwargs.setdefault("fg_color", TRANSPARENT)
        super().__init__(master, **kwargs)

        self.back_command = back_command
        self.export_command = export_command

        self.current_evaluation = None
        self.baseline_evaluation = None
        self.rows_data = []

        self._ui_built = False
        self._meta_value_labels = {}
        self._body = None
        self._empty_label = None
        self._table_entries = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self._build_ui()

    def on_show(self, current_evaluation=None, baseline_evaluation=None, **kwargs):
        if current_evaluation is not None:
            self.current_evaluation = current_evaluation
        if baseline_evaluation is not None:
            self.baseline_evaluation = baseline_evaluation

        self.rows_data = self._build_rows()
        self._build_ui()
        self._update_view()

    def _build_rows(self):
        current = self.current_evaluation or {}
        baseline = self.baseline_evaluation or {}
        dtype = current.get("screen_type") or baseline.get("screen_type", "")
        period = current.get("period") or baseline.get("period", "")
        groups = TEST_CONFIG.get(dtype, {}).get(period, [])
        cur_answers = current.get("answers", {})
        base_answers = baseline.get("answers", {})

        rows = []
        for group in groups:
            items = group.get("items", [])
            if not items:
                continue

            section = {"section_title": group.get("group_title", ""), "items": []}
            for item in items:
                item_id = item.get("item_id", "")
                base_answer = base_answers.get(item_id)
                current_answer = cur_answers.get(item_id)
                compare_text, description = _compare_result(item, base_answer, current_answer)
                section["items"].append(
                    {
                        "title": item.get("title", ""),
                        "baseline_text": _answer_text(base_answer),
                        "current_text": _answer_text(current_answer),
                        "compare_text": compare_text,
                        "description": description,
                    }
                )

            rows.append(section)

        return rows

    def _build_ui(self):
        if self._ui_built:
            return

        FONT_TH = "TH Sarabun New"
        FONT_TITLE = (FONT_TH, 30, "bold")
        FONT_META = (FONT_TH, 20, "bold")
        FONT_HEADER = (FONT_TH, 20, "bold")
        FONT_SECTION = (FONT_TH, 19, "bold")
        FONT_ITEM = (FONT_TH, 17, "bold")
        FONT_CELL = (FONT_TH, 17, "bold")
        FONT_DESC = (FONT_TH, 16)
        FONT_BTN = (FONT_TH, 18, "bold")

        card = ctk.CTkFrame(self.main_frame, corner_radius=16, fg_color=HISTORY_CARD_COLOR)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)
        card.grid_rowconfigure(3, weight=1)
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        top.grid(row=0, column=0, sticky="ew", padx=28, pady=(18, 10))

        ctk.CTkButton(
            top,
            text="↩",
            font=(FONT_TH, 20, "bold"),
            width=52,
            height=38,
            corner_radius=19,
            fg_color=HISTORY_BUTTON_GRAY,
            hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE,
            command=self._on_back,
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text="เปรียบเทียบกับ Baseline",
            font=FONT_TITLE,
            text_color=WHITE,
        ).pack(side="left", expand=True)

        meta_box = ctk.CTkFrame(card, corner_radius=18, fg_color=HEADER_BG)
        meta_box.grid(row=1, column=0, sticky="ew", padx=34, pady=(0, 14))

        baseline_lbl = ctk.CTkLabel(
            meta_box,
            text="",
            font=FONT_META,
            text_color=WHITE,
            anchor="w",
            justify="left",
        )
        baseline_lbl.grid(row=0, column=0, sticky="w", padx=24, pady=(14, 6))
        self._meta_value_labels["baseline"] = baseline_lbl

        current_lbl = ctk.CTkLabel(
            meta_box,
            text="",
            font=FONT_META,
            text_color=WHITE,
            anchor="w",
            justify="left",
        )
        current_lbl.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 14))
        self._meta_value_labels["current"] = current_lbl

        header = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        header.grid(row=2, column=0, sticky="ew", padx=34)
        header.grid_columnconfigure(0, weight=4)
        header.grid_columnconfigure(1, weight=2)
        header.grid_columnconfigure(2, weight=2)
        header.grid_columnconfigure(3, weight=4)
        header.grid_columnconfigure(4, weight=4)

        for idx, text in enumerate([
            "หัวข้อประเมิน",
            "Baseline",
            "ครั้งนี้",
            "ผลการเปรียบเทียบ",
            "คำอธิบายเพิ่มเติมจากการเปรียบเทียบ",
        ]):
            ctk.CTkLabel(
                header,
                text=text,
                font=FONT_HEADER,
                text_color=WHITE,
                anchor="center" if idx else "w",
                justify="center",
            ).grid(row=0, column=idx, sticky="ew", pady=(0, 8))

        ctk.CTkFrame(card, height=1, fg_color=HISTORY_LINE_COLOR).grid(row=3, column=0, sticky="new", padx=34)

        body = ctk.CTkScrollableFrame(
            card,
            fg_color=TRANSPARENT,
            scrollbar_button_color=HISTORY_BUTTON_GRAY,
            scrollbar_button_hover_color=HISTORY_BUTTON_GRAY_HOVER,
        )
        body.grid(row=3, column=0, sticky="nsew", padx=34, pady=(10, 8))
        body.grid_columnconfigure(0, weight=4)
        body.grid_columnconfigure(1, weight=2)
        body.grid_columnconfigure(2, weight=2)
        body.grid_columnconfigure(3, weight=4)
        body.grid_columnconfigure(4, weight=4)
        body.grid_anchor("nw")
        self._body = body

        self._empty_label = ctk.CTkLabel(
            body,
            text="ยังไม่มีข้อมูลสำหรับเปรียบเทียบ Baseline",
            font=FONT_ITEM,
            text_color=HISTORY_TEXT_GRAY,
            anchor="w",
        )
        self._empty_label.grid(row=0, column=0, columnspan=5, sticky="w", pady=(6, 12))
        self._empty_label.grid_remove()

        bottom = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        bottom.grid(row=4, column=0, sticky="ew", padx=34, pady=(8, 20))

        ctk.CTkButton(
            bottom,
            text="กลับ",
            font=FONT_BTN,
            width=180,
            height=46,
            corner_radius=23,
            fg_color=HISTORY_BUTTON_GRAY,
            hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE,
            command=self._on_back,
        ).pack(side="left")

        ctk.CTkButton(
            bottom,
            text="ส่งออก PDF",
            font=FONT_BTN,
            width=190,
            height=46,
            corner_radius=23,
            fg_color=HISTORY_ACCENT,
            hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE,
            command=self._on_export,
        ).pack(side="right")

        self._ui_built = True

    def _flatten_rows(self):
        entries = []
        for section in self.rows_data or []:
            entries.append(("section", {"title": section.get("section_title", "")}))
            for item in section.get("items", []) or []:
                entries.append(("item", item))
        return entries

    def _ensure_table_entry(self, kind: str, idx: int):
        if self._body is None:
            return None

        while len(self._table_entries) <= idx:
            self._table_entries.append(None)

        current = self._table_entries[idx]
        if current is not None and current.get("kind") == kind:
            return current

        if current:
            for widget in current.get("widgets", []):
                widget.destroy()

        FONT_TH = "TH Sarabun New"
        FONT_SECTION = (FONT_TH, 19, "bold")
        FONT_ITEM = (FONT_TH, 17, "bold")
        FONT_CELL = (FONT_TH, 17, "bold")
        FONT_DESC = (FONT_TH, 16)

        widgets = []
        if kind == "section":
            title_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=FONT_SECTION,
                text_color=SECTION_BLUE,
                anchor="w",
                wraplength=820,
                justify="left",
            )
            widgets = [title_lbl]
            entry = {"kind": kind, "title": title_lbl, "widgets": widgets}
        else:
            title_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=FONT_ITEM,
                text_color=WHITE,
                anchor="w",
                wraplength=320,
                justify="left",
            )
            baseline_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=FONT_CELL,
                text_color=WHITE,
                anchor="w",
                wraplength=160,
                justify="left",
            )
            current_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=FONT_CELL,
                text_color=WHITE,
                anchor="w",
                wraplength=160,
                justify="left",
            )
            compare_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=FONT_CELL,
                text_color=WHITE,
                anchor="w",
                wraplength=260,
                justify="left",
            )
            desc_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=FONT_DESC,
                text_color=WHITE,
                anchor="w",
                wraplength=320,
                justify="left",
            )
            widgets = [title_lbl, baseline_lbl, current_lbl, compare_lbl, desc_lbl]
            entry = {
                "kind": kind,
                "title": title_lbl,
                "baseline": baseline_lbl,
                "current": current_lbl,
                "compare": compare_lbl,
                "description": desc_lbl,
                "widgets": widgets,
            }

        self._table_entries[idx] = entry
        return entry

    def _update_view(self):
        if not self._ui_built:
            return

        self._meta_value_labels["baseline"].configure(
            text=self._compose_meta_line(self.baseline_evaluation, prefix="Baseline")
        )
        self._meta_value_labels["current"].configure(
            text=self._compose_meta_line(self.current_evaluation, prefix="ครั้งนี้")
        )

        entries = self._flatten_rows()
        if not entries:
            if self._empty_label:
                self._empty_label.grid()
            for entry in self._table_entries:
                if not entry:
                    continue
                for widget in entry.get("widgets", []):
                    widget.grid_remove()
            if self._body is not None:
                self.after(0, lambda: self._body._parent_canvas.yview_moveto(0))
            return

        if self._empty_label:
            self._empty_label.grid_remove()

        for i, (kind, payload) in enumerate(entries):
            entry = self._ensure_table_entry(kind, i)
            if not entry:
                continue

            if kind == "section":
                entry["title"].configure(text=payload.get("title", ""))
                entry["title"].grid(row=i, column=0, columnspan=5, sticky="w", pady=(8, 6))
            else:
                entry["title"].configure(text=payload.get("title", ""))
                entry["baseline"].configure(text=payload.get("baseline_text", "-"))
                entry["current"].configure(text=payload.get("current_text", "-"))
                entry["compare"].configure(text=payload.get("compare_text", "-"))
                entry["description"].configure(text=payload.get("description", "-"))

                entry["title"].grid(row=i, column=0, sticky="nw", padx=(0, 10), pady=4)
                entry["baseline"].grid(row=i, column=1, sticky="nw", padx=8, pady=4)
                entry["current"].grid(row=i, column=2, sticky="nw", padx=8, pady=4)
                entry["compare"].grid(row=i, column=3, sticky="nw", padx=8, pady=4)
                entry["description"].grid(row=i, column=4, sticky="nw", padx=8, pady=4)

        for j in range(len(entries), len(self._table_entries)):
            entry = self._table_entries[j]
            if not entry:
                continue
            for widget in entry.get("widgets", []):
                widget.grid_remove()

        if self._body is not None:
            self.after(0, lambda: self._body._parent_canvas.yview_moveto(0))

    def _compose_meta_line(self, evaluation, prefix):
        if not evaluation:
            return f"{prefix}: -"

        date_text, time_text = self._format_datetime(evaluation.get("eval_datetime", ""))
        rank = self._get_eval_rank(evaluation)
        hospital = evaluation.get("hospital_name", "")
        evaluator = evaluation.get("evaluator_name", "")
        return (
            f"{prefix} (ครั้งที่ {rank}):   โรงพยาบาล{hospital}   "
            f"ผู้ประเมิน {evaluator}   {date_text}   {time_text}"
        ).strip()

    def _get_eval_rank(self, evaluation):
        from database.database import get_eval_rank

        eval_id = evaluation.get("id")
        if not eval_id:
            return "-"
        return get_eval_rank(
            evaluation.get("screen_type", ""),
            evaluation.get("period", ""),
            eval_id,
        )

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

    def _on_back(self):
        if self.back_command:
            self.back_command(self.current_evaluation)

    def _on_export(self):
        if self.export_command:
            self.export_command(self.current_evaluation, self.baseline_evaluation, self.rows_data)


def _answer_text(answer):
    if answer is None:
        return "ไม่มีข้อมูล"
    if answer.get("passed"):
        return "ผ่าน"

    failed_channels = answer.get("failed_channels", [])
    if failed_channels:
        if all(str(ch).isdigit() and len(str(ch)) == 3 for ch in failed_channels):
            return f"ไม่ผ่าน ({len(failed_channels)} ค่า)"
        return f"ไม่ผ่าน ({len(failed_channels)} ช่อง)"
    return "ไม่ผ่าน"


def _compare_result(item, baseline_answer, current_answer):
    if baseline_answer is None or current_answer is None:
        return "ไม่มีข้อมูล", "-"

    base_pass = baseline_answer.get("passed")
    current_pass = current_answer.get("passed")
    question_type = item.get("question_type", "yes_no")
    drift = item.get("cmp_drift", "A")

    if base_pass and current_pass:
        return (
            "คุณภาพของหน้าจอเท่าเดิม",
            "ผลที่ได้จากการทดสอบ ครั้งนี้ และผลที่ได้จาก baseline ผ่านเกณฑ์ทั้งคู่",
        )

    if base_pass and not current_pass:
        return (
            "คุณภาพของหน้าจอลดลง",
            "ผลที่ได้จากการทดสอบ ครั้งนี้ ไม่ผ่านเกณฑ์และผลที่ได้จาก baseline ผ่านเกณฑ์",
        )

    if not base_pass and current_pass:
        if drift == "A":
            compare_text = "ผลการทดสอบคลาดเคลื่อนอาจเกิดจากการเปลี่ยนผู้ประเมินและปัจจัยที่เกี่ยวข้องอื่น ๆ"
        else:
            compare_text = "ผลการทดสอบคลาดเคลื่อนเนื่องมาจากมีการเปลี่ยนผู้ประเมินและปัจจัยที่เกี่ยวข้องอื่น ๆ"
        return (
            compare_text,
            "ผลที่ได้จากการทดสอบ ครั้งนี้ ผ่านเกณฑ์และผลที่ได้จาก baseline ไม่ผ่านเกณฑ์",
        )

    if question_type == "yes_no":
        return "ผลการประเมินไม่ผ่านทั้งคู่", "-"

    base_count = len(baseline_answer.get("failed_channels", []))
    current_count = len(current_answer.get("failed_channels", []))
    base_desc = "ผลที่ได้จากการทดสอบ ครั้งนี้ และผลที่ได้จาก baseline ไม่ผ่านเกณฑ์"

    if question_type == "yes_no_channels_text":
        if current_count > base_count:
            return (
                "คุณภาพของหน้าจอลดลง",
                f"{base_desc} แต่พบว่าจำนวนภาพที่มองเห็นไม่สม่ำเสมอในครั้งนี้มากกว่า baseline",
            )
        if current_count == base_count:
            return (
                "คุณภาพของหน้าจอเท่าเดิม",
                f"{base_desc} แต่พบว่าจำนวนภาพที่มองเห็นได้ไม่สม่ำเสมอมีจำนวนเท่ากัน",
            )
        if drift == "A":
            compare_text = "ผลการทดสอบคลาดเคลื่อนอาจเกิดจากการเปลี่ยนผู้ประเมินและปัจจัยที่เกี่ยวข้องอื่น ๆ"
        else:
            compare_text = "ผลการทดสอบคลาดเคลื่อนเนื่องมาจากมีการเปลี่ยนผู้ประเมินและปัจจัยที่เกี่ยวข้องอื่น ๆ"
        return (
            compare_text,
            f"{base_desc} แต่พบว่าจำนวนภาพที่มองเห็นไม่สม่ำเสมอในครั้งนี้น้อยกว่า baseline",
        )

    if current_count > base_count:
        return (
            "คุณภาพของหน้าจอลดลง",
            f"{base_desc} แต่พบว่าจำนวนกลุ่มเส้นคู่ที่มองเห็นในครั้งนี้น้อยกว่า baseline",
        )
    if current_count == base_count:
        return (
            "คุณภาพของหน้าจอเท่าเดิม",
            f"{base_desc} แต่พบว่าจำนวนกลุ่มเส้นคู่ที่มองเห็นมีจำนวนเท่ากัน",
        )
    if drift == "A":
        compare_text = "ผลการทดสอบคลาดเคลื่อนอาจเกิดจากการเปลี่ยนผู้ประเมินและปัจจัยที่เกี่ยวข้องอื่น ๆ"
    else:
        compare_text = "ผลการทดสอบคลาดเคลื่อนเนื่องมาจากมีการเปลี่ยนผู้ประเมินและปัจจัยที่เกี่ยวข้องอื่น ๆ"
    return (
        compare_text,
        f"{base_desc} แต่พบว่าจำนวนกลุ่มเส้นคู่ที่มองเห็นในครั้งนี้มากกว่า baseline",
    )
