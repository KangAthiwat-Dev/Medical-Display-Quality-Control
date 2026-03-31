import os
import customtkinter as ctk
from PIL import Image

from widgets.nav_bar import NavBarWidget
from widgets.side_bar import SideBarWidget


class HomeScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        self._guide_dialog = None

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.navbar = NavBarWidget(self)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.navbar_separator = ctk.CTkFrame(self, height=1, fg_color=("#cccccc", "#333333"))
        self.navbar_separator.grid(row=0, column=0, columnspan=2, sticky="sew")

        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=1, column=0, sticky="nsew")

        self.separator = ctk.CTkFrame(self, width=1, fg_color="transparent")
        self.separator.grid(row=1, column=0, sticky="nse")

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=1, sticky="nsew")

        self.center_wrapper = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.center_wrapper.place(relx=0.5, rely=0.5, anchor="center")

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_path = os.path.join(project_root, "assets", "logo", "logo-darkmode.png")

        try:
            self.original_img = Image.open(img_path)
            self.display_image = ctk.CTkImage(
                light_image=self.original_img,
                dark_image=self.original_img,
                size=(220, 190),
            )
            self.image_label = ctk.CTkLabel(self.center_wrapper, text="", image=self.display_image)
            self.image_label.grid(row=0, column=0, columnspan=2, pady=(0, 34))
        except Exception:
            pass

        admin_icon_path = os.path.join(project_root, "assets", "icons", "admin-panel_d.png")
        history_icon_path = os.path.join(project_root, "assets", "icons", "order-history_d.png")
        admin_icon = None
        history_icon = None
        try:
            admin_img = Image.open(admin_icon_path)
            admin_icon = ctk.CTkImage(light_image=admin_img, dark_image=admin_img, size=(26, 26))
        except Exception:
            pass
        try:
            history_img = Image.open(history_icon_path)
            history_icon = ctk.CTkImage(light_image=history_img, dark_image=history_img, size=(26, 26))
        except Exception:
            pass

        self.select_type_button = ctk.CTkButton(
            self.center_wrapper,
            text="เริ่มต้นการทดสอบ",
            command=lambda: self.master.show_screen("select_type"),
            fg_color="#0078D4",
            hover_color="#005A9E",
            font=("TH Sarabun New", 30, "bold"),
            height=62,
            width=620,
            corner_radius=6,
        )
        self.select_type_button.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 18))

        self.admin_login_button = ctk.CTkButton(
            self.center_wrapper,
            text="Admin Login",
            image=admin_icon,
            compound="left",
            command=lambda: self.master.show_screen("admin_login"),
            fg_color=("#e0e0e0", "#313131"),
            hover_color=("#d0d0d0", "#444444"),
            text_color=("black", "white"),
            font=("TH Sarabun New", 25, "bold"),
            height=58,
            width=304,
            corner_radius=6,
        )
        self.admin_login_button.image = admin_icon
        self.admin_login_button.grid(row=2, column=0, sticky="ew", padx=(0, 8))

        self.history_button = ctk.CTkButton(
            self.center_wrapper,
            text="ประวัติการทดสอบ",
            image=history_icon,
            compound="left",
            command=lambda: self.master.show_screen("history_hook"),
            fg_color=("#e0e0e0", "#313131"),
            hover_color=("#d0d0d0", "#444444"),
            text_color=("black", "white"),
            font=("TH Sarabun New", 25, "bold"),
            height=58,
            width=304,
            corner_radius=6,
        )
        self.history_button.image = history_icon
        self.history_button.grid(row=2, column=1, sticky="ew", padx=(8, 0))

        guide_icon_path = os.path.join(project_root, "assets", "icons", "question_d.png")
        guide_icon = None
        try:
            guide_img = Image.open(guide_icon_path)
            guide_icon = ctk.CTkImage(light_image=guide_img, dark_image=guide_img, size=(22, 22))
        except Exception:
            pass

        self.guide_button = ctk.CTkButton(
            self.main_frame,
            text="คู่มือ",
            image=guide_icon,
            compound="left",
            command=self._show_guide_dialog,
            fg_color="transparent",
            hover_color="#2C2F35",
            text_color=("black", "white"),
            font=("TH Sarabun New", 22, "bold"),
            width=90,
            height=34,
            corner_radius=6,
        )
        self.guide_button.image = guide_icon
        self.guide_button.place(relx=0.98, rely=0.97, anchor="se")

    def _show_guide_dialog(self):
        if self._guide_dialog and self._guide_dialog.winfo_exists():
            self._guide_dialog.lift()
            self._guide_dialog.focus_force()
            return

        dialog = ctk.CTkToplevel(self)
        self._guide_dialog = dialog
        dialog.title("คู่มือ")
        dialog_w, dialog_h = 720, 520
        dialog.resizable(False, False)
        dialog.configure(fg_color="#2B2D32")
        dialog.transient(self.winfo_toplevel())
        dialog.protocol("WM_DELETE_WINDOW", self._close_guide_dialog)

        root = self.winfo_toplevel()
        root.update_idletasks()
        x = root.winfo_rootx() + max((root.winfo_width() - dialog_w) // 2, 0)
        y = root.winfo_rooty() + max((root.winfo_height() - dialog_h) // 2, 0)
        dialog.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")

        dialog.lift()
        dialog.focus_force()

        title = ctk.CTkLabel(
            dialog,
            text="คู่มือการใช้งานเบื้องต้น",
            font=("TH Sarabun New", 30, "bold"),
            text_color="white",
        )
        title.pack(anchor="w", padx=24, pady=(18, 8))

        ctk.CTkFrame(dialog, height=1, fg_color="#4A4D55").pack(fill="x", padx=24, pady=(0, 14))

        body = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        guide_text = (
            "1) เริ่มต้นการทดสอบจากปุ่ม 'เริ่มต้นการทดสอบ'\n"
            "2) ผู้ประเมินต้องเข้าสู่ระบบก่อนจึงจะเข้าถึงบางหน้าจอได้\n"
            "3) สามารถดูประวัติการทดสอบและส่งออก PDF ได้จากหน้าประวัติ\n"
            "4) หากต้องการตั้งค่าข้อมูลโรงพยาบาลหรือจัดการผู้ประเมิน ให้เข้า Admin Login\n"
            "5) ระหว่างการทดสอบสามารถใช้ปุ่มลัดและแถบควบคุมตามที่ระบบแสดงได้"
        )

        ctk.CTkLabel(
            body,
            text=guide_text,
            font=("TH Sarabun New", 22),
            text_color="#E8E8E8",
            justify="left",
            wraplength=640,
            anchor="w",
        ).pack(fill="x")

        footer = ctk.CTkFrame(dialog, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(0, 18))

        ctk.CTkButton(
            footer,
            text="ปิด",
            command=self._close_guide_dialog,
            font=("TH Sarabun New", 22, "bold"),
            width=120,
            height=42,
            corner_radius=21,
            fg_color="#1D5BBF",
            hover_color="#174FA3",
            text_color="white",
        ).pack(side="right")

    def _close_guide_dialog(self):
        if self._guide_dialog and self._guide_dialog.winfo_exists():
            try:
                self._guide_dialog.destroy()
            except Exception:
                pass
        self._guide_dialog = None

    def on_show(self, **kwargs):
        if self._guide_dialog and self._guide_dialog.winfo_exists():
            self._guide_dialog.lift()

    def on_hide(self, **kwargs):
        self._close_guide_dialog()
