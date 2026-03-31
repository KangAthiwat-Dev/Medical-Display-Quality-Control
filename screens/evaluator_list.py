import os
import time
import customtkinter as ctk
from widgets.nav_bar import NavBarWidget
from widgets.side_bar import SideBarWidget


class EvaluatorListScreen(ctk.CTkFrame):
    def __init__(self, master,
                 back_command=None,
                 edit_command=None,
                 delete_command=None,
                 evaluators=None,
                 **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self.back_command   = back_command
        self.edit_command   = edit_command
        self.delete_command = delete_command
        # evaluators = [{"first": "Athiwat", "last": "Yospanya"}, ...]
        self.evaluators = evaluators or []
        self.all_evaluators = self.evaluators.copy()
        self._delete_dialog = None
        self._perf_enabled = os.environ.get("MEDICAL_PERF", "").strip() not in ("", "0", "false", "False")
        self._row_pool = []
        self._empty_row_label = None

        # กางโครงสร้างแบ่งหน้าจอเป็น 3 โซน (1. Navbar บนสุดพาดขวาง 2. Sidebar ซ้าย 3. Main Content ขวา)
        self.grid_rowconfigure(0, weight=0) # แถว 0 ล็อกความสูงพอดีตาม Navbar
        self.grid_rowconfigure(1, weight=1) # แถว 1 ยืดเต็มจออิสระ
        self.grid_columnconfigure(0, weight=0) # คอลัมน์ 0 ล็อกความกว้างตาม Sidebar
        self.grid_columnconfigure(1, weight=1) # คอลัมน์ 1 ยืดพื้นที่ที่เหลืออิสระ

        # =============== NAVBAR ===============
        self.navbar = NavBarWidget(self)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.navbar_separator = ctk.CTkFrame(self, height=1, fg_color=("#cccccc", "#333333"))
        self.navbar_separator.grid(row=0, column=0, columnspan=2, sticky="sew")

        # =============== ICON BAR ===============
        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=1, column=0, sticky="nsew")

        # =============== MAIN CONTENT ===============
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=1, sticky="nsew")

        self._build_ui()

    def _build_ui(self):
        FONT_TH      = "TH Sarabun New"
        FONT_TITLE   = (FONT_TH, 28, "bold")
        FONT_HEADER  = (FONT_TH, 20, "bold")
        FONT_ROW     = (FONT_TH, 18)
        FONT_BTN     = (FONT_TH, 20, "bold")
        FONT_ICON    = ("Segoe UI Emoji", 16)

        CARD_COLOR   = ("#2b2b2b", "#2b2b2b")
        HEADER_COLOR = ("#3a3a3a", "#3a3a3a")
        LINE_COLOR   = ("#444444", "#444444")
        GRAY_BTN     = ("#4a4a4a", "#4a4a4a")
        GRAY_HOVER   = ("#3a3a3a", "#3a3a3a")
        TEXT_WHITE   = ("white", "white")
        TEXT_GRAY    = ("#aaaaaa", "#aaaaaa")

        # ── Card ──
        card = ctk.CTkFrame(
            self.main_frame, corner_radius=16,
            fg_color=CARD_COLOR,
            border_width=2, border_color=("#3a3a3a", "#3a3a3a"),
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.88, relheight=0.88)
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        # ── Top row: back + title + search ──
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=28, pady=(22, 12))
        top.grid_columnconfigure(1, weight=1) # บังคับให้ชื่อเรื่องดันกล่องค้นหาไปชิดขวา

        ctk.CTkButton(
            top, text="↩", font=(FONT_TH, 20, "bold"),
            width=52, height=38, corner_radius=19,
            fg_color=GRAY_BTN, hover_color=GRAY_HOVER,
            text_color="white", command=self._on_back,
        ).grid(row=0, column=0, sticky="w", padx=(0, 16))

        ctk.CTkLabel(
            top, text="รายชื่อผู้ประเมิน",
            font=FONT_TITLE, text_color="white",
        ).grid(row=0, column=1, sticky="w")

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            top, placeholder_text="🔍 ค้นหาชื่อ หรือ นามสกุล...",
            font=(FONT_TH, 18), width=240, height=38,
            corner_radius=19, fg_color=("#1f1f1f", "#1f1f1f"),
            border_width=1, border_color=("#444444", "#444444"),
            text_color="white",
            textvariable=self.search_var
        )
        self.search_entry.grid(row=0, column=2, sticky="e")
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # ── Table container ──
        table_frame = ctk.CTkFrame(card, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 24))
        table_frame.grid_columnconfigure(0, weight=3)  # ชื่อ
        table_frame.grid_columnconfigure(1, weight=3)  # นามสกุล
        table_frame.grid_columnconfigure(2, weight=1)  # จัดการ

        # ── Header row ──
        header = ctk.CTkFrame(table_frame, corner_radius=10, fg_color=HEADER_COLOR)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        header.grid_columnconfigure(0, weight=3)
        header.grid_columnconfigure(1, weight=3)
        header.grid_columnconfigure(2, weight=1)

        for col, text in enumerate(["ชื่อ", "นามสกุล", "จัดการ"]):
            ctk.CTkLabel(
                header, text=text, font=FONT_HEADER,
                text_color="white", anchor="w" if col < 2 else "center",
            ).grid(row=0, column=col, padx=20, pady=12, sticky="ew")

        # ── Scrollable rows ──
        self._row_container = ctk.CTkScrollableFrame(
            table_frame, fg_color="transparent",
            scrollbar_button_color=GRAY_BTN,
        )
        self._row_container.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self._row_container.grid_columnconfigure(0, weight=3)
        self._row_container.grid_columnconfigure(1, weight=3)
        self._row_container.grid_columnconfigure(2, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        self._font_row    = FONT_ROW
        self._font_icon   = FONT_ICON
        self._line_color  = LINE_COLOR
        self._text_white  = TEXT_WHITE
        self._text_gray   = TEXT_GRAY
        self._gray_btn    = GRAY_BTN
        self._gray_hover  = GRAY_HOVER

        self._render_rows()

    def _render_rows(self):
        t0 = time.perf_counter()
        if self._empty_row_label is None:
            self._empty_row_label = ctk.CTkLabel(
                self._row_container,
                text="ยังไม่มีผู้ประเมิน",
                font=self._font_row,
                text_color=self._text_gray,
            )

        if not self.evaluators:
            self._empty_row_label.grid(row=0, column=0, columnspan=3, pady=40)
            for entry in self._row_pool:
                entry["first"].grid_remove()
                entry["last"].grid_remove()
                entry["actions"].grid_remove()
                entry["divider"].grid_remove()
            return
        else:
            self._empty_row_label.grid_remove()

        # Ensure pool size
        while len(self._row_pool) < len(self.evaluators):
            first_lbl = ctk.CTkLabel(
                self._row_container,
                text="",
                font=self._font_row,
                text_color=self._text_white,
                anchor="w",
            )
            last_lbl = ctk.CTkLabel(
                self._row_container,
                text="",
                font=self._font_row,
                text_color=self._text_white,
                anchor="w",
            )

            actions = ctk.CTkFrame(self._row_container, fg_color="transparent")
            edit_btn = ctk.CTkButton(
                actions,
                text="✏",
                font=self._font_icon,
                width=36,
                height=36,
                corner_radius=8,
                fg_color="transparent",
                hover_color=self._gray_btn,
                text_color="white",
                command=lambda: None,
            )
            del_btn = ctk.CTkButton(
                actions,
                text="🗑",
                font=self._font_icon,
                width=36,
                height=36,
                corner_radius=8,
                fg_color="transparent",
                hover_color="#5a1a1a",
                text_color="#e05a5a",
                command=lambda: None,
            )
            edit_btn.pack(side="left", padx=4)
            del_btn.pack(side="left", padx=4)

            divider = ctk.CTkFrame(self._row_container, height=1, fg_color=self._line_color)

            self._row_pool.append(
                {
                    "first": first_lbl,
                    "last": last_lbl,
                    "actions": actions,
                    "edit_btn": edit_btn,
                    "del_btn": del_btn,
                    "divider": divider,
                }
            )

        for idx, ev in enumerate(self.evaluators):
            r = idx * 2  # แยกแถวคู่เพื่อให้มีพื้นที่แทรกเส้นคั่น
            entry = self._row_pool[idx]

            entry["first"].configure(text=ev.get("first", ""))
            entry["last"].configure(text=ev.get("last", ""))

            entry["first"].grid(row=r, column=0, padx=20, pady=10, sticky="ew")
            entry["last"].grid(row=r, column=1, padx=20, pady=10, sticky="ew")
            entry["actions"].grid(row=r, column=2, padx=12, pady=6, sticky="e")

            # ป้องกันบัคเวลาเสิร์จแล้วคิวอิงสลับ
            original_idx = self.all_evaluators.index(ev)
            entry["edit_btn"].configure(command=lambda i=original_idx: self._on_edit(i))
            entry["del_btn"].configure(command=lambda i=original_idx: self._on_delete(i))

            if idx < len(self.evaluators) - 1:
                entry["divider"].grid(row=r + 1, column=0, columnspan=3, sticky="ew", padx=8, pady=4)
            else:
                entry["divider"].grid_remove()

        # Hide extra pooled rows
        for j in range(len(self.evaluators), len(self._row_pool)):
            self._row_pool[j]["first"].grid_remove()
            self._row_pool[j]["last"].grid_remove()
            self._row_pool[j]["actions"].grid_remove()
            self._row_pool[j]["divider"].grid_remove()
                
        # สั่งให้แถวสุดท้ายว่างๆ ยืดพื้นที่ออก เพื่อดันให้ก้อนรายชื่อที่เหลืองัดลอยไปชิดบนสุดตลอดเวลา
        self._row_container.grid_rowconfigure(len(self.evaluators) * 2, weight=1)

        if self._perf_enabled:
            print(
                f"[PERF] EvaluatorListScreen._render_rows rows={len(self.evaluators)} "
                f"ms={(time.perf_counter() - t0) * 1000:.1f}"
            )

    # ── Public: refresh list from outside ──
    def set_evaluators(self, evaluators: list):
        self.evaluators = evaluators
        self.all_evaluators = evaluators.copy()
        if hasattr(self, "search_var"):
            self.search_var.set("") # ล้างช่องค้นหาทิ้งทุกครั้งที่อัปเดตข้อมูลใหม่
        self._render_rows()

    def _on_search(self, event=None):
        query = self.search_var.get().strip().lower()
        if not query:
            self.evaluators = self.all_evaluators.copy()
        else:
            self.evaluators = [
                ev for ev in self.all_evaluators
                if query in ev.get("first", "").lower() or query in ev.get("last", "").lower()
            ]
        self._render_rows()

    # ── Callbacks ──
    def _on_back(self):
        if self.back_command:
            self.back_command()

    def _on_edit(self, original_idx: int):
        ev = self.all_evaluators[original_idx]
        if hasattr(self.master, "show_screen"):
            # วาร์ปไปหน้าระบุรหัสผ่านและแก้ไข แบบ Full Screen พร้อมแนบ data ของคนนี้ไปให้ด้วย
            self.master.show_screen("evaluator_edit", bypass_auth=True, evaluator_data=ev)

    def _on_delete(self, original_idx: int):
        self._open_delete_dialog(self.all_evaluators[original_idx])

    def _open_delete_dialog(self, evaluator: dict):
        self._close_delete_dialog()

        FONT_TH = "TH Sarabun New"
        dlg = ctk.CTkToplevel(self)
        self._delete_dialog = dlg
        dlg.title("")
        dlg.attributes("-topmost", True)
        dlg.resizable(False, False)
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.configure(fg_color=("#2b2b2b", "#2b2b2b"))

        width, height = 640, 560
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        dlg.geometry(f"{width}x{height}+{(sw-width)//2}+{(sh-height)//2}")

        ctk.CTkLabel(
            dlg,
            text="ยืนยันการลบผู้ประเมิน",
            font=(FONT_TH, 28, "bold"),
            text_color="white",
        ).pack(pady=(22, 8))

        ctk.CTkFrame(dlg, height=1, fg_color=("#444444", "#444444")).pack(fill="x", padx=28, pady=(0, 14))

        ctk.CTkLabel(
            dlg,
            text=f"{evaluator.get('first', '')} {evaluator.get('last', '')}",
            font=(FONT_TH, 22, "bold"),
            text_color="white",
        ).pack(anchor="w", padx=32)

        ctk.CTkLabel(
            dlg,
            text="กรอกรหัสของผู้ประเมินรายนี้ หรือใส่ username และ password ของ admin เพื่อยืนยันการลบ",
            font=(FONT_TH, 18),
            text_color=("#d0d0d0", "#d0d0d0"),
            wraplength=560,
            justify="left",
        ).pack(anchor="w", padx=32, pady=(4, 16))

        body = ctk.CTkFrame(dlg, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=32)

        def make_field(parent, label, placeholder="", show=None):
            ctk.CTkLabel(
                parent,
                text=label,
                font=(FONT_TH, 18, "bold"),
                text_color="white",
                anchor="w",
            ).pack(anchor="w", pady=(0, 4))
            entry = ctk.CTkEntry(
                parent,
                placeholder_text=placeholder,
                font=(FONT_TH, 18),
                height=40,
                corner_radius=14,
                fg_color=("#1f1f1f", "#1f1f1f"),
                border_width=1,
                border_color=("#444444", "#444444"),
                text_color="white",
                show=show,
            )
            entry.pack(fill="x", pady=(0, 12))
            return entry

        self._evaluator_password_entry = make_field(body, "รหัสผู้ประเมิน", "กรอกรหัสของผู้ประเมินรายนี้", show="•")

        ctk.CTkLabel(
            body,
            text="หรือ",
            font=(FONT_TH, 18, "bold"),
            text_color=("#aaaaaa", "#aaaaaa"),
        ).pack(pady=(2, 6))

        self._admin_username_entry = make_field(body, "Admin Username", "กรอก username ของ admin")
        self._admin_password_entry = make_field(body, "Admin Password", "กรอก password ของ admin", show="•")

        self._delete_error_label = ctk.CTkLabel(
            body,
            text="",
            font=(FONT_TH, 17),
            text_color="#ff7b7b",
            anchor="w",
        )
        self._delete_error_label.pack(fill="x", pady=(0, 10))

        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(fill="x", padx=32, pady=(0, 24))

        ctk.CTkButton(
            btns,
            text="ยกเลิก",
            font=(FONT_TH, 20, "bold"),
            width=150,
            height=44,
            corner_radius=22,
            fg_color=("#4a4a4a", "#4a4a4a"),
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color="white",
            command=self._close_delete_dialog,
        ).pack(side="left")

        ctk.CTkButton(
            btns,
            text="ลบผู้ประเมิน",
            font=(FONT_TH, 20, "bold"),
            width=170,
            height=44,
            corner_radius=22,
            fg_color="#b33a3a",
            hover_color="#982e2e",
            text_color="white",
            command=lambda: self._confirm_delete(evaluator),
        ).pack(side="right")

        dlg.protocol("WM_DELETE_WINDOW", self._close_delete_dialog)

    def _confirm_delete(self, evaluator: dict):
        if not self.delete_command:
            return

        evaluator_password = self._evaluator_password_entry.get().strip()
        admin_username = self._admin_username_entry.get().strip()
        admin_password = self._admin_password_entry.get().strip()

        if not evaluator_password and not (admin_username and admin_password):
            self._delete_error_label.configure(text="กรุณากรอกรหัสผู้ประเมิน หรือ username/password ของ admin")
            return

        error = self.delete_command(
            evaluator,
            evaluator_password=evaluator_password,
            admin_username=admin_username,
            admin_password=admin_password,
        )
        if error:
            self._delete_error_label.configure(text=error)
            return

        self._close_delete_dialog()

    def _close_delete_dialog(self):
        if self._delete_dialog and self._delete_dialog.winfo_exists():
            self._delete_dialog.grab_release()
            self._delete_dialog.destroy()
        self._delete_dialog = None
