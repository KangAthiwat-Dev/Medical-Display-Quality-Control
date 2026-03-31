import os
import customtkinter as ctk
from PIL import Image


class SideBarWidget(ctk.CTkFrame):
    def __init__(self, master, navigate_command=None, **kwargs):
        kwargs["width"] = 96
        kwargs["corner_radius"] = 0
        kwargs["fg_color"] = "transparent"
        super().__init__(master, **kwargs)

        self.navigate_command = navigate_command
        self._tooltip_win = None
        self.grid_propagate(False)

        self._assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
            "icons",
        )

        self._panel = ctk.CTkFrame(
            self,
            width=72,
            fg_color="#1A1A1A",
            corner_radius=12,
            border_width=1,
            border_color="#303030",
        )
        self._panel.pack(anchor="n", padx=(12, 12), pady=(86, 0))

        buttons = [
            ("home-agreement_d.png", "หน้าหลัก", self.on_home_click),
            ("admin-panel_d.png", "เข้าสู่ระบบผู้ดูแล", self.on_admin_login_click),
            ("order-history_d.png", "ประวัติการทดสอบ", self.on_history_click),
            ("contact-list_d.png", "รายชื่อผู้ประเมิน", self.on_evaluator_list_click),
        ]

        for idx, (icon_name, tooltip, command) in enumerate(buttons):
            button = self._make_icon_button(icon_name, command)
            button.pack(padx=10, pady=(12 if idx == 0 else 6, 6))
            button.bind("<Enter>", lambda _e, t=tooltip, b=button: self._show_tip(b, t), add="+")
            button.bind("<Leave>", lambda _e: self._hide_tip(), add="+")

    def _load_image(self, filename, size=(24, 24)):
        path = os.path.join(self._assets_dir, filename)
        try:
            image = Image.open(path)
            return ctk.CTkImage(light_image=image, dark_image=image, size=size)
        except Exception:
            return None

    def _make_icon_button(self, icon_name, command):
        image = self._load_image(icon_name)
        button = ctk.CTkButton(
            self._panel,
            text="",
            image=image,
            width=48,
            height=48,
            corner_radius=10,
            fg_color="transparent",
            hover_color="#2C2F35",
            border_width=0,
            command=command,
        )
        button.image = image
        return button

    def _show_tip(self, widget, text: str):
        self._hide_tip()
        x = widget.winfo_rootx() + widget.winfo_width() + 8
        y = widget.winfo_rooty() + (widget.winfo_height() // 2)

        self._tooltip_win = tip = ctk.CTkToplevel(self)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f"+{x}+{y}")
        tip.attributes("-topmost", True)

        ctk.CTkLabel(
            tip,
            text=text,
            font=("TH Sarabun New", 16),
            fg_color="#121212",
            text_color="#FFFFFF",
            corner_radius=6,
            padx=10,
            pady=4,
        ).pack()

    def _hide_tip(self):
        if self._tooltip_win:
            try:
                self._tooltip_win.destroy()
            except Exception:
                pass
            self._tooltip_win = None

    def on_home_click(self):
        if self.navigate_command:
            self.navigate_command("home")

    def on_admin_login_click(self):
        if self.navigate_command:
            self.navigate_command("admin_login")

    def on_history_click(self):
        if self.navigate_command:
            self.navigate_command("history_hook")

    def on_evaluator_list_click(self):
        if self.navigate_command:
            self.navigate_command("evaluator_list_hook")
