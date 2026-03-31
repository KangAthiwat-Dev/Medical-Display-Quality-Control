import customtkinter as ctk

from constants.evaluation_questions import TEST_CONFIG
from styles.base_colors import (
    HISTORY_BUTTON_GRAY,
    HISTORY_BUTTON_GRAY_HOVER,
    HISTORY_CARD_COLOR,
    HISTORY_LINE_COLOR,
    TRANSPARENT,
    WHITE,
)


SECTION_BLUE = "#2F67D8"
HEADER_BG = ("#F2F2F2", "#F2F2F2")
CONTENT_BG = ("#E8E8E8", "#E8E8E8")
CONTENT_TEXT = ("#202020", "#202020")
CONTENT_LINE = ("#C7C7C7", "#C7C7C7")


class CriteriaScreen(ctk.CTkFrame):
    def __init__(self, master, back_command=None, **kwargs):
        kwargs.setdefault("fg_color", TRANSPARENT)
        super().__init__(master, **kwargs)

        self.back_command = back_command
        self.display_type = ""
        self.period = ""
        self.rows = []

        self._ui_built = False
        self._body = None
        self._table_entries = []
        self._empty_label = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self._build_ui()

    def on_show(self, display_type="", period="", **kwargs):
        if display_type:
            self.display_type = display_type
        if period:
            self.period = period

        self.rows = self._build_rows()
        self._build_ui()
        self._update_view()

    def _build_rows(self):
        groups = TEST_CONFIG.get(self.display_type, {}).get(self.period, [])
        rows = []
        for group in groups:
            items = group.get("items")
            if not items:
                continue

            section = {"section_title": group.get("group_title", ""), "items": []}
            for item in items:
                section["items"].append(
                    {
                        "title": item.get("title", ""),
                        "criterion": item.get("pass_criterion", ""),
                        "fix_guide": item.get("fix_guide", ""),
                    }
                )
            rows.append(section)
        return rows

    def _build_ui(self):
        if self._ui_built:
            return

        FONT_TH = "TH Sarabun New"
        FONT_TITLE = (FONT_TH, 30, "bold")
        FONT_HEADER = (FONT_TH, 20, "bold")
        FONT_ITEM = (FONT_TH, 17, "bold")

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
            text="เกณฑ์และวิธีการแก้ไขปัญหา",
            font=FONT_TITLE,
            text_color=WHITE,
        ).pack(side="left", expand=True)

        ctk.CTkFrame(card, height=1, fg_color=HISTORY_LINE_COLOR).grid(
            row=1, column=0, sticky="ew", padx=34, pady=(0, 14)
        )

        header = ctk.CTkFrame(card, corner_radius=18, fg_color=HEADER_BG)
        header.grid(row=2, column=0, sticky="ew", padx=34, pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="หัวข้อและเกณฑ์การประเมิน",
            font=FONT_HEADER,
            text_color=CONTENT_TEXT,
        ).grid(row=0, column=0, sticky="ew", padx=14, pady=10)

        ctk.CTkLabel(
            header,
            text="วิธีการแก้ไขปัญหากรณีไม่ผ่านเกณฑ์การประเมิน",
            font=FONT_HEADER,
            text_color=CONTENT_TEXT,
        ).grid(row=0, column=1, sticky="ew", padx=14, pady=10)

        body = ctk.CTkScrollableFrame(
            card,
            fg_color=CONTENT_BG,
            corner_radius=18,
            scrollbar_button_color=HISTORY_BUTTON_GRAY,
            scrollbar_button_hover_color=HISTORY_BUTTON_GRAY_HOVER,
        )
        body.grid(row=3, column=0, sticky="nsew", padx=34, pady=(0, 18))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_anchor("nw")
        self._body = body

        self._empty_label = ctk.CTkLabel(
            body,
            text="ยังไม่มีข้อมูลเกณฑ์การประเมิน",
            font=FONT_ITEM,
            text_color=CONTENT_TEXT,
            anchor="w",
            justify="left",
        )
        self._empty_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(16, 12))
        self._empty_label.grid_remove()

        self._ui_built = True

    def _flatten_rows(self):
        entries = []
        for section in self.rows or []:
            entries.append(
                (
                    "section",
                    {
                        "title": section.get("section_title", ""),
                    },
                )
            )
            items = section.get("items", []) or []
            for idx, item in enumerate(items):
                entries.append(
                    (
                        "item",
                        {
                            "left_text": f"{item.get('title', '')}\nเกณฑ์: {item.get('criterion', '')}",
                            "right_text": item.get("fix_guide", ""),
                            "show_divider": idx != len(items) - 1,
                        },
                    )
                )
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
        FONT_SECTION = (FONT_TH, 18, "bold")
        FONT_ITEM = (FONT_TH, 17, "bold")
        FONT_BODY = (FONT_TH, 16, "bold")

        if kind == "section":
            title_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=FONT_SECTION,
                text_color=SECTION_BLUE,
                anchor="w",
                justify="left",
                wraplength=780,
            )
            entry = {
                "kind": "section",
                "title": title_lbl,
                "widgets": [title_lbl],
            }
        else:
            left_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=FONT_ITEM,
                text_color=CONTENT_TEXT,
                anchor="nw",
                justify="left",
                wraplength=430,
            )
            right_lbl = ctk.CTkLabel(
                self._body,
                text="",
                font=FONT_BODY,
                text_color=CONTENT_TEXT,
                anchor="nw",
                justify="left",
                wraplength=430,
            )
            divider = ctk.CTkFrame(self._body, height=1, fg_color=CONTENT_LINE)
            entry = {
                "kind": "item",
                "left": left_lbl,
                "right": right_lbl,
                "divider": divider,
                "widgets": [left_lbl, right_lbl, divider],
            }

        self._table_entries[idx] = entry
        return entry

    def _update_view(self):
        if not self._ui_built or self._body is None:
            return

        entries = self._flatten_rows()
        if not entries:
            self._empty_label.grid()
            for entry in self._table_entries:
                if not entry:
                    continue
                for widget in entry.get("widgets", []):
                    widget.grid_remove()
            self.after(0, lambda: self._body._parent_canvas.yview_moveto(0))
            return

        self._empty_label.grid_remove()

        row_index = 0
        for idx, (kind, data) in enumerate(entries):
            entry = self._ensure_table_entry(kind, idx)
            if kind == "section":
                entry["title"].configure(text=data.get("title", ""))
                entry["title"].grid(
                    row=row_index,
                    column=0,
                    columnspan=2,
                    sticky="w",
                    padx=18,
                    pady=(12, 8),
                )
                row_index += 1
            else:
                entry["left"].configure(text=data.get("left_text", ""))
                entry["right"].configure(text=data.get("right_text", ""))

                entry["left"].grid(
                    row=row_index,
                    column=0,
                    sticky="nsew",
                    padx=(18, 12),
                    pady=(4, 12),
                )
                entry["right"].grid(
                    row=row_index,
                    column=1,
                    sticky="nsew",
                    padx=(12, 18),
                    pady=(4, 12),
                )

                if data.get("show_divider"):
                    entry["divider"].grid(
                        row=row_index + 1,
                        column=0,
                        columnspan=2,
                        sticky="ew",
                        padx=18,
                        pady=(0, 0),
                    )
                else:
                    entry["divider"].grid_remove()

                row_index += 2

        for idx in range(len(entries), len(self._table_entries)):
            entry = self._table_entries[idx]
            if not entry:
                continue
            for widget in entry.get("widgets", []):
                widget.grid_remove()

        self.after(0, lambda: self._body._parent_canvas.yview_moveto(0))

    def _on_back(self):
        if self.back_command:
            self.back_command()
