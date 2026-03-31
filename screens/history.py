import tkinter as tk
from tkinter import ttk
from datetime import datetime

import customtkinter as ctk

from constants.history_text import (
    DISPLAY_TYPE_FILTER_TO_KEY,
    DISPLAY_TYPE_KEY_TO_LABEL,
    HISTORY_BACK_TEXT,
    HISTORY_DATE_ERROR_TEXT,
    HISTORY_DATE_FROM_LABEL,
    HISTORY_DATE_PLACEHOLDER,
    HISTORY_DATE_TO_LABEL,
    HISTORY_DETAIL_BUTTON_TEXT,
    HISTORY_DISPLAY_TYPE_LABEL,
    HISTORY_DISPLAY_TYPE_OPTIONS,
    HISTORY_HOSPITAL_LABEL,
    HISTORY_HOSPITAL_PLACEHOLDER,
    HISTORY_PDF_BUTTON_TEXT,
    HISTORY_ROUND_LABEL,
    HISTORY_ROUND_OPTIONS,
    HISTORY_SELECTION_REQUIRED_TEXT,
    HISTORY_TABLE_HEADERS,
    HISTORY_TITLE_TEXT,
    ROUND_FILTER_TO_KEY,
    ROUND_KEY_TO_LABEL,
)
from styles.base_colors import (
    DIVIDER_COLOR,
    HISTORY_ACCENT,
    HISTORY_ACCENT_HOVER,
    HISTORY_BUTTON_GRAY,
    HISTORY_BUTTON_GRAY_HOVER,
    HISTORY_CARD_COLOR,
    HISTORY_DROPDOWN_BG,
    HISTORY_DROPDOWN_BUTTON,
    HISTORY_ERROR_TEXT,
    HISTORY_INPUT_BG,
    HISTORY_INPUT_TEXT,
    HISTORY_SEARCH_BG,
    HISTORY_SEARCH_PANEL,
    HISTORY_TEXT_MUTED,
    TRANSPARENT,
    WHITE,
)
from widgets.nav_bar import NavBarWidget
from widgets.side_bar import SideBarWidget


def _pick_color(value, fallback="#2b2b2b"):
    if isinstance(value, (tuple, list)):
        return value[0] if value else fallback
    return value or fallback


