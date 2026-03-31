import customtkinter as ctk
from constants.select_type_text import (
    BACK_BUTTON_TEXT,
    CONFIRM_BUTTON_TEXT,
    DISPLAY_TYPES,
    PERIOD_ANNUAL_TEXT,
    PERIOD_MONTHLY_TEXT,
    PERIOD_QUARTERLY_TEXT,
    PERIOD_SECTION_TITLE,
    SCREEN_TITLE_TEXT,
)
from styles.base_colors import (
    DIVIDER_COLOR,
    SELECT_TYPE_ACCENT,
    SELECT_TYPE_ACCENT_HOVER,
    SELECT_TYPE_BG_COLOR,
    SELECT_TYPE_BUTTON_HOVER,
    SELECT_TYPE_BUTTON_NORMAL,
    SELECT_TYPE_CARD_HOVER,
    SELECT_TYPE_CARD_NORMAL,
    SELECT_TYPE_CARD_SELECTED,
    SELECT_TYPE_TEXT_MUTED,
    TRANSPARENT,
    WHITE,
)
from widgets.side_bar import SideBarWidget


class SelectTypeScreen(ctk.CTkFrame):
    def __init__(self, master,
                 back_command=None,
                 confirm_command=None,
                 **kwargs):
        kwargs.setdefault("fg_color", TRANSPARENT)
        super().__init__(master, **kwargs)

        self.back_command = back_command
        self.confirm_command = confirm_command
        self._selected_key = None
        self._selected_period = None
        self._card_widgets = {}   # key -> (card_frame, indicator)
        self._period_btns = {}
        self._confirm_btn = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkFrame(self, width=1, fg_color=DIVIDER_COLOR).grid(
            row=0, column=0, sticky="nse")

        # Main
        self.main_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self._build_ui()

    def _build_ui(self):
        FONT_TH = "TH Sarabun New"
        FONT_TITLE = (FONT_TH, 36, "bold")
        FONT_CARD_T = (FONT_TH, 22, "bold")
        FONT_CARD_S = (FONT_TH, 17)
        FONT_ICON = ("Segoe UI Emoji", 26)
        FONT_BTN = (FONT_TH, 18, "bold")

        self.main_frame.configure(fg_color=SELECT_TYPE_BG_COLOR)

        center = ctk.CTkFrame(self.main_frame, fg_color=TRANSPARENT)
        center.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.84)

        ctk.CTkButton(
            self.main_frame,
            text=BACK_BUTTON_TEXT,
            font=(FONT_TH, 20, "bold"),
            width=52,
            height=38,
            corner_radius=19,
            fg_color=SELECT_TYPE_BUTTON_NORMAL,
            hover_color=SELECT_TYPE_BUTTON_HOVER,
            text_color=WHITE,
            command=self._on_back,
        ).place(x=24, y=20)

        ctk.CTkLabel(
            center,
            text=SCREEN_TITLE_TEXT,
            font=FONT_TITLE,
            text_color=WHITE,
        ).pack(pady=(0, 28))

        for dt in DISPLAY_TYPES:
            self._make_card(
                center,
                dt,
                SELECT_TYPE_CARD_NORMAL,
                SELECT_TYPE_CARD_SELECTED,
                SELECT_TYPE_CARD_HOVER,
                FONT_ICON,
                FONT_CARD_T,
                FONT_CARD_S,
            )

        self._confirm_btn = ctk.CTkButton(
            self.main_frame,
            text=CONFIRM_BUTTON_TEXT,
            font=FONT_BTN,
            width=160,
            height=46,
            corner_radius=23,
            fg_color=SELECT_TYPE_BUTTON_NORMAL,
            hover_color=SELECT_TYPE_BUTTON_HOVER,
            text_color=WHITE,
            command=self._on_confirm,
        )
        self._confirm_btn.place(relx=1.0, rely=1.0, anchor="se", x=-32, y=-28)

        self._card_normal = SELECT_TYPE_CARD_NORMAL
        self._card_selected = SELECT_TYPE_CARD_SELECTED
        self._card_hover = SELECT_TYPE_CARD_HOVER
        self._font_th = FONT_TH
        self._gray_btn = SELECT_TYPE_BUTTON_NORMAL
        self._gray_hover = SELECT_TYPE_BUTTON_HOVER
        self._accent = SELECT_TYPE_ACCENT
        self._accent_hover = SELECT_TYPE_ACCENT_HOVER

        self.options_frame = ctk.CTkFrame(center, fg_color=TRANSPARENT)
        self.options_frame.pack(fill="x", pady=(16, 0))

    def _make_card(self, parent, dt,
                   color_normal, color_selected, color_hover,
                   font_icon, font_title, font_sub):
        key = dt["key"]

        card = ctk.CTkFrame(
            parent,
            corner_radius=14,
            fg_color=color_normal,
            cursor="hand2",
        )
        card.pack(fill="x", pady=6)

        inner = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            inner,
            text=dt["icon"],
            font=font_icon,
            text_color=WHITE,
            width=48,
        ).pack(side="left", padx=(0, 16))

        text_block = ctk.CTkFrame(inner, fg_color=TRANSPARENT)
        text_block.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            text_block,
            text=dt["title"],
            font=font_title,
            text_color=WHITE,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            text_block,
            text=dt["subtitle"],
            font=font_sub,
            text_color=DIVIDER_COLOR[0:2],
            anchor="w",
            wraplength=700,
            justify="left",
        ).pack(fill="x")

        indicator = ctk.CTkFrame(card, width=6, corner_radius=3, fg_color=TRANSPARENT)
        indicator.place(x=0, rely=0.1, relheight=0.8)

        self._card_widgets[key] = (card, indicator)

        for widget in (card, inner, text_block) + tuple(inner.winfo_children()) + tuple(text_block.winfo_children()):
            widget.bind("<Button-1>", lambda e, k=key: self._select(k))
            widget.bind("<Enter>", lambda e, c=card, k=key: self._on_hover(c, k, True))
            widget.bind("<Leave>", lambda e, c=card, k=key: self._on_hover(c, k, False))

    def _clear_period_options(self):
        for w in self.options_frame.winfo_children():
            w.destroy()
        self._period_btns.clear()

    def _lock_confirm(self):
        if self._confirm_btn is not None:
            self._confirm_btn.configure(fg_color=self._gray_btn, hover_color=self._gray_hover)

    def _unlock_confirm(self):
        if self._confirm_btn is not None:
            self._confirm_btn.configure(fg_color=self._accent, hover_color=self._accent_hover)

    def _reset_selection_state(self):
        self._selected_key = None
        self._selected_period = None
        self._clear_period_options()
        self._lock_confirm()
        for card, ind in self._card_widgets.values():
            card.configure(fg_color=self._card_normal)
            ind.configure(fg_color=TRANSPARENT)

    def _select(self, key: str):
        for k, (card, ind) in self._card_widgets.items():
            if k == key:
                card.configure(fg_color=self._card_selected)
                ind.configure(fg_color=WHITE)
            else:
                card.configure(fg_color=self._card_normal)
                ind.configure(fg_color=TRANSPARENT)

        self._selected_key = key
        self._selected_period = None
        self._lock_confirm()
        self._clear_period_options()

        ctk.CTkLabel(
            self.options_frame,
            text=PERIOD_SECTION_TITLE,
            font=(self._font_th, 16),
            text_color=SELECT_TYPE_TEXT_MUTED,
        ).pack(pady=(8, 16))

        if key == "diagnostic":
            row = ctk.CTkFrame(self.options_frame, fg_color=TRANSPARENT)
            row.pack(fill="x")
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=1)
            self._make_period_btn(row, PERIOD_MONTHLY_TEXT).grid(row=0, column=0, padx=(0, 4), sticky="ew")
            self._make_period_btn(row, PERIOD_QUARTERLY_TEXT).grid(row=0, column=1, padx=(4, 0), sticky="ew")

        elif key == "modality":
            row1 = ctk.CTkFrame(self.options_frame, fg_color=TRANSPARENT)
            row1.pack(fill="x")
            row1.grid_columnconfigure(0, weight=1)
            row1.grid_columnconfigure(1, weight=1)
            self._make_period_btn(row1, PERIOD_MONTHLY_TEXT).grid(row=0, column=0, padx=(0, 4), sticky="ew")
            self._make_period_btn(row1, PERIOD_QUARTERLY_TEXT).grid(row=0, column=1, padx=(4, 0), sticky="ew")

            row2 = ctk.CTkFrame(self.options_frame, fg_color=TRANSPARENT)
            row2.pack(fill="x", pady=(8, 0))
            row2.grid_columnconfigure(0, weight=1)
            row2.grid_columnconfigure(1, weight=1)
            row2.grid_columnconfigure(2, weight=1)
            self._make_period_btn(row2, PERIOD_ANNUAL_TEXT).grid(row=0, column=1, sticky="ew")

        elif key == "clinical":
            row = ctk.CTkFrame(self.options_frame, fg_color=TRANSPARENT)
            row.pack(fill="x")
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=1)
            self._make_period_btn(row, PERIOD_ANNUAL_TEXT).grid(row=0, column=1, sticky="ew")
            self._select_period(PERIOD_ANNUAL_TEXT)

    def _make_period_btn(self, parent, val):
        btn = ctk.CTkButton(
            parent,
            text=val,
            font=(self._font_th, 18, "bold"),
            height=42,
            corner_radius=6,
            fg_color=self._card_normal,
            hover_color=self._card_hover,
            text_color=WHITE,
            command=lambda v=val: self._select_period(v),
        )
        self._period_btns[val] = btn
        return btn

    def _select_period(self, val: str):
        self._selected_period = val
        for k, btn in self._period_btns.items():
            if k == val:
                btn.configure(fg_color=self._card_selected, hover_color=self._accent_hover)
            else:
                btn.configure(fg_color=self._card_normal, hover_color=self._card_hover)
        self._unlock_confirm()

    def _on_hover(self, card, key: str, entering: bool):
        if key != self._selected_key:
            card.configure(fg_color=self._card_hover if entering else self._card_normal)

    def on_show(self, **kwargs):
        self._reset_selection_state()
        if self._confirm_btn is not None:
            self.after(0, self._confirm_btn.focus_set)

    def on_hide(self, **kwargs):
        pass

    def _on_back(self):
        if self.back_command:
            self.back_command()

    def _on_confirm(self):
        if not self._selected_key or not self._selected_period:
            return
        if self.confirm_command:
            self.confirm_command(self._selected_key, self._selected_period)

    def get_selected(self) -> str | None:
        return self._selected_key
