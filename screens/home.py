import customtkinter as ctk
import os
from PIL import Image

from widgets.nav_bar import NavBarWidget
from widgets.side_bar import SideBarWidget

class HomeScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        self._guide_dialog = None
        
        # กางโครงสร้างแบ่งหน้าจอเป็น 3 โซน (1. Navbar บนสุดพาดขวาง 2. Sidebar ซ้าย 3. Main Content ขวา)
        self.grid_rowconfigure(0, weight=0) # แถว 0 ล็อกความสูงพอดีตาม Navbar
        self.grid_rowconfigure(1, weight=1) # แถว 1 ยืดเต็มจออิสระ
        self.grid_columnconfigure(0, weight=0) # คอลัมน์ 0 ล็อกความกว้างตาม Sidebar
        self.grid_columnconfigure(1, weight=1) # คอลัมน์ 1 ยืดพื้นที่ที่เหลืออิสระ

        # =============== NAVBAR ===============
        # เรียกใช้ Navbar แบบเดี่ยวๆ ได้เลย ไม่ต้องทำคลาสลูกน้องอีกแล้ว เพราะมันจัดการตัวเองเป๊ะ!
        self.navbar = NavBarWidget(self)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.navbar_separator = ctk.CTkFrame(self, height=1, fg_color=("#cccccc", "#333333"))
        self.navbar_separator.grid(row=0, column=0, columnspan=2, sticky="sew")
        
        # =============== ICON BAR ===============
        self.sidebar = SideBarWidget(self, navigate_command=self.master.show_screen)
        self.sidebar.grid(row=1, column=0, sticky="nsew") # เลื่อนลงมาแถว 1
        
        self.separator = ctk.CTkFrame(self, width=1, fg_color="transparent")
        self.separator.grid(row=1, column=0, sticky="nse") # เลื่อนลงมาแถว 1

        # =============== MAIN CONTENT ===============
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=1, sticky="nsew") # เลื่อนลงมาแถว 1
        
        # สร้าง Frame ครอบกลุ่มปุ่มทั้งหมดเอาไว้ แล้วใช้คำสั่ง .place เพื่อจัดให้อยู่กลางจอ
        self.center_wrapper = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.center_wrapper.place(relx=0.5, rely=0.5, anchor="center")
        
        # 1) รูปภาพหรือโลโก้ด้านบน
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_path = os.path.join(project_root, "assets", "logo", "logo-darkmode.png")
        
        try:
            self.original_img = Image.open(img_path)
            self.display_image = ctk.CTkImage(
                light_image=self.original_img,
                dark_image=self.original_img,
                size=(220, 190)
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
            
        # 2) กลุ่ม 3 ปุ่มตรงกลางจอ
        self.select_type_button = ctk.CTkButton(
            self.center_wrapper, 
            text="เริ่มต้นการทดสอบ",
            command=lambda: self.master.show_screen("select_type"),
            fg_color="#0078D4", 
            hover_color="#005A9E",
            font=("TH Sarabun New", 30, "bold"),
            height=62,
            width=620,
            corner_radius=6
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
            corner_radius=6
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
            corner_radius=6
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

        root = self.winfo_toplevel()
        root.update_idletasks()
        x = root.winfo_rootx() + max((root.winfo_width() - dialog_w) // 2, 0)
        y = root.winfo_rooty() + max((root.winfo_height() - dialog_h) // 2, 0)
        dialog.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")

        dialog.lift()
        dialog.focus_force()
