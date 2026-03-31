import os
import time
import customtkinter as ctk
from datetime import datetime
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
    HISTORY_EMPTY_TEXT,
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
    HISTORY_LINE_COLOR,
    HISTORY_PLACEHOLDER,
    HISTORY_ROW_HOVER,
    HISTORY_ROW_SELECTED,
    HISTORY_SEARCH_BG,
    HISTORY_SEARCH_PANEL,
    HISTORY_TEXT_GRAY,
    HISTORY_TEXT_MUTED,
    TRANSPARENT,
    WHITE,
)
from widgets.nav_bar import NavBarWidget
from widgets.side_bar import SideBarWidget


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

        self.back_command   = back_command
        self.search_command = search_command
        self.detail_command = detail_command
        self.pdf_command    = pdf_command
        self.display_type_options = display_type_options or HISTORY_DISPLAY_TYPE_OPTIONS
        self.round_options        = round_options or HISTORY_ROUND_OPTIONS
        self.records = records or []
        self._all_records = list(self.records)
        self._selected_idx = None
        self._row_frames = []
        self._row_pool = []
        self._empty_row_label = None
        self._multi_select_mode = False
        self._checked_ids = set()
        self._perf_enabled = os.environ.get("MEDICAL_PERF", "").strip() not in ("", "0", "false", "False")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Nav bar ──
        self.navbar = NavBarWidget(self)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.navbar_separator = ctk.CTkFrame(self, height=1, fg_color=DIVIDER_COLOR)
        self.navbar_separator.grid(row=0, column=0, columnspan=2, sticky="sew")

        # ── Sidebar ──
        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        ctk.CTkFrame(self, width=1, fg_color="transparent").grid(row=1, column=0, sticky="nse")

        # ── Main ──
        self.main_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT)
        self.main_frame.grid(row=1, column=1, sticky="nsew")

        self._build_ui()

    # ──────────────────────────────────────────────
    def _build_ui(self):
        FONT_TH     = "TH Sarabun New"
        FONT_TITLE  = (FONT_TH, 28, "bold")
        FONT_LABEL  = (FONT_TH, 18)
        FONT_HEADER = (FONT_TH, 18, "bold")
        FONT_ROW    = (FONT_TH, 17)
        FONT_BTN    = (FONT_TH, 18, "bold")

        # ── Card ──
        card = ctk.CTkFrame(
            self.main_frame, corner_radius=16,
            fg_color=HISTORY_CARD_COLOR,
            border_width=0,
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)
        card.grid_rowconfigure(3, weight=1)
        card.grid_columnconfigure(0, weight=1)

        # ══ Row 0: Back + Title ══
        top = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        top.grid(row=0, column=0, sticky="ew", padx=28, pady=(14, 6))

        ctk.CTkButton(
            top, text=HISTORY_BACK_TEXT, font=(FONT_TH, 20, "bold"),
            width=52, height=38, corner_radius=19,
            fg_color=HISTORY_BUTTON_GRAY, hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE, command=self._on_back,
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=HISTORY_TITLE_TEXT,
            font=FONT_TITLE, text_color=WHITE,
        ).pack(side="left", expand=True)

        # ══ Row 1: Search bar ══
        search_bar = ctk.CTkFrame(card, corner_radius=24, fg_color=HISTORY_SEARCH_BG)
        search_bar.grid(row=1, column=0, sticky="ew", padx=28, pady=0)
        search_bar.grid_columnconfigure(0, weight=3)
        search_bar.grid_columnconfigure(1, weight=2)
        search_bar.grid_columnconfigure(2, weight=2)

        hospital_panel = ctk.CTkFrame(search_bar, fg_color=HISTORY_SEARCH_PANEL, corner_radius=18)
        hospital_panel.grid(row=0, column=0, sticky="ew", padx=(14, 8), pady=8)
        hospital_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hospital_panel, text=HISTORY_HOSPITAL_LABEL,
            font=(FONT_TH, 15), text_color=HISTORY_TEXT_MUTED, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(7, 1))

        self.hospital_entry = ctk.CTkEntry(
            hospital_panel,
            placeholder_text=HISTORY_HOSPITAL_PLACEHOLDER,
            font=FONT_LABEL, height=40, corner_radius=16,
            fg_color=HISTORY_INPUT_BG, text_color=HISTORY_INPUT_TEXT,
            placeholder_text_color=HISTORY_PLACEHOLDER, border_width=0,
        )
        self.hospital_entry.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        filters_panel = ctk.CTkFrame(search_bar, fg_color=TRANSPARENT)
        filters_panel.grid(row=0, column=1, sticky="ew", padx=(8, 8), pady=8)
        filters_panel.grid_columnconfigure(0, weight=1)
        filters_panel.grid_columnconfigure(1, weight=1)

        type_panel = ctk.CTkFrame(filters_panel, fg_color=HISTORY_SEARCH_PANEL, corner_radius=18)
        type_panel.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        type_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            type_panel, text=HISTORY_DISPLAY_TYPE_LABEL,
            font=(FONT_TH, 15), text_color=HISTORY_TEXT_MUTED, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(7, 1))

        self.type_var = ctk.StringVar(value=self.display_type_options[0])
        self.type_dropdown = ctk.CTkOptionMenu(
            type_panel,
            values=self.display_type_options,
            variable=self.type_var,
            font=FONT_LABEL, height=40, corner_radius=16,
            fg_color=HISTORY_DROPDOWN_BG, button_color=HISTORY_DROPDOWN_BUTTON,
            button_hover_color=HISTORY_DROPDOWN_BUTTON,
            text_color=WHITE, dropdown_font=(FONT_TH, 16),
        )
        self.type_dropdown.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        round_panel = ctk.CTkFrame(filters_panel, fg_color=HISTORY_SEARCH_PANEL, corner_radius=18)
        round_panel.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        round_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            round_panel, text=HISTORY_ROUND_LABEL,
            font=(FONT_TH, 15), text_color=HISTORY_TEXT_MUTED, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(7, 1))

        self.round_var = ctk.StringVar(value=self.round_options[0])
        self.round_dropdown = ctk.CTkOptionMenu(
            round_panel,
            values=self.round_options,
            variable=self.round_var,
            font=FONT_LABEL, height=40, corner_radius=16,
            fg_color=HISTORY_DROPDOWN_BG, button_color=HISTORY_DROPDOWN_BUTTON,
            button_hover_color=HISTORY_DROPDOWN_BUTTON,
            text_color=WHITE, dropdown_font=(FONT_TH, 16),
        )
        self.round_dropdown.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        date_panel = ctk.CTkFrame(search_bar, fg_color=TRANSPARENT)
        date_panel.grid(row=0, column=2, sticky="ew", padx=(8, 14), pady=8)
        date_panel.grid_columnconfigure(0, weight=1)
        date_panel.grid_columnconfigure(1, weight=1)

        date_from_panel = ctk.CTkFrame(date_panel, fg_color=HISTORY_SEARCH_PANEL, corner_radius=18)
        date_from_panel.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        date_from_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            date_from_panel, text=HISTORY_DATE_FROM_LABEL,
            font=(FONT_TH, 15), text_color=HISTORY_TEXT_MUTED, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(7, 1))

        self.date_from_entry = ctk.CTkEntry(
            date_from_panel,
            placeholder_text=HISTORY_DATE_PLACEHOLDER,
            font=FONT_LABEL, height=40, corner_radius=16,
            fg_color=HISTORY_INPUT_BG, text_color=HISTORY_INPUT_TEXT,
            placeholder_text_color=HISTORY_PLACEHOLDER, border_width=0,
        )
        self.date_from_entry.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        date_to_panel = ctk.CTkFrame(date_panel, fg_color=HISTORY_SEARCH_PANEL, corner_radius=18)
        date_to_panel.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        date_to_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            date_to_panel, text=HISTORY_DATE_TO_LABEL,
            font=(FONT_TH, 15), text_color=HISTORY_TEXT_MUTED, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(7, 1))

        self.date_to_entry = ctk.CTkEntry(
            date_to_panel,
            placeholder_text=HISTORY_DATE_PLACEHOLDER,
            font=FONT_LABEL, height=40, corner_radius=16,
            fg_color=HISTORY_INPUT_BG, text_color=HISTORY_INPUT_TEXT,
            placeholder_text_color=HISTORY_PLACEHOLDER, border_width=0,
        )
        self.date_to_entry.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        self._error_label = ctk.CTkLabel(
            card,
            text="",
            font=(FONT_TH, 16),
            text_color=HISTORY_ERROR_TEXT,
        )
        self._error_label.grid(row=2, column=0, sticky="w", padx=32, pady=(0, 0))

        # ══ Row 2: Table ══
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
            command=self._toggle_multi_select_mode,
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

        COLS = HISTORY_TABLE_HEADERS
        COL_WEIGHTS = [1, 2, 3, 2, 2, 3, 2]

        # header
        header_card = ctk.CTkFrame(
            table_wrap,
            fg_color=HISTORY_SEARCH_BG,
            corner_radius=16,
        )
        header_card.grid(row=1, column=0, sticky="ew", pady=(0, 2))
        header = ctk.CTkFrame(header_card, fg_color=TRANSPARENT)
        header.pack(fill="x", padx=12, pady=8)
        for i, w in enumerate(COL_WEIGHTS):
            header.grid_columnconfigure(i, weight=w)

        for col_i, col_name in enumerate(COLS):
            ctk.CTkLabel(
                header, text=col_name,
                font=FONT_HEADER, text_color=WHITE, anchor="w",
            ).grid(row=0, column=col_i, padx=12, pady=0, sticky="ew")

        # scrollable rows
        self._scroll = ctk.CTkScrollableFrame(
            table_wrap, fg_color=TRANSPARENT,
            scrollbar_button_color=HISTORY_BUTTON_GRAY,
            scrollbar_button_hover_color=HISTORY_BUTTON_GRAY_HOVER,
        )
        self._scroll.grid(row=2, column=0, sticky="nsew")
        table_wrap.grid_rowconfigure(2, weight=1)
        self._scroll.grid_anchor("nw")
        for i, w in enumerate(COL_WEIGHTS):
            self._scroll.grid_columnconfigure(i, weight=w)
        table_wrap.bind("<Button-1>", lambda e: self._clear_selection())
        self._scroll.bind("<Button-1>", lambda e: self._clear_selection())

        self._col_weights = COL_WEIGHTS
        self._font_row    = FONT_ROW
        self._line_color  = HISTORY_LINE_COLOR
        self._text_white  = WHITE
        self._text_gray   = HISTORY_TEXT_GRAY

        self._render_rows()

        # ══ Row 3: Bottom actions ══
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
            button_group, text=HISTORY_DETAIL_BUTTON_TEXT, font=FONT_BTN,
            height=46, corner_radius=23, width=180,
            fg_color=HISTORY_ACCENT, hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE, command=self._on_detail,
        )
        self._detail_btn.pack(side="left", padx=(0, 12))

        self._pdf_btn = ctk.CTkButton(
            button_group, text=HISTORY_PDF_BUTTON_TEXT, font=FONT_BTN,
            height=46, corner_radius=23, width=180,
            fg_color=HISTORY_ACCENT, hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE, command=self._on_pdf,
        )
        self._pdf_btn.pack(side="left")

        self._update_selection_mode_ui()

        self.hospital_entry.bind("<KeyRelease>", self._on_filter_change)
        self.date_from_entry.bind("<KeyRelease>", self._on_filter_change)
        self.date_to_entry.bind("<KeyRelease>", self._on_filter_change)
        self.type_dropdown.configure(command=lambda _: self._on_filter_change())
        self.round_dropdown.configure(command=lambda _: self._on_filter_change())

    # ──────────────────────────────────────────────
    def _render_rows(self, reset_scroll: bool = True):
        t0 = time.perf_counter()
        if self._empty_row_label is None:
            self._empty_row_label = ctk.CTkLabel(
                self._scroll,
                text="ไม่พบข้อมูล",
                font=self._font_row,
                text_color=self._text_gray,
                anchor="w",
            )

        if not self.records:
            self._empty_row_label.grid(row=0, column=0, columnspan=7, pady=24, sticky="w")
            for entry in self._row_pool:
                entry["row"].grid_remove()
                entry["divider"].grid_remove()
            self._row_frames = []
            if reset_scroll:
                self.after(0, lambda: self._scroll._parent_canvas.yview_moveto(0))
            if self._perf_enabled:
                print(
                    f"[PERF] HistoryScreen._render_rows rows=0 "
                    f"multi={int(self._multi_select_mode)} ms={(time.perf_counter() - t0) * 1000:.1f}"
                )
            return
        else:
            self._empty_row_label.grid_remove()

        if self._selected_idx is not None and self._selected_idx >= len(self.records):
            self._selected_idx = None
        if not self._multi_select_mode:
            self._checked_ids.clear()

        # Ensure pool size
        while len(self._row_pool) < len(self.records):
            row_frame = ctk.CTkFrame(
                self._scroll,
                fg_color=TRANSPARENT,
                corner_radius=12,
                cursor="hand2",
            )
            for i, w in enumerate(self._col_weights):
                row_frame.grid_columnconfigure(i, weight=w)

            # Column 0 always uses a cell frame with optional checkbox
            cell0 = ctk.CTkFrame(row_frame, fg_color=TRANSPARENT)
            cell0.grid(row=0, column=0, padx=12, pady=8, sticky="ew")
            cell0.grid_columnconfigure(2, weight=1)

            check = ctk.CTkCheckBox(
                cell0,
                text="",
                width=18,
                checkbox_width=18,
                checkbox_height=18,
                fg_color=HISTORY_ACCENT,
                hover_color=HISTORY_ACCENT_HOVER,
                border_color=WHITE,
                checkmark_color=WHITE,
            )
            check.grid(row=0, column=0, padx=(0, 8), sticky="w")

            label0 = ctk.CTkLabel(
                cell0,
                text="",
                font=self._font_row,
                text_color=self._text_white,
                anchor="w",
                cursor="hand2",
            )
            label0.grid(row=0, column=2, sticky="w")

            labels = [label0]
            for col_i in range(1, 7):
                lbl = ctk.CTkLabel(
                    row_frame,
                    text="",
                    font=self._font_row,
                    text_color=self._text_white,
                    anchor="w",
                )
                lbl.grid(row=0, column=col_i, padx=12, pady=8, sticky="ew")
                labels.append(lbl)

            divider = ctk.CTkFrame(self._scroll, height=1, fg_color=self._line_color)
            self._row_pool.append(
                {
                    "row": row_frame,
                    "divider": divider,
                    "cell0": cell0,
                    "check": check,
                    "labels": labels,
                }
            )

        # Render visible rows
        self._row_frames = []
        for idx, rec in enumerate(self.records):
            record_id = rec.get("id")
            fields = [
                str(rec.get("rank", idx + 1)),
                self._format_record_datetime(rec.get("date", "")),
                rec.get("hospital", ""),
                self._display_type_label(rec.get("display_type", "")),
                self._round_label(rec.get("round", "")),
                rec.get("evaluator", ""),
                rec.get("display_model", ""),
            ]

            entry = self._row_pool[idx]
            row_frame = entry["row"]
            divider = entry["divider"]
            check = entry["check"]
            labels = entry["labels"]

            is_selected = (idx == self._selected_idx) if not self._multi_select_mode else (record_id in self._checked_ids)
            row_frame.configure(fg_color=HISTORY_ROW_SELECTED if is_selected else TRANSPARENT)

            # Position row + divider
            row_frame.grid(row=idx * 2, column=0, columnspan=7, sticky="ew", pady=(0, 2))
            divider.grid(row=idx * 2 + 1, column=0, columnspan=7, sticky="ew", padx=4, pady=(0, 4))
            self._row_frames.append(row_frame)

            # Checkbox visibility + state
            if self._multi_select_mode:
                check.grid()
                if record_id in self._checked_ids:
                    check.select()
                else:
                    check.deselect()
            else:
                check.grid_remove()
                check.deselect()

            # Update label texts
            for col_i, val in enumerate(fields):
                labels[col_i].configure(text=val)

            # Rebind events (replace previous bindings)
            if self._multi_select_mode:
                for w in [row_frame, entry["cell0"], check] + labels:
                    w.bind("<Button-1>", lambda e, rid=record_id: self._handle_multi_select_click(e, rid))
                row_frame.bind("<Enter>", lambda e, i=idx: self._set_row_hover(i, True))
                row_frame.bind("<Leave>", lambda e, i=idx: self._set_row_hover(i, False))
            else:
                for w in [row_frame, entry["cell0"]] + labels:
                    w.bind("<Button-1>", lambda e, i=idx: self._select_row(i))
                    w.bind("<Double-Button-1>", lambda e, i=idx: self._open_detail(i))
                row_frame.bind("<Enter>", lambda e, i=idx: self._set_row_hover(i, True))
                row_frame.bind("<Leave>", lambda e, i=idx: self._set_row_hover(i, False))

        # Hide extra pooled rows
        for j in range(len(self.records), len(self._row_pool)):
            self._row_pool[j]["row"].grid_remove()
            self._row_pool[j]["divider"].grid_remove()

        if reset_scroll:
            self.after(0, lambda: self._scroll._parent_canvas.yview_moveto(0))

        if self._perf_enabled:
            print(
                f"[PERF] HistoryScreen._render_rows rows={len(self.records)} "
                f"multi={int(self._multi_select_mode)} ms={(time.perf_counter() - t0) * 1000:.1f}"
            )

    def _select_row(self, idx: int):
        if self._multi_select_mode:
            return
        self._selected_idx = idx
        self._hide_table_error()
        self._refresh_row_styles()

    def _clear_selection(self):
        if self._multi_select_mode:
            return
        if self._selected_idx is None:
            return
        self._selected_idx = None
        self._refresh_row_styles()

    def _set_row_hover(self, idx: int, entering: bool):
        if idx >= len(self._row_frames):
            return
        if self._selected_idx == idx:
            return
        if self._multi_select_mode and self.records[idx].get("id") in self._checked_ids:
            return
        self._row_frames[idx].configure(fg_color=HISTORY_ROW_HOVER if entering else TRANSPARENT)

    def _refresh_row_styles(self):
        for idx, row_frame in enumerate(self._row_frames):
            if self._multi_select_mode:
                record = self.records[idx]
                row_frame.configure(
                    fg_color=HISTORY_ROW_SELECTED if record.get("id") in self._checked_ids else TRANSPARENT
                )
            else:
                row_frame.configure(fg_color=HISTORY_ROW_SELECTED if idx == self._selected_idx else TRANSPARENT)

    def _show_table_error(self, text: str):
        self._table_error_label.configure(text=text)
        self._table_error_label.grid_configure(pady=(0, 0))

    def _hide_table_error(self):
        self._table_error_label.configure(text="")
        self._table_error_label.grid_configure(pady=(0, 0))

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

    # ── Public ──
    def set_records(self, records: list):
        self._all_records = self._sort_records(list(records))
        self._apply_filters(local_only=True)

    def get_selected(self):
        if self._selected_idx is not None:
            return self.records[self._selected_idx]
        return None

    # ── Callbacks ──
    def _on_back(self):
        if self.back_command:
            self.back_command()

    def _on_search(self):
        self._apply_filters()

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
        if self._multi_select_mode:
            selected = [record for record in self.records if record.get("id") in self._checked_ids]
            if not selected:
                self._show_table_error(HISTORY_SELECTION_REQUIRED_TEXT)
                return
            self.pdf_command(selected)
        else:
            selected = self.get_selected()
            if not selected:
                self._show_table_error(HISTORY_SELECTION_REQUIRED_TEXT)
                return
            self.pdf_command(selected)

    def _open_detail(self, idx: int):
        self._select_row(idx)
        self._on_detail()

    def _display_type_label(self, value: str) -> str:
        return DISPLAY_TYPE_KEY_TO_LABEL.get(value, value)

    def _round_label(self, value: str) -> str:
        return ROUND_KEY_TO_LABEL.get(value, value)

    def _format_record_datetime(self, value: str) -> str:
        if not value:
            return ""

        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
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

    def _on_filter_change(self, event=None):
        self.after(10, self._apply_filters)

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
            self._error_label.configure(text=HISTORY_DATE_ERROR_TEXT)
            self._error_label.grid_configure(pady=(0, 8))
            return

        self._error_label.configure(text="")
        self._error_label.grid_configure(pady=(0, 0))

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
            if display_type_label != "ทั้งหมด" and record.get("display_type", "") != DISPLAY_TYPE_FILTER_TO_KEY.get(display_type_label, ""):
                continue
            if round_label != "ทั้งหมด" and record.get("round", "") != ROUND_FILTER_TO_KEY.get(round_label, ""):
                continue

            record_date = record.get("date", "")
            try:
                record_iso = datetime.strptime(record_date, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                record_iso = ""

            if date_from and record_iso and record_iso < date_from:
                continue
            if date_to and record_iso and record_iso > date_to:
                continue

            filtered.append(record)

        self.records = self._sort_records(filtered)
        self._render_rows(reset_scroll=False)

    def _toggle_multi_select_mode(self, enabled=None):
        if enabled is None:
            enabled = not self._multi_select_mode
        self._multi_select_mode = enabled
        self._checked_ids = set() if not enabled else self._checked_ids
        self._selected_idx = None
        self._hide_table_error()
        self._update_selection_mode_ui()
        self._render_rows()

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

    def _toggle_checked_record(self, record_id):
        if not self._multi_select_mode or record_id is None:
            return
        if record_id in self._checked_ids:
            self._checked_ids.remove(record_id)
        else:
            self._checked_ids.add(record_id)
        self._hide_table_error()
        self._render_rows()

    def _handle_multi_select_click(self, event, record_id):
        self._toggle_checked_record(record_id)
        return "break"
