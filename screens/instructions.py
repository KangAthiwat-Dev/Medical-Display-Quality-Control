import customtkinter as ctk
from PIL import Image
import os
from widgets.side_bar import SideBarWidget


# ── คำแนะนำแต่ละข้อ ──────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTRUCTIONS = [
    {
        "number":   "1",
        "image":    os.path.join(PROJECT_ROOT, "assets", "images", "image_1.png"),
        "caption":  "ควรเปิดหน้าจอไว้ก่อน 30 นาที",
    },
    {
        "number":   "2",
        "image":    os.path.join(PROJECT_ROOT, "assets", "images", "image_2.png"),
        "caption":  (
            "ระยะห่างของการทดสอบตั้งแต่ระยะสายตา\n"
            "ของผู้ทดสอบถึงหน้าจอควรมีระยะห่าง\n"
            "ประมาณหนึ่งช่วงแขน\n"
            "(ประมาณ 65 เซนติเมตร)"
        ),
    },
    {
        "number":   "3",
        "image":    os.path.join(PROJECT_ROOT, "assets", "images", "image_3.png"),
        "caption":  (
            "ทำความสะอาดหน้าจอก่อนตาม\n"
            "ที่บริษัทผู้ผลิตแนะนำการทดสอบ"
        ),
    },
]


class InstructionsScreen(ctk.CTkFrame):
    def __init__(self, master,
                 back_command=None,
                 next_command=None,
                 **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self.back_command = back_command
        self.next_command = next_command
        self._image_refs = []
        self._next_button = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Sidebar ──
        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkFrame(self, width=1, fg_color=("#cccccc", "#333333")).grid(
            row=0, column=0, sticky="nse")

        # ── Main ──
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self._build_ui()

    # ──────────────────────────────────────────────
    def _build_ui(self):
        FONT_TH      = "TH Sarabun New"
        FONT_TITLE   = (FONT_TH, 26, "bold")
        FONT_NUMBER  = (FONT_TH, 32, "bold")
        FONT_CAPTION = (FONT_TH, 17)
        FONT_BTN     = (FONT_TH, 18, "bold")

        CARD_COLOR   = ("#2b2b2b", "#2b2b2b")
        LINE_COLOR   = ("#3a3a3a", "#3a3a3a")
        NUM_BG       = ("white", "white")
        NUM_FG       = ("#1a1a1a", "#1a1a1a")
        GRAY_BTN     = ("#4a4a4a", "#4a4a4a")
        GRAY_HOVER   = ("#3a3a3a", "#3a3a3a")
        ACCENT       = "#1d5bbf"
        ACCENT_HOVER = "#174fa3"
        IMG_SIZE     = (200, 200)

        # ── Card ──
        card = ctk.CTkFrame(
            self.main_frame, corner_radius=16, fg_color=CARD_COLOR)
        card.place(relx=0.5, rely=0.5, anchor="center",
                   relwidth=0.90, relheight=0.90)
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        # ── Top bar: back + title ──
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 0))

        ctk.CTkButton(
            top, text="↩", font=(FONT_TH, 20, "bold"),
            width=52, height=38, corner_radius=19,
            fg_color=GRAY_BTN, hover_color=GRAY_HOVER,
            text_color="white", command=self._on_back,
        ).pack(side="left")

        ctk.CTkLabel(
            top, text="คำแนะนำในการทดสอบระบบ",
            font=FONT_TITLE, text_color="white",
        ).pack(side="left", expand=True)

        # divider under title
        ctk.CTkFrame(card, height=1, fg_color=LINE_COLOR).grid(
            row=1, column=0, sticky="ew", padx=24, pady=(10, 0))

        # ── Instruction columns ──
        cols_frame = ctk.CTkFrame(card, fg_color="transparent")
        cols_frame.grid(row=2, column=0, sticky="nsew", padx=24, pady=20)
        cols_frame.grid_rowconfigure(0, weight=1)

        self._image_refs.clear()
        for col_i, item in enumerate(INSTRUCTIONS):
            cols_frame.grid_columnconfigure(col_i, weight=1)
            col = ctk.CTkFrame(cols_frame, fg_color="transparent")
            col.grid(row=0, column=col_i, sticky="nsew", padx=8)
            col.grid_rowconfigure(2, weight=1)
            col.grid_columnconfigure(0, weight=1)

            # ── Number badge ──
            badge = ctk.CTkFrame(col, width=56, height=56,
                                 corner_radius=28, fg_color=NUM_BG)
            badge.grid(row=0, column=0, pady=(8, 12))
            badge.grid_propagate(False)
            ctk.CTkLabel(
                badge,
                text=item["number"],
                font=FONT_NUMBER,
                text_color=NUM_FG,
            ).place(relx=0.5, rely=0.5, anchor="center")

            # ── Image ──
            img_frame = ctk.CTkFrame(col, fg_color="transparent")
            img_frame.grid(row=1, column=0, pady=(0, 16))

            img_path = item["image"]
            if os.path.exists(img_path):
                try:
                    pil_img = Image.open(img_path).convert("RGBA")
                    ctk_img = ctk.CTkImage(pil_img, size=IMG_SIZE)
                    self._image_refs.append(ctk_img)
                    img_label = ctk.CTkLabel(img_frame, image=ctk_img, text="")
                    img_label.image = ctk_img
                    img_label.pack()
                except Exception:
                    self._placeholder(img_frame, IMG_SIZE)
            else:
                self._placeholder(img_frame, IMG_SIZE)

            # ── Caption ──
            ctk.CTkLabel(
                col, text=item["caption"],
                font=FONT_CAPTION, text_color="white",
                wraplength=280, justify="center",
            ).grid(row=2, column=0, padx=8)

        # ── Bottom: ถัดไป ──
        bottom = ctk.CTkFrame(card, fg_color="transparent")
        bottom.grid(row=3, column=0, sticky="e", padx=28, pady=(8, 20))

        self._next_button = ctk.CTkButton(
            bottom, text="ถัดไป", font=FONT_BTN,
            width=160, height=46, corner_radius=23,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="white", command=self._on_next,
        )
        self._next_button.pack()

    # ──────────────────────────────────────────────
    @staticmethod
    def _placeholder(parent, size: tuple):
        """แสดงกรอบสี่เหลี่ยมแทนรูปที่หาไม่เจอ"""
        w, h = size
        ph = ctk.CTkFrame(parent, width=w, height=h,
                          corner_radius=16,
                          fg_color=("#3a3a3a", "#3a3a3a"),
                          border_width=2,
                          border_color=("#555555", "#555555"))
        ph.pack()
        ph.pack_propagate(False)
        ctk.CTkLabel(ph, text="🖼", font=("Segoe UI Emoji", 48),
                     text_color=("#666666", "#666666")).place(
            relx=0.5, rely=0.5, anchor="center")

    def on_show(self, **kwargs):
        if self._next_button is not None:
            self.after(0, self._next_button.focus_set)

    def on_hide(self, **kwargs):
        pass

    # ── Callbacks ──
    def _on_back(self):
        if self.back_command:
            self.back_command()

    def _on_next(self):
        if self.next_command:
            self.next_command()