class HistoryScreen(ctk.CTkFrame):
    def __init__(self, master,
                 back_command=None,
                 search_command=None,
                 detail_command=None,
                 pdf_command=None,
                 display_type_options=None,
                 round_options=None,
                 records=None,
                 **kwargs):
        kwargs.setdefault("fg_color", TRANSPARENT)
        super().__init__(master, **kwargs)

        self.back_command = back_command
        self.search_command = search_command
        self.detail_command = detail_command
        self.pdf_command = pdf_command
        self.display_type_options = display_type_options or HISTORY_DISPLAY_TYPE_OPTIONS
        self.round_options = round_options or HISTORY_ROUND_OPTIONS

        self.records = records or []
        self._all_records = list(self.records)
        self._loaded_once = False
        self._multi_select_mode = False
        self._id_to_record = {}

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.navbar = NavBarWidget(self)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.navbar_separator = ctk.CTkFrame(self, height=1, fg_color=DIVIDER_COLOR)
        self.navbar_separator.grid(row=0, column=0, columnspan=2, sticky="sew")

        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        ctk.CTkFrame(self, width=1, fg_color="transparent").grid(row=1, column=0, sticky="nse")

        self.main_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT)
        self.main_frame.grid(row=1, column=1, sticky="nsew")

        self._build_ui()
        self._refresh_tree(self._sort_records(self.records))

    def _build_ui(self):
        FONT_TH = "TH Sarabun New"
        FONT_TITLE = (FONT_TH, 28, "bold")
        FONT_LABEL = (FONT_TH, 18)
        FONT_BTN = (FONT_TH, 18, "bold")

        bg_card = _pick_color(HISTORY_CARD_COLOR)
        bg_search = _pick_color(HISTORY_SEARCH_BG)

        card = ctk.CTkFrame(
            self.main_frame,
            corner_radius=16,
            fg_color=HISTORY_CARD_COLOR,
            border_width=0,
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)
        card.grid_rowconfigure(3, weight=1)
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        top.grid(row=0, column=0, sticky="ew", padx=28, pady=(14, 6))

        ctk.CTkButton(
            top,
            text=HISTORY_BACK_TEXT,
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
            text=HISTORY_TITLE_TEXT,
            font=FONT_TITLE,
            text_color=WHITE,
        ).pack(side="left", expand=True)

        search_bar = ctk.CTkFrame(card, corner_radius=24, fg_color=HISTORY_SEARCH_BG)
        search_bar.grid(row=1, column=0, sticky="ew", padx=28, pady=0)
        search_bar.grid_columnconfigure(0, weight=3)
        search_bar.grid_columnconfigure(1, weight=2)
        search_bar.grid_columnconfigure(2, weight=2)
        search_bar.grid_columnconfigure(3, weight=0)

        hospital_panel = ctk.CTkFrame(search_bar, fg_color=HISTORY_SEARCH_PANEL, corner_radius=18)
        hospital_panel.grid(row=0, column=0, sticky="ew", padx=(14, 8), pady=8)
        hospital_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hospital_panel,
            text=HISTORY_HOSPITAL_LABEL,
            font=(FONT_TH, 15),
            text_color=HISTORY_TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(7, 1))

        self.hospital_entry = ctk.CTkEntry(
            hospital_panel,
            placeholder_text=HISTORY_HOSPITAL_PLACEHOLDER,
            font=FONT_LABEL,
            height=40,
            corner_radius=16,
            fg_color=HISTORY_INPUT_BG,
            text_color=HISTORY_INPUT_TEXT,
            placeholder_text_color="#8a8a8a",
            border_width=0,
        )
        self.hospital_entry.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        self.hospital_entry.bind("<Return>", lambda _e: self._on_search())

        filters_panel = ctk.CTkFrame(search_bar, fg_color=TRANSPARENT)
        filters_panel.grid(row=0, column=1, sticky="ew", padx=(8, 8), pady=8)
        filters_panel.grid_columnconfigure(0, weight=1)
        filters_panel.grid_columnconfigure(1, weight=1)

        type_panel = ctk.CTkFrame(filters_panel, fg_color=HISTORY_SEARCH_PANEL, corner_radius=18)
        type_panel.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        type_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            type_panel,
            text=HISTORY_DISPLAY_TYPE_LABEL,
            font=(FONT_TH, 15),
            text_color=HISTORY_TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(7, 1))

        self.type_var = ctk.StringVar(value=self.display_type_options[0])
        self.type_dropdown = ctk.CTkOptionMenu(
            type_panel,
            values=self.display_type_options,
            variable=self.type_var,
            font=FONT_LABEL,
            height=40,
            corner_radius=16,
            fg_color=HISTORY_DROPDOWN_BG,
            button_color=HISTORY_DROPDOWN_BUTTON,
            button_hover_color=HISTORY_DROPDOWN_BUTTON,
            text_color=WHITE,
            dropdown_font=(FONT_TH, 16),
        )
        self.type_dropdown.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        round_panel = ctk.CTkFrame(filters_panel, fg_color=HISTORY_SEARCH_PANEL, corner_radius=18)
        round_panel.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        round_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            round_panel,
            text=HISTORY_ROUND_LABEL,
            font=(FONT_TH, 15),
            text_color=HISTORY_TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(7, 1))

        self.round_var = ctk.StringVar(value=self.round_options[0])
        self.round_dropdown = ctk.CTkOptionMenu(
            round_panel,
            values=self.round_options,
            variable=self.round_var,
            font=FONT_LABEL,
            height=40,
            corner_radius=16,
            fg_color=HISTORY_DROPDOWN_BG,
            button_color=HISTORY_DROPDOWN_BUTTON,
            button_hover_color=HISTORY_DROPDOWN_BUTTON,
            text_color=WHITE,
            dropdown_font=(FONT_TH, 16),
        )
        self.round_dropdown.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        date_panel = ctk.CTkFrame(search_bar, fg_color=TRANSPARENT)
        date_panel.grid(row=0, column=2, sticky="ew", padx=(8, 8), pady=8)
        date_panel.grid_columnconfigure(0, weight=1)
        date_panel.grid_columnconfigure(1, weight=1)

        date_from_panel = ctk.CTkFrame(date_panel, fg_color=HISTORY_SEARCH_PANEL, corner_radius=18)
        date_from_panel.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        date_from_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            date_from_panel,
            text=HISTORY_DATE_FROM_LABEL,
            font=(FONT_TH, 15),
            text_color=HISTORY_TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(7, 1))

        self.date_from_entry = ctk.CTkEntry(
            date_from_panel,
            placeholder_text=HISTORY_DATE_PLACEHOLDER,
            font=FONT_LABEL,
            height=40,
            corner_radius=16,
            fg_color=HISTORY_INPUT_BG,
            text_color=HISTORY_INPUT_TEXT,
            placeholder_text_color="#8a8a8a",
            border_width=0,
        )
        self.date_from_entry.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        self.date_from_entry.bind("<Return>", lambda _e: self._on_search())

        date_to_panel = ctk.CTkFrame(date_panel, fg_color=HISTORY_SEARCH_PANEL, corner_radius=18)
        date_to_panel.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        date_to_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            date_to_panel,
            text=HISTORY_DATE_TO_LABEL,
            font=(FONT_TH, 15),
            text_color=HISTORY_TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(7, 1))

        self.date_to_entry = ctk.CTkEntry(
            date_to_panel,
            placeholder_text=HISTORY_DATE_PLACEHOLDER,
            font=FONT_LABEL,
            height=40,
            corner_radius=16,
            fg_color=HISTORY_INPUT_BG,
            text_color=HISTORY_INPUT_TEXT,
            placeholder_text_color="#8a8a8a",
            border_width=0,
        )
        self.date_to_entry.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        self.date_to_entry.bind("<Return>", lambda _e: self._on_search())

        actions_panel = ctk.CTkFrame(search_bar, fg_color=TRANSPARENT)
        actions_panel.grid(row=0, column=3, sticky="e", padx=(0, 14), pady=8)

        self.search_btn = ctk.CTkButton(
            actions_panel,
            text="ค้นหา",
            font=FONT_BTN,
            height=40,
            width=120,
            corner_radius=16,
            fg_color=HISTORY_ACCENT,
            hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE,
            command=self._on_search,
        )
        self.search_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = ctk.CTkButton(
            actions_panel,
            text="ล้างตัวกรอง",
            font=FONT_BTN,
            height=40,
            width=140,
            corner_radius=16,
            fg_color=HISTORY_BUTTON_GRAY,
            hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE,
            command=self._on_clear_filters,
        )
        self.clear_btn.pack(side="left")

        self._error_label = ctk.CTkLabel(
            card,
            text="",
            font=(FONT_TH, 16),
            text_color=HISTORY_ERROR_TEXT,
        )
        self._error_label.grid(row=2, column=0, sticky="w", padx=32, pady=(0, 0))

        table_wrap = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        table_wrap.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 4))
        table_wrap.grid_rowconfigure(2, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        table_actions = ctk.CTkFrame(table_wrap, fg_color=TRANSPARENT)
        table_actions.grid(row=0, column=0, sticky="e", pady=(2, 10))

        self._multi_btn = ctk.CTkButton(
            table_actions,
            text="เลือกหลายรายการ",
            font=FONT_BTN,
            height=38,
            corner_radius=19,
            width=160,
            fg_color=HISTORY_BUTTON_GRAY,
            hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE,
            command=lambda: self._toggle_multi_select_mode(True),
        )
        self._multi_btn.pack(side="right")

        self._cancel_multi_btn = ctk.CTkButton(
            table_actions,
            text="ยกเลิก",
            font=FONT_BTN,
            height=38,
            corner_radius=19,
            width=120,
            fg_color=HISTORY_BUTTON_GRAY,
            hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE,
            command=lambda: self._toggle_multi_select_mode(False),
        )

        header_card = ctk.CTkFrame(table_wrap, fg_color=HISTORY_SEARCH_BG, corner_radius=16)
        header_card.grid(row=1, column=0, sticky="ew", pady=(0, 2))

        table_host = tk.Frame(header_card, bg=bg_search, highlightthickness=0, bd=0)
        table_host.pack(fill="both", expand=True, padx=10, pady=8)

        style = ttk.Style()
        try:
            style.theme_use("default")
        except Exception:
            pass

        style.configure(
            "HistoryHybrid.Treeview",
            font=(FONT_TH, 17),
            rowheight=34,
            background=bg_card,
            fieldbackground=bg_card,
            foreground="white",
            borderwidth=0,
            relief="flat",
        )
        style.configure(
            "HistoryHybrid.Treeview.Heading",
            font=(FONT_TH, 18, "bold"),
            background=bg_search,
            foreground="white",
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "HistoryHybrid.Treeview",
            background=[("selected", _pick_color(HISTORY_ACCENT, "#4a90d9"))],
            foreground=[("selected", "white")],
        )

        cols = ("rank", "date", "hospital", "display_type", "round", "evaluator", "display_model")
        self.tree = ttk.Treeview(
            table_host,
            columns=cols,
            show="headings",
            style="HistoryHybrid.Treeview",
            selectmode="browse",
        )

        widths = [90, 180, 250, 160, 160, 220, 230]
        anchors = ["center", "center", "w", "center", "center", "w", "w"]
        headers = list(HISTORY_TABLE_HEADERS)
        for col, header_text, width, anchor in zip(cols, headers, widths, anchors):
            self.tree.heading(col, text=header_text, anchor=anchor)
            self.tree.column(col, width=width, anchor=anchor, stretch=True)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_host, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", self._on_tree_double_click)

        bottom = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        bottom.grid(row=4, column=0, sticky="ew", padx=28, pady=(4, 20))
        bottom.grid_columnconfigure(0, weight=1)

        self._table_error_label = ctk.CTkLabel(
            bottom,
            text="",
            font=(FONT_TH, 16),
            text_color=HISTORY_ERROR_TEXT,
            anchor="w",
        )
        self._table_error_label.grid(row=0, column=0, sticky="w")

        button_group = ctk.CTkFrame(bottom, fg_color=TRANSPARENT)
        button_group.grid(row=0, column=1, sticky="e")

        self._detail_btn = ctk.CTkButton(
            button_group,
            text=HISTORY_DETAIL_BUTTON_TEXT,
            font=FONT_BTN,
            height=46,
            corner_radius=23,
            width=180,
            fg_color=HISTORY_ACCENT,
            hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE,
            command=self._on_detail,
        )
        self._detail_btn.pack(side="left", padx=(0, 12))

        self._pdf_btn = ctk.CTkButton(
            button_group,
            text=HISTORY_PDF_BUTTON_TEXT,
            font=FONT_BTN,
            height=46,
            corner_radius=23,
            width=180,
            fg_color=HISTORY_ACCENT,
            hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE,
            command=self._on_pdf,
        )
        self._pdf_btn.pack(side="left")

        self._update_selection_mode_ui()

    def _record_sort_key(self, record):
        value = record.get("date", "")
        record_id = record.get("id", 0) or 0

        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%Y-%m-%d",
        ):
            try:
                return (datetime.strptime(value, fmt), record_id)
            except ValueError:
                continue
        return (datetime.min, record_id)

    def _sort_records(self, records):
        return sorted(records, key=self._record_sort_key, reverse=True)

    def _format_record_datetime(self, value: str) -> str:
        if not value:
            return ""
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                continue
        return value

    def _parse_date_input(self, value: str) -> str:
        value = value.strip()
        if not value:
            return ""
        return datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d")

    def _record_date_iso(self, value: str) -> str:
        if not value:
            return ""
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return ""

    def _display_type_label(self, value: str) -> str:
        return DISPLAY_TYPE_KEY_TO_LABEL.get(value, value)

    def _round_label(self, value: str) -> str:
        return ROUND_KEY_TO_LABEL.get(value, value)

    def _refresh_tree(self, rows):
        self.records = list(rows)
        self._id_to_record = {}
        self.tree.delete(*self.tree.get_children())

        for idx, record in enumerate(rows, start=1):
            record_id = record.get("id", idx)
            iid = str(record_id)
            self._id_to_record[iid] = record
            self.tree.insert(
                "",
                "end",
                iid=iid,
                values=(
                    str(record.get("rank", idx)),
                    self._format_record_datetime(record.get("date", "")),
                    record.get("hospital", ""),
                    self._display_type_label(record.get("display_type", "")),
                    self._round_label(record.get("round", "")),
                    record.get("evaluator", ""),
                    record.get("display_model", ""),
                ),
            )

    def _show_table_error(self, text: str):
        self._table_error_label.configure(text=text)

    def _hide_table_error(self):
        self._table_error_label.configure(text="")

    def _set_error(self, text: str):
        self._error_label.configure(text=text)
        self._error_label.grid_configure(pady=(0, 8) if text else (0, 0))

    def _on_tree_select(self, _event=None):
        self._hide_table_error()

    def _on_tree_double_click(self, _event=None):
        self._on_detail()

    def _get_selected_records(self):
        selected = []
        for iid in self.tree.selection():
            record = self._id_to_record.get(str(iid))
            if record:
                selected.append(record)
        return selected

    def get_selected(self):
        selected = self._get_selected_records()
        return selected[0] if selected else None

    def _apply_filters(self, local_only: bool = False):
        hospital = self.hospital_entry.get().strip()
        display_type_label = self.type_var.get()
        round_label = self.round_var.get()
        date_from_text = self.date_from_entry.get().strip()
        date_to_text = self.date_to_entry.get().strip()

        try:
            date_from = self._parse_date_input(date_from_text)
            date_to = self._parse_date_input(date_to_text)
        except ValueError:
            self._set_error(HISTORY_DATE_ERROR_TEXT)
            return

        self._set_error("")

        if not local_only and self.search_command:
            self.search_command(
                hospital=hospital,
                display_type=DISPLAY_TYPE_FILTER_TO_KEY.get(display_type_label, ""),
                round_no=ROUND_FILTER_TO_KEY.get(round_label, ""),
                date_from=date_from,
                date_to=date_to,
            )
            return

        filtered = []
        for record in self._all_records:
            if hospital and hospital.lower() not in record.get("hospital", "").lower():
                continue

            if display_type_label != self.display_type_options[0]:
                wanted_type = DISPLAY_TYPE_FILTER_TO_KEY.get(display_type_label, "")
                if record.get("display_type", "") != wanted_type:
                    continue

            if round_label != self.round_options[0]:
                wanted_round = ROUND_FILTER_TO_KEY.get(round_label, "")
                if record.get("round", "") != wanted_round:
                    continue

            record_iso = self._record_date_iso(record.get("date", ""))
            if date_from and record_iso and record_iso < date_from:
                continue
            if date_to and record_iso and record_iso > date_to:
                continue

            filtered.append(record)

        self._refresh_tree(self._sort_records(filtered))

    def _on_search(self):
        self._hide_table_error()
        self._apply_filters()

    def _on_clear_filters(self):
        self.hospital_entry.delete(0, "end")
        self.type_var.set(self.display_type_options[0])
        self.type_dropdown.set(self.display_type_options[0])
        self.round_var.set(self.round_options[0])
        self.round_dropdown.set(self.round_options[0])
        self.date_from_entry.delete(0, "end")
        self.date_to_entry.delete(0, "end")
        self._hide_table_error()
        self._set_error("")
        self._apply_filters()

    def _toggle_multi_select_mode(self, enabled=None):
        if enabled is None:
            enabled = not self._multi_select_mode
        self._multi_select_mode = enabled
        self.tree.selection_remove(*self.tree.selection())
        self.tree.configure(selectmode="extended" if enabled else "browse")
        self._update_selection_mode_ui()
        self._hide_table_error()

    def _update_selection_mode_ui(self):
        if self._multi_select_mode:
            self._multi_btn.pack_forget()
            self._cancel_multi_btn.pack(side="right", padx=(0, 8))
            self._detail_btn.pack_forget()
            self._pdf_btn.pack_forget()
            self._pdf_btn.pack(side="left")
        else:
            self._cancel_multi_btn.pack_forget()
            self._multi_btn.pack(side="right")
            self._pdf_btn.pack_forget()
            self._detail_btn.pack_forget()
            self._detail_btn.pack(side="left", padx=(0, 12))
            self._pdf_btn.pack(side="left")

    def set_records(self, records: list):
        self._all_records = self._sort_records(list(records))
        self._apply_filters(local_only=True)

    def on_show(self, **kwargs):
        if not self._loaded_once:
            self._loaded_once = True
            if self.search_command:
                self._on_search()
            else:
                self._refresh_tree(self._sort_records(self._all_records))
        self.after(0, self.hospital_entry.focus_set)

    def on_hide(self, **kwargs):
        self._hide_table_error()
        self._set_error("")
        self.tree.selection_remove(*self.tree.selection())

    def _on_back(self):
        if self.back_command:
            self.back_command()

    def _on_detail(self):
        selected = self.get_selected()
        if not selected:
            self._show_table_error(HISTORY_SELECTION_REQUIRED_TEXT)
            return
        if self.detail_command:
            self.detail_command(selected)

    def _on_pdf(self):
        if not self.pdf_command:
            return

        selected = self._get_selected_records()
        if not selected:
            self._show_table_error(HISTORY_SELECTION_REQUIRED_TEXT)
            return

        if self._multi_select_mode or len(selected) > 1:
            self.pdf_command(selected)
        else:
            self.pdf_command(selected[0])
