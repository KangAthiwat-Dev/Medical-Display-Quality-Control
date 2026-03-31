import customtkinter as ctk

from constants.dock_bar_text import DOCK_ITEMS
from styles.base_colors import (
    DOCK_BAR_BG,
    DOCK_BAR_BORDER,
    DOCK_BAR_CIRCLE_BG,
    DOCK_BAR_CIRCLE_FG,
    DOCK_BAR_HOVER,
    DOCK_BAR_ICON,
    DOCK_BAR_TOOLTIP_BG,
    TRANSPARENT,
    WHITE,
)


class DockBarWidget(ctk.CTkFrame):
    def __init__(self, master, command=None, **kwargs):
        kwargs.setdefault("width", 52)
        kwargs.setdefault("corner_radius", 4)
        kwargs.setdefault("fg_color", DOCK_BAR_BG)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", DOCK_BAR_BORDER)
        super().__init__(master, **kwargs)

        self.command = command
        self._tooltip_win = None
        self._btn_refs = {}

        self.pack_propagate(False)
        self.configure(height=len(DOCK_ITEMS) * 52 + 16)  # สูงตาม content

        self._build()

    def _build(self):
        FONT_TH    = "TH Sarabun New"
        FONT_ICON  = ("Segoe UI Emoji", 17)
        FONT_CIRC  = (FONT_TH, 17, "bold")

        wrapper = ctk.CTkFrame(self, fg_color=TRANSPARENT)
        wrapper.pack(expand=True, fill="both", padx=6, pady=8)

        for idx, item in enumerate(DOCK_ITEMS):
            key     = item["key"]
            icon    = item["icon"]
            circle  = item.get("circle", False)
            tooltip = item.get("tooltip", "")

            if circle:
                # filled dark circle button
                btn = ctk.CTkButton(
                    wrapper,
                    text=icon,
                    font=FONT_CIRC,
                    width=38, height=38,
                    corner_radius=19,
                    fg_color=DOCK_BAR_CIRCLE_BG,
                    hover_color=DOCK_BAR_CIRCLE_BG,
                    text_color=DOCK_BAR_CIRCLE_FG,
                    border_width=0,
                    command=lambda k=key: self._on_click(k),
                )
            else:
                btn = ctk.CTkButton(
                    wrapper,
                    text=icon,
                    font=FONT_ICON,
                    width=38, height=38,
                    corner_radius=8,
                    fg_color=TRANSPARENT,
                    hover_color=DOCK_BAR_HOVER,
                    text_color=DOCK_BAR_ICON,
                    border_width=0,
                    command=lambda k=key: self._on_click(k),
                )

            btn.pack(pady=3)
            self._btn_refs[key] = btn

            # divider after 2nd item (between display and help)
            if idx == 1:
                ctk.CTkFrame(wrapper, height=1,
                             fg_color=DOCK_BAR_BORDER).pack(
                    fill="x", pady=4)

            # tooltip
            if tooltip:
                btn.bind("<Enter>", lambda e, t=tooltip, b=btn: self._show_tip(b, t), add="+")
                btn.bind("<Leave>", lambda e: self._hide_tip(), add="+")

    # ── Tooltip ─────────────────────────────────
    def _show_tip(self, widget, text: str):
        self._hide_tip()
        x = widget.winfo_rootx() + widget.winfo_width() + 6
        y = widget.winfo_rooty() + widget.winfo_height() // 2

        self._tooltip_win = tw = ctk.CTkToplevel(self)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)

        ctk.CTkLabel(
            tw, text=text,
            font=("TH Sarabun New", 14),
            fg_color=DOCK_BAR_TOOLTIP_BG,
            text_color=WHITE,
            corner_radius=6,
            padx=10, pady=4,
        ).pack()

    def _hide_tip(self):
        if self._tooltip_win:
            try:
                self._tooltip_win.destroy()
            except Exception:
                pass
            self._tooltip_win = None

    # ── Click ────────────────────────────────────
    def _on_click(self, key: str):
        if self.command:
            self.command(key)
