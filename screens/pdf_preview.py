import os
import time
from collections import OrderedDict
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import ImageTk

from services.reports.pdf_render import get_page_count, render_page
from styles.base_colors import (
    HISTORY_ACCENT,
    HISTORY_ACCENT_HOVER,
    HISTORY_BUTTON_GRAY,
    HISTORY_BUTTON_GRAY_HOVER,
    HISTORY_CARD_COLOR,
    HISTORY_LINE_COLOR,
    TRANSPARENT,
    WHITE,
)


class PdfPreviewScreen(ctk.CTkFrame):
    def __init__(self, master, back_command=None, **kwargs):
        kwargs.setdefault("fg_color", TRANSPARENT)
        super().__init__(master, **kwargs)

        self.back_command = back_command
        self.pdf_bytes = b""
        self.default_filename = "report.pdf"
        self.title_text = "Preview PDF"
        self.page_index = 0
        self.page_count = 0
        self._tk_img = None
        self._perf_enabled = os.environ.get("MEDICAL_PERF", "").strip() not in ("", "0", "false", "False")
        self._ui_built = False
        self._pdf_key = None
        self._page_image_cache = OrderedDict()  # (page_index, max_w) -> ImageTk.PhotoImage (LRU)
        self._pdf_cache_max_pages = self._env_int("MEDICAL_CACHE_PDF_PAGES", 8, min_value=0, max_value=100)
        self._pdf_cache_warm_next = os.environ.get("MEDICAL_PDF_WARM_NEXT", "").strip() in ("1", "true", "True")
        self._title_label = None
        self.preview_label = None
        self.page_label = None
        self.prev_btn = None
        self.next_btn = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self._build_ui()

    def on_show(self, pdf_bytes=None, title_text=None, default_filename=None, **kwargs):
        if pdf_bytes is not None:
            self.pdf_bytes = pdf_bytes
            self.page_count = get_page_count(pdf_bytes) if pdf_bytes else 0
            self.page_index = 0
        if title_text:
            self.title_text = title_text
        if default_filename:
            self.default_filename = default_filename
        self._build_ui()

        # Reset cache when PDF changes
        pdf_key = (len(self.pdf_bytes or b""), (self.pdf_bytes or b"")[:32], (self.pdf_bytes or b"")[-32:])
        if pdf_key != self._pdf_key:
            self._pdf_key = pdf_key
            self._page_image_cache.clear()

        if self._title_label is not None:
            self._title_label.configure(text=self.title_text)

        self.after(1, self._render_current_page)

    def _env_int(self, name: str, default: int, min_value: int | None = None, max_value: int | None = None) -> int:
        raw = os.environ.get(name, "").strip()
        try:
            val = int(raw)
        except Exception:
            val = default
        if min_value is not None and val < min_value:
            val = min_value
        if max_value is not None and val > max_value:
            val = max_value
        return val

    def _lru_get(self, key):
        try:
            val = self._page_image_cache.pop(key)
        except KeyError:
            return None
        self._page_image_cache[key] = val
        return val

    def _lru_put(self, key, value):
        if self._pdf_cache_max_pages <= 0:
            return
        if key in self._page_image_cache:
            try:
                self._page_image_cache.pop(key)
            except KeyError:
                pass
        self._page_image_cache[key] = value
        while len(self._page_image_cache) > self._pdf_cache_max_pages:
            self._page_image_cache.popitem(last=False)

    def _build_ui(self):
        if self._ui_built:
            return

        FONT_TH = "TH Sarabun New"
        FONT_TITLE = (FONT_TH, 28, "bold")
        FONT_BTN = (FONT_TH, 18, "bold")
        FONT_META = (FONT_TH, 17, "bold")

        card = ctk.CTkFrame(self.main_frame, corner_radius=16, fg_color=HISTORY_CARD_COLOR)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.94, relheight=0.94)
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 10))

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

        self._title_label = ctk.CTkLabel(top, text=self.title_text, font=FONT_TITLE, text_color=WHITE)
        self._title_label.pack(side="left", expand=True)

        ctk.CTkFrame(card, height=1, fg_color=HISTORY_LINE_COLOR).grid(row=1, column=0, sticky="ew", padx=24)

        body = ctk.CTkScrollableFrame(
            card,
            fg_color=TRANSPARENT,
            scrollbar_button_color=HISTORY_BUTTON_GRAY,
            scrollbar_button_hover_color=HISTORY_BUTTON_GRAY_HOVER,
        )
        body.grid(row=2, column=0, sticky="nsew", padx=24, pady=(12, 12))
        body.grid_columnconfigure(0, weight=1)

        self.preview_label = ctk.CTkLabel(body, text="")
        self.preview_label.grid(row=0, column=0, sticky="n", pady=(0, 8))

        bottom = ctk.CTkFrame(card, fg_color=TRANSPARENT)
        bottom.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 18))

        nav = ctk.CTkFrame(bottom, fg_color=TRANSPARENT)
        nav.pack(side="left")

        self.prev_btn = ctk.CTkButton(
            nav,
            text="ก่อนหน้า",
            font=FONT_BTN,
            width=120,
            height=44,
            corner_radius=22,
            fg_color=HISTORY_BUTTON_GRAY,
            hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE,
            command=self._prev_page,
        )
        self.prev_btn.pack(side="left")

        self.page_label = ctk.CTkLabel(nav, text="", font=FONT_META, text_color=WHITE)
        self.page_label.pack(side="left", padx=14)

        self.next_btn = ctk.CTkButton(
            nav,
            text="ถัดไป",
            font=FONT_BTN,
            width=120,
            height=44,
            corner_radius=22,
            fg_color=HISTORY_BUTTON_GRAY,
            hover_color=HISTORY_BUTTON_GRAY_HOVER,
            text_color=WHITE,
            command=self._next_page,
        )
        self.next_btn.pack(side="left")

        ctk.CTkButton(
            bottom,
            text="บันทึก PDF",
            font=FONT_BTN,
            width=180,
            height=44,
            corner_radius=22,
            fg_color=HISTORY_ACCENT,
            hover_color=HISTORY_ACCENT_HOVER,
            text_color=WHITE,
            command=self._save_pdf,
        ).pack(side="right")

        self._ui_built = True

    def _render_current_page(self):
        t0 = time.perf_counter()
        if not self.pdf_bytes or self.page_count == 0:
            self.preview_label.configure(text="ไม่พบข้อมูล PDF สำหรับแสดง preview", image=None)
            self.page_label.configure(text="หน้า 0/0")
            return

        max_w = max(400, self.winfo_width() - 180)
        cache_key = (self.page_index, max_w)
        cached = self._lru_get(cache_key)
        if cached is None:
            image = render_page(self.pdf_bytes, self.page_index, scale=1.6)
            if image.width > max_w:
                ratio = max_w / image.width
                image = image.resize((int(image.width * ratio), int(image.height * ratio)))
            cached = ImageTk.PhotoImage(image)
            self._lru_put(cache_key, cached)

        self._tk_img = cached
        self.preview_label.configure(image=cached, text="")
        self.page_label.configure(text=f"หน้า {self.page_index + 1}/{self.page_count}")
        self.prev_btn.configure(state="normal" if self.page_index > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.page_index < (self.page_count - 1) else "disabled")

        if self._perf_enabled:
            print(
                f"[PERF] PdfPreviewScreen._render_current_page "
                f"page={self.page_index + 1}/{self.page_count} "
                f"ms={(time.perf_counter() - t0) * 1000:.1f}"
            )

        # Optional: warm up next page (bounded by LRU cap)
        if self._pdf_cache_warm_next and self.page_index + 1 < self.page_count:
            next_key = (self.page_index + 1, max_w)
            if next_key not in self._page_image_cache:
                self.after(1, lambda: self._warm_cache_page(self.page_index + 1, max_w))

    def _warm_cache_page(self, page_index: int, max_w: int):
        if not self.pdf_bytes or self.page_count == 0:
            return
        cache_key = (page_index, max_w)
        if cache_key in self._page_image_cache:
            return
        if self._pdf_cache_max_pages <= 0:
            return
        image = render_page(self.pdf_bytes, page_index, scale=1.6)
        if image.width > max_w:
            ratio = max_w / image.width
            image = image.resize((int(image.width * ratio), int(image.height * ratio)))
        self._lru_put(cache_key, ImageTk.PhotoImage(image))

    def warmup(self):
        # Hook for app preload; actual warmup occurs on_show when a PDF is provided.
        return

    def _prev_page(self):
        if self.page_index > 0:
            self.page_index -= 1
            self._render_current_page()

    def _next_page(self):
        if self.page_index < self.page_count - 1:
            self.page_index += 1
            self._render_current_page()

    def _save_pdf(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=self.default_filename,
        )
        if not path:
            return
        Path(path).write_bytes(self.pdf_bytes)
        messagebox.showinfo("บันทึกสำเร็จ", f"บันทึกไฟล์ PDF เรียบร้อยแล้ว\n{path}")

    def _on_back(self):
        if self.back_command:
            self.back_command()
