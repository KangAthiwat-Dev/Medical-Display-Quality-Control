import os
from collections import OrderedDict
import tkinter as tk
import customtkinter as ctk
from PIL import ImageTk

from constants.evaluation_questions import TEST_CONFIG
from widgets.dock_bar import DockBarWidget
from widgets.seek_bar import SequenceSeekBarWidget
from constants.test_text import (
    ANSWER_NO_TEXT,
    ANSWER_REQUIRED_ERROR,
    ANSWER_YES_TEXT,
    CHANNEL_REQUIRED_ERROR,
    DISPLAY_INFO_TEMPLATE,
    DISPLAY_TYPE_LABELS,
    HELP_TEXT,
    INVISIBLE_CHANNELS_TEXT,
    INVISIBLE_NOTE_TEMPLATE,
    INVISIBLE_NOTE_WITH_TEXT_TEMPLATE,
    MARK_FAIL_BUTTON_TEMPLATE,
    NEXT_BUTTON_TEXT,
    NOTE_LABEL_TEXT,
    PAUSE_BUTTON_TEXT,
    PLAY_BUTTON_TEXT,
    PERIOD_LABELS,
    POPUP_CLOSE_TEXT,
    PREVIOUS_BUTTON_TEXT,
    REPLAY_BUTTON_TEXT,
    SEQUENCE_FAILED_EMPTY_TEXT,
    SEQUENCE_FAILED_LABEL_TEXT,
    SEQUENCE_LEVEL_TEMPLATE,
    SEQUENCE_NOT_FINISHED_ERROR,
    SEQUENCE_NOTE_TEMPLATE,
    SEQUENCE_NOTE_WITH_TEXT_TEMPLATE,
    SEQUENCE_PLAYER_HELP_TEXT,
    SEQUENCE_SHORTCUT_HELP_TEXT,
    SEQUENCE_SPEED_LABEL_TEMPLATE,
    SEQUENCE_STATUS_COMPLETED,
    SEQUENCE_STATUS_PAUSED,
    SEQUENCE_STATUS_PLAYING,
    SEQUENCE_SUMMARY_BUTTON_TEXT,
    SEQUENCE_SUMMARY_FAIL_TEMPLATE,
    SEQUENCE_SUMMARY_PASS_TEXT,
    SEEK_LABEL_TEMPLATE,
    SPEED_FAST_TEXT,
    SPEED_NORMAL_TEXT,
    SPEED_SLOW_TEXT,
    START_BUTTON_TEXT,
    SUMMARY_BUTTON_TEXT,
    UNMARK_FAIL_BUTTON_TEMPLATE,
)
from patterns.load_patterns import (
    get_frame_level,
    get_pattern_sequence_frames,
    has_pattern_sequence,
    load_pattern_image,
    load_pattern_sequence_frame,
)

SEQUENCE_SPEEDS = {
    SPEED_SLOW_TEXT: 300,
    SPEED_NORMAL_TEXT: 150,
    SPEED_FAST_TEXT: 90,
}


class TestScreen(ctk.CTkFrame):
    """หน้าจอทดสอบ QC — แสดง pattern บน Canvas + คำถามบน Toplevel"""

    def __init__(self, master, back_command=None, **kw):
        super().__init__(master, **kw)
        self.app = master
        self._back = back_command

        # state
        self._items = []
        self._idx = 0
        self._answers = {}
        self._card_win = None
        self._tk_img = None
        self._canvas_img_id = None
        self._channel_vars = {}
        self._popup_win = None     # popup สำหรับ display / help
        self._sequence_states = {}
        self._sequence_after_id = None
        self._sequence_ui = {}

        # ── Canvas สำหรับแสดง pattern ──
        self._canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)

        # ── DockBar (hover show/hide) — จัดกึ่งกลางแนวตั้ง ──
        self._dock = DockBarWidget(self, command=self._on_dock_click)
        self._dock.place(x=-60, rely=0.5, anchor="w")
        self._dock_visible = False

        self._cache_target_size = (1920, 1080)
        self._seq_cache_max_frames = self._env_int(
            "MEDICAL_CACHE_SEQ_FRAMES", 128, min_value=0, max_value=5000
        )
        self._sequence_image_cache = OrderedDict()  # (frame_path, w, h) -> ImageTk.PhotoImage
        self._pattern_cache_max = self._env_int(
            "MEDICAL_CACHE_PATTERNS", 64, min_value=0, max_value=5000
        )
        self._pattern_image_cache = OrderedDict()  # (display_type, period, item_id, w, h) -> ImageTk.PhotoImage

        # Bind hover events
        self.bind("<Motion>", self._handle_mouse_motion, add="+")
        self._canvas.bind("<Motion>", self._handle_mouse_motion, add="+")
        self._dock.bind("<Leave>", self._schedule_hide_dock)

        # bind ลูกๆ ทุกตัวใน dock ไม่ให้ trigger Leave
        self._bind_dock_children(self._dock)

        # ── Bottom sequence seek bar (hover show/hide) ──
        self._bottom_sequence_bar = SequenceSeekBarWidget(
            self,
            on_seek=self._on_bottom_seek_changed,
            on_prev=self._on_bottom_prev,
            on_play_toggle=self._on_bottom_play_toggle,
            on_replay=self._on_bottom_replay,
            on_next=self._on_bottom_next,
            on_speed_change=self._on_bottom_speed_change,
        )
        self._bottom_sequence_visible = False
        self._bottom_sequence_bar.place_forget()
        self._bottom_sequence_bar.bind("<Enter>", self._cancel_hide_bottom_sequence_bar, add="+")
        self._bottom_sequence_bar.bind("<Leave>", self._schedule_hide_bottom_sequence_bar, add="+")
 
        self.bind("<space>", self._handle_main_space_shortcut, add="+")
        self.bind("<KeyPress-m>", self._handle_main_mark_shortcut, add="+")
        self.bind("<KeyPress-M>", self._handle_main_mark_shortcut, add="+")
        self._canvas.bind("<space>", self._handle_main_space_shortcut, add="+")
        self._canvas.bind("<KeyPress-m>", self._handle_main_mark_shortcut, add="+")
        self._canvas.bind("<KeyPress-M>", self._handle_main_mark_shortcut, add="+")
        self.winfo_toplevel().bind_all("<space>", self._handle_main_space_shortcut, add="+")
        self.winfo_toplevel().bind_all("<KeyPress-m>", self._handle_main_mark_shortcut, add="+")
        self.winfo_toplevel().bind_all("<KeyPress-M>", self._handle_main_mark_shortcut, add="+")

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

    def _seq_cache_get(self, key):
        try:
            val = self._sequence_image_cache.pop(key)
        except KeyError:
            return None
        self._sequence_image_cache[key] = val
        return val

    def _seq_cache_put(self, key, value):
        if self._seq_cache_max_frames <= 0:
            return
        if key in self._sequence_image_cache:
            try:
                self._sequence_image_cache.pop(key)
            except KeyError:
                pass
        self._sequence_image_cache[key] = value
        while len(self._sequence_image_cache) > self._seq_cache_max_frames:
            self._sequence_image_cache.popitem(last=False)

    def _pattern_cache_get(self, key):
        try:
            val = self._pattern_image_cache.pop(key)
        except KeyError:
            return None
        self._pattern_image_cache[key] = val
        return val

    def _pattern_cache_put(self, key, value):
        if self._pattern_cache_max <= 0:
            return
        if key in self._pattern_image_cache:
            try:
                self._pattern_image_cache.pop(key)
            except KeyError:
                pass
        self._pattern_image_cache[key] = value
        while len(self._pattern_image_cache) > self._pattern_cache_max:
            self._pattern_image_cache.popitem(last=False)

    def _set_canvas_image(self, image_ref):
        self._tk_img = image_ref
        if self._canvas_img_id is None:
            self._canvas_img_id = self._canvas.create_image(0, 0, anchor="nw", image=image_ref)
        else:
            self._canvas.itemconfig(self._canvas_img_id, image=image_ref)

    def _bind_dock_children(self, widget):
        """Recursively bind Enter ให้ทุก child ของ dock"""
        for child in widget.winfo_children():
            child.bind("<Enter>", self._cancel_hide_dock, add="+")
            child.bind("<Leave>", self._schedule_hide_dock, add="+")
            self._bind_dock_children(child)

    def _get_active_sequence_item(self):
        if 0 <= self._idx < len(self._items):
            item = self._items[self._idx]
            if self._is_sequence_item(item):
                return item
        return None

    def _on_bottom_seek_changed(self, value):
        item = self._get_active_sequence_item()
        if item:
            self._seek_sequence_frame(item, value)

    def _on_bottom_prev(self):
        item = self._get_active_sequence_item()
        if item:
            self._move_sequence_frame(item, -1)

    def _on_bottom_next(self):
        item = self._get_active_sequence_item()
        if item:
            self._move_sequence_frame(item, 1)

    def _on_bottom_play_toggle(self):
        item = self._get_active_sequence_item()
        if item:
            self._toggle_sequence_playback(item)

    def _on_bottom_replay(self):
        item = self._get_active_sequence_item()
        if item:
            self._restart_sequence(item)

    def _on_bottom_speed_change(self, speed_label):
        item = self._get_active_sequence_item()
        if item:
            self._set_sequence_speed(item, speed_label)

    def _handle_main_space_shortcut(self, event=None):
        if not self.winfo_viewable():
            return
        item = self._get_active_sequence_item()
        if not item:
            return
        state = self._get_sequence_state(item)
        if not state["started"]:
            return
        self._toggle_sequence_playback(item)
        return "break"

    def _handle_main_mark_shortcut(self, event=None):
        if not self.winfo_viewable():
            return
        item = self._get_active_sequence_item()
        if not item:
            return
        state = self._get_sequence_state(item)
        if not state["started"]:
            return
        self._toggle_sequence_fail(item)
        return "break"

    def _handle_mouse_motion(self, event=None):
        try:
            x = event.x if event else 9999
            y = event.y if event else 9999
            screen_h = max(1, self.winfo_height())
            in_left_edge = x <= 2
            in_vertical_zone = (screen_h * 0.35) <= y <= (screen_h * 0.65)
            near_bottom_edge = y >= (screen_h - 3)

            if in_left_edge and in_vertical_zone:
                self._show_dock()
            if near_bottom_edge:
                self._show_bottom_sequence_bar()
        except Exception:
            pass

    # ── DockBar show/hide ──────────────────────────────────────────────

    def _show_dock(self, event=None):
        if not self._dock_visible:
            self._dock_visible = True
            self._dock.place(x=0, rely=0.5, anchor="w")
            self._dock.lift()

    def _schedule_hide_dock(self, event=None):
        """ตั้ง timer ซ่อน dock (ให้เวลาเมาส์ย้ายไป child)"""
        self._cancel_hide_dock()
        self._hide_dock_timer = self.after(200, self._do_hide_dock)

    def _cancel_hide_dock(self, event=None):
        """ยกเลิก timer ถ้าเมาส์ยังอยู่ใน dock"""
        if hasattr(self, "_hide_dock_timer") and self._hide_dock_timer is not None:
            try:
                self.after_cancel(self._hide_dock_timer)
            except ValueError:
                pass
            self._hide_dock_timer = None

    def _do_hide_dock(self):
        self._hide_dock_timer = None
        """เช็คตำแหน่งเมาส์แล้วซ่อนถ้าออกจาก dock จริง"""
        try:
            mx = self.winfo_pointerx() - self.winfo_rootx()
            my = self.winfo_pointery() - self.winfo_rooty()
            dock_w = self._dock.winfo_width()
            dock_y = self._dock.winfo_y()
            dock_h = self._dock.winfo_height()

            in_dock = (0 <= mx <= dock_w + 5 and
                       dock_y <= my <= dock_y + dock_h + 5)
            near_left_edge = mx <= 2 and (self.winfo_height() * 0.35) <= my <= (self.winfo_height() * 0.65)
            if not in_dock and not near_left_edge:
                self._dock_visible = False
                self._dock.place(x=-60, rely=0.5, anchor="w")
        except Exception:
            pass

    def _show_bottom_sequence_bar(self, event=None):
        item = self._get_active_sequence_item()
        if not item:
            return

        state = self._get_sequence_state(item)
        if not state["started"]:
            return

        if not self._bottom_sequence_visible:
            self._bottom_sequence_visible = True
            self._bottom_sequence_bar.place(
                relx=0.5,
                rely=1.0,
                anchor="s",
                y=-10,
                relwidth=0.72,
            )
        self._bottom_sequence_bar.lift()
        self._update_sequence_ui(item)

    def _schedule_hide_bottom_sequence_bar(self, event=None):
        self._cancel_hide_bottom_sequence_bar()
        self._bottom_sequence_hide_timer = self.after(240, self._do_hide_bottom_sequence_bar)

    def _cancel_hide_bottom_sequence_bar(self, event=None):
        if hasattr(self, "_bottom_sequence_hide_timer") and self._bottom_sequence_hide_timer is not None:
            self.after_cancel(self._bottom_sequence_hide_timer)
            self._bottom_sequence_hide_timer = None

    def _do_hide_bottom_sequence_bar(self):
        self._bottom_sequence_hide_timer = None
        try:
            item = self._get_active_sequence_item()
            if not item:
                self._hide_bottom_sequence_bar()
                return

            mx = self.winfo_pointerx() - self.winfo_rootx()
            my = self.winfo_pointery() - self.winfo_rooty()
            bar_x = self._bottom_sequence_bar.winfo_x()
            bar_y = self._bottom_sequence_bar.winfo_y()
            bar_w = self._bottom_sequence_bar.winfo_width()
            bar_h = self._bottom_sequence_bar.winfo_height()
            near_bottom_edge = my >= (self.winfo_height() - 3)
            in_bar = bar_x <= mx <= (bar_x + bar_w) and bar_y <= my <= (bar_y + bar_h + 5)
            if not in_bar and not near_bottom_edge:
                self._hide_bottom_sequence_bar()
        except Exception:
            pass

    def _hide_bottom_sequence_bar(self):
        self._bottom_sequence_visible = False
        self._bottom_sequence_bar.place_forget()

    # ── DockBar button handlers ───────────────────────────────────────

    def _on_dock_click(self, key):
        self._close_popup()
        if key == "toggle":
            self._toggle_dialog()
        elif key == "display":
            self._show_display_info()
        elif key == "help":
            self._show_help()
        elif key == "close":
            self._cancel_test_to_instructions()
        elif key == "home":
            self._cancel_test_to_home()

    def _toggle_dialog(self):
        """ซ่อน/แสดง dialog คำถาม"""
        if self._card_win and self._card_win.winfo_exists():
            if self._card_win.state() == "withdrawn":
                self._card_win.deiconify()
                self._card_win.lift()
                self._card_win.focus_force()
            else:
                self._card_win.withdraw()

    def _show_display_info(self):
        """Popup แสดงว่าทำ test อะไร"""
        session = getattr(self.app, "test_session", {})
        dtype   = session.get("display_type", "")
        period  = session.get("period", "")

        display_name = DISPLAY_TYPE_LABELS.get(dtype, dtype)
        period_name = PERIOD_LABELS.get(period, period)

        self._show_popup(
            DISPLAY_INFO_TEMPLATE.format(
                display_name=display_name,
                period_name=period_name,
                total_items=len(self._items),
                current_index=self._idx + 1,
            )
        )

    def _show_help(self):
        """Popup แสดงคำแนะนำ"""
        self._show_popup(HELP_TEXT)

    def _show_popup(self, text):
        """แสดง popup ข้อมูลชั่วคราว"""
        self._close_popup()
        self._popup_win = ctk.CTkToplevel(self)
        pw = self._popup_win
        pw.title("")
        pw.attributes("-topmost", True)
        pw.resizable(False, False)

        pw_w, pw_h = 360, 280
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        pw.geometry(f"{pw_w}x{pw_h}+{(sw-pw_w)//2}+{(sh-pw_h)//2}")
        pw.configure(fg_color="#2a2a2a")

        ctk.CTkLabel(pw, text=text,
                     font=("TH Sarabun New", 18),
                     text_color="#CCCCCC",
                     wraplength=320,
                     justify="left").pack(padx=20, pady=(20, 10), fill="both", expand=True)

        ctk.CTkButton(pw, text=POPUP_CLOSE_TEXT,
                      font=("TH Sarabun New", 18, "bold"),
                      fg_color="#4A90D9", hover_color="#3A7BC8",
                      height=38, width=80, corner_radius=16,
                      command=self._close_popup).pack(pady=(0, 15))

    def _close_popup(self):
        if self._popup_win and self._popup_win.winfo_exists():
            self._popup_win.destroy()
            self._popup_win = None

    # ═══════════════════════════════════════════════════════════════════════
    # Lifecycle
    # ═══════════════════════════════════════════════════════════════════════

    def on_show(self, **kw):
        self._stop_sequence_playback()
        session = getattr(self.app, "test_session", {})
        dtype   = session.get("display_type", "diagnostic")
        period  = session.get("period", "monthly")

        groups = TEST_CONFIG.get(dtype, {}).get(period, [])
        self._items = []
        pending_instruction = None
        for g in groups:
            if g.get("instruction_id"):
                pending_instruction = {
                    "instruction_id": g.get("instruction_id"),
                    "instruction_title": g.get("instruction_title", ""),
                    "instruction_text": g.get("instruction_text", ""),
                }
                continue
            for item in g.get("items", []):
                item_copy = dict(item)
                item_copy["group_title"] = g.get("group_title", "")
                if pending_instruction:
                    item_copy["instruction"] = dict(pending_instruction)
                    pending_instruction = None
                self._items.append(item_copy)

        self._idx = 0
        self._answers = {}
        self._sequence_states = {}
        self._sequence_ui = {}
        self._hide_bottom_sequence_bar()
        if self._canvas_img_id is not None:
            try:
                self._canvas.delete(self._canvas_img_id)
            except Exception:
                self._canvas.delete("all")
        self._canvas_img_id = None
        self.after_idle(self.focus_set)
        self.after_idle(self._canvas.focus_set)
        self.after_idle(self._load_current_item)

    def on_hide(self, **kw):
        self._stop_sequence_playback()
        if self._card_win and self._card_win.winfo_exists():
            self._card_win.withdraw()
        self._close_popup()
        self._hide_bottom_sequence_bar()

    def _get_test_context(self):
        session = getattr(self.app, "test_session", {})
        return (
            session.get("display_type", "diagnostic"),
            session.get("period", "monthly"),
        )

    def _is_sequence_item(self, item) -> bool:
        display_type, period = self._get_test_context()
        return has_pattern_sequence(display_type, period, item["item_id"])

    def _get_sequence_state(self, item):
        item_id = item["item_id"]
        if item_id not in self._sequence_states:
            display_type, period = self._get_test_context()
            frame_paths = get_pattern_sequence_frames(display_type, period, item_id)
            self._sequence_states[item_id] = {
                "started": False,
                "playing": False,
                "completed": False,
                "current_index": 0,
                "frame_paths": frame_paths,
                "failed_levels": set(),
                "speed_label": SPEED_NORMAL_TEXT,
                "speed_ms": SEQUENCE_SPEEDS[SPEED_NORMAL_TEXT],
                "updating_seek": False,
            }
        return self._sequence_states[item_id]

    def _stop_sequence_playback(self):
        if self._sequence_after_id is not None:
            self.after_cancel(self._sequence_after_id)
            self._sequence_after_id = None

        for state in self._sequence_states.values():
            state["playing"] = False

    def _refresh_sequence_canvas(self, item):
        state = self._get_sequence_state(item)
        frame_path = state["frame_paths"][state["current_index"]]

        self.update_idletasks()
        cw = self._canvas.winfo_width() or self._cache_target_size[0]
        ch = self._canvas.winfo_height() or self._cache_target_size[1]

        cache_key = (frame_path, cw, ch)
        cached = self._seq_cache_get(cache_key)
        if cached is None:
            pil_img = load_pattern_sequence_frame(frame_path, cw, ch)
            cached = ImageTk.PhotoImage(pil_img)
            self._seq_cache_put(cache_key, cached)

        self._set_canvas_image(cached)

    def _get_current_sequence_level(self, item) -> str:
        state = self._get_sequence_state(item)
        return get_frame_level(state["frame_paths"][state["current_index"]])

    def _format_failed_levels(self, failed_levels) -> str:
        return ", ".join(sorted(failed_levels, key=int))

    def _update_sequence_ui(self, item):
        if not self._sequence_ui and not self._get_active_sequence_item():
            return

        state = self._get_sequence_state(item)
        current_level = self._get_current_sequence_level(item)
        failed_levels = self._format_failed_levels(state["failed_levels"])
        current_mark_status = (
            f"ค่าปัจจุบัน {current_level} ไม่ผ่าน"
            if current_level in state["failed_levels"]
            else ""
        )

        if "level_label" in self._sequence_ui:
            self._sequence_ui["level_label"].configure(
                text=SEQUENCE_LEVEL_TEMPLATE.format(level=current_level)
            )

        if state["completed"]:
            status_text = SEQUENCE_STATUS_COMPLETED
        elif state["playing"]:
            status_text = SEQUENCE_STATUS_PLAYING
        else:
            status_text = SEQUENCE_STATUS_PAUSED
        if "status_label" in self._sequence_ui:
            self._sequence_ui["status_label"].configure(text=status_text)

        mark_text = (
            UNMARK_FAIL_BUTTON_TEMPLATE.format(level=current_level)
            if current_level in state["failed_levels"]
            else MARK_FAIL_BUTTON_TEMPLATE.format(level=current_level)
        )
        if "mark_button" in self._sequence_ui:
            self._sequence_ui["mark_button"].configure(text=mark_text)

        play_text = PAUSE_BUTTON_TEXT if state["playing"] else PLAY_BUTTON_TEXT
        if "play_button" in self._sequence_ui:
            self._sequence_ui["play_button"].configure(text=play_text)

        if "seek_label" in self._sequence_ui:
            self._sequence_ui["seek_label"].configure(
                text=SEEK_LABEL_TEMPLATE.format(
                    current=state["current_index"] + 1,
                    total=len(state["frame_paths"]),
                )
            )

        if "speed_label" in self._sequence_ui:
            self._sequence_ui["speed_label"].configure(
                text=SEQUENCE_SPEED_LABEL_TEMPLATE.format(speed=state["speed_label"])
            )

        if "seek_slider" in self._sequence_ui:
            state["updating_seek"] = True
            self._sequence_ui["seek_slider"].set(state["current_index"])
            state["updating_seek"] = False

        if "speed_control" in self._sequence_ui:
            self._sequence_ui["speed_control"].set(state["speed_label"])

        failed_text = failed_levels if failed_levels else SEQUENCE_FAILED_EMPTY_TEXT
        if "failed_values_label" in self._sequence_ui:
            self._sequence_ui["failed_values_label"].configure(text=failed_text)

        summary_text = (
            SEQUENCE_SUMMARY_FAIL_TEMPLATE.format(levels=failed_levels)
            if failed_levels
            else SEQUENCE_SUMMARY_PASS_TEXT
        )
        if "summary_label" in self._sequence_ui:
            self._sequence_ui["summary_label"].configure(text=summary_text)

        if state["completed"] and "summary_button" in self._sequence_ui:
            self._sequence_ui["summary_button"].pack(side="right", padx=(10, 20), pady=10)
        elif "summary_button" in self._sequence_ui:
            self._sequence_ui["summary_button"].pack_forget()

        if state["started"]:
            state["updating_seek"] = True
            self._bottom_sequence_bar.update_state(
                current=state["current_index"] + 1,
                total=len(state["frame_paths"]),
                speed_label=state["speed_label"],
                playing=state["playing"],
                slider_to=max(len(state["frame_paths"]) - 1, 0),
                slider_steps=max(len(state["frame_paths"]) - 1, 1),
                mark_status_text=current_mark_status,
            )
            state["updating_seek"] = False

    def _step_sequence_forward(self, item_id: str):
        self._sequence_after_id = None

        if self._idx >= len(self._items):
            return

        item = self._items[self._idx]
        if item["item_id"] != item_id:
            return

        state = self._get_sequence_state(item)
        if not state["playing"]:
            return

        last_index = len(state["frame_paths"]) - 1
        if state["current_index"] >= last_index:
            state["playing"] = False
            state["completed"] = True
            self._update_sequence_ui(item)
            return

        state["current_index"] += 1
        if state["current_index"] >= last_index:
            state["completed"] = True

        self._refresh_sequence_canvas(item)
        self._update_sequence_ui(item)

        if state["current_index"] >= last_index:
            state["playing"] = False
            state["completed"] = True
            self._update_sequence_ui(item)
            return

        self._sequence_after_id = self.after(
            state["speed_ms"], lambda: self._step_sequence_forward(item_id)
        )

    def _start_sequence_playback(self, item):
        self._stop_sequence_playback()
        state = self._get_sequence_state(item)
        state["started"] = True
        state["completed"] = False
        state["playing"] = True
        self._show_sequence_question(item)
        self._refresh_sequence_canvas(item)
        self._update_sequence_ui(item)
        self._sequence_after_id = self.after(
            state["speed_ms"], lambda: self._step_sequence_forward(item["item_id"])
        )

    def _toggle_sequence_playback(self, item):
        state = self._get_sequence_state(item)
        if state["playing"]:
            self._stop_sequence_playback()
        else:
            if state["current_index"] >= len(state["frame_paths"]) - 1:
                state["completed"] = True
            else:
                self._stop_sequence_playback()
                state["playing"] = True
                self._sequence_after_id = self.after(
                    state["speed_ms"], lambda: self._step_sequence_forward(item["item_id"])
                )
        self._update_sequence_ui(item)

    def _move_sequence_frame(self, item, step: int):
        state = self._get_sequence_state(item)
        self._stop_sequence_playback()
        next_index = min(max(state["current_index"] + step, 0), len(state["frame_paths"]) - 1)
        state["current_index"] = next_index
        if next_index >= len(state["frame_paths"]) - 1:
            state["completed"] = True
        self._refresh_sequence_canvas(item)
        self._update_sequence_ui(item)

    def _toggle_sequence_fail(self, item):
        state = self._get_sequence_state(item)
        self._stop_sequence_playback()
        current_level = self._get_current_sequence_level(item)

        if current_level in state["failed_levels"]:
            state["failed_levels"].remove(current_level)
        else:
            state["failed_levels"].add(current_level)

        self._update_sequence_ui(item)

    def _seek_sequence_frame(self, item, value):
        state = self._get_sequence_state(item)
        if state.get("updating_seek"):
            return

        self._stop_sequence_playback()
        target_index = int(round(float(value)))
        target_index = min(max(target_index, 0), len(state["frame_paths"]) - 1)
        state["current_index"] = target_index
        state["completed"] = target_index >= len(state["frame_paths"]) - 1
        self._refresh_sequence_canvas(item)
        self._update_sequence_ui(item)

    def _restart_sequence(self, item):
        state = self._get_sequence_state(item)
        self._stop_sequence_playback()
        state["current_index"] = 0
        state["completed"] = False
        state["playing"] = True
        self._refresh_sequence_canvas(item)
        self._update_sequence_ui(item)
        self._sequence_after_id = self.after(
            state["speed_ms"], lambda: self._step_sequence_forward(item["item_id"])
        )

    def _set_sequence_speed(self, item, speed_label: str):
        state = self._get_sequence_state(item)
        if speed_label not in SEQUENCE_SPEEDS:
            return

        state["speed_label"] = speed_label
        state["speed_ms"] = SEQUENCE_SPEEDS[speed_label]
        self._update_sequence_ui(item)

        if state["playing"]:
            self._stop_sequence_playback()
            state["playing"] = True
            self._sequence_after_id = self.after(
                state["speed_ms"], lambda: self._step_sequence_forward(item["item_id"])
            )

    def _bind_sequence_shortcuts(self, item):
        if self._card_win is None or not self._card_win.winfo_exists():
            return

        self._card_win.bind(
            "<space>",
            lambda _e: (self._toggle_sequence_playback(item), "break")[1],
        )
        self._card_win.bind(
            "<KeyPress-m>",
            lambda _e: (self._toggle_sequence_fail(item), "break")[1],
        )
        self._card_win.bind(
            "<KeyPress-M>",
            lambda _e: (self._toggle_sequence_fail(item), "break")[1],
        )

    def _submit_sequence_summary(self, item):
        state = self._get_sequence_state(item)
        if not state["completed"]:
            if self._sequence_ui:
                self._sequence_ui["error_label"].configure(text=SEQUENCE_NOT_FINISHED_ERROR)
            return

        failed_levels = sorted(state["failed_levels"], key=int)
        answer = {
            "result": "fail" if failed_levels else "pass",
            "note": "",
            "failed_levels": failed_levels,
        }

        self._answers[item["item_id"]] = answer
        print(f"  → [{item['item_id']}] = {answer}")

        self._idx += 1
        self._load_current_item()

    # ═══════════════════════════════════════════════════════════════════════
    # Pattern display
    # ═══════════════════════════════════════════════════════════════════════

    def _load_current_item(self):
        if self._idx >= len(self._items):
            self._finish_test()
            return

        item = self._items[self._idx]
        self._stop_sequence_playback()

        if self._is_sequence_item(item):
            self._refresh_sequence_canvas(item)
            state = self._get_sequence_state(item)
            if state["started"]:
                self._update_sequence_ui(item)
            else:
                self._hide_bottom_sequence_bar()
        else:
            self._hide_bottom_sequence_bar()
            session = getattr(self.app, "test_session", {})

            self.update_idletasks()
            cw = self._canvas.winfo_width()  or 1920
            ch = self._canvas.winfo_height() or 1080

            display_type = session.get("display_type", "diagnostic")
            period = session.get("period", "monthly")
            cache_key = (display_type, period, item["item_id"], cw, ch)
            cached = self._pattern_cache_get(cache_key)
            if cached is None:
                pil_img = load_pattern_image(
                    display_type=display_type,
                    period=period,
                    item_id=item["item_id"],
                    width=cw,
                    height=ch,
                )
                cached = ImageTk.PhotoImage(pil_img)
                self._pattern_cache_put(cache_key, cached)

            self._set_canvas_image(cached)

        self._show_question(item)

    # ═══════════════════════════════════════════════════════════════════════
    # Question card (Toplevel)
    # ═══════════════════════════════════════════════════════════════════════

    def _show_question(self, item):
        if self._is_sequence_item(item):
            self._show_sequence_question(item)
            return

        self._sequence_ui = {}
        self._hide_bottom_sequence_bar()
        if self._card_win is None or not self._card_win.winfo_exists():
            self._build_card_window()

        win = self._card_win

        # Clear
        for w in self._body_frame.winfo_children():
            w.destroy()
        for w in self._footer_frame.winfo_children():
            w.destroy()

        # Reset state — ไม่ default เลือกอะไร
        self._answer_var = ctk.StringVar(value="")
        self._note_var = ctk.StringVar(value="")
        self._channel_vars = {}
        self._error_label = None

        # ── Restore previous answer ──
        prev_ans = self._answers.get(item.get("item_id"))
        if prev_ans:
            self._answer_var.set("yes" if prev_ans.get("result") == "pass" else "no")
            self._note_var.set(prev_ans.get("note", ""))

        # ═══ Body ═══

        # ── Title row: ชื่อ (blue) + badge + ปุ่มปิด ──
        title_row = ctk.CTkFrame(self._body_frame, fg_color="transparent")
        title_row.pack(fill="x", padx=15, pady=(12, 5))

        title_text = item.get("title", "")
        if ")" in title_text:
            title_display = title_text.split(")", 1)[-1].strip()
        else:
            title_display = title_text

        ctk.CTkLabel(title_row, text=title_display,
                     font=("TH Sarabun New", 22, "bold"),
                     text_color="#4A90D9",
                     wraplength=380,
                     justify="left").pack(side="left", fill="x", expand=True)

        # Badge
        counter = f"{self._idx + 1}/{len(self._items)}"
        ctk.CTkLabel(title_row, text=counter,
                     font=("TH Sarabun New", 16, "bold"),
                     fg_color="#4A90D9", text_color="white",
                     corner_radius=14, width=50, height=30).pack(side="right", padx=(5, 0))

        # ปุ่มซ่อน dialog (─)
        ctk.CTkButton(title_row, text="─",
                      font=("TH Sarabun New", 16, "bold"),
                      width=30, height=30, corner_radius=15,
                      fg_color="#555555", hover_color="#777777",
                      text_color="white",
                      command=self._toggle_dialog
                      ).pack(side="right", padx=(5, 0))

        # ── เกณฑ์ ──
        criterion = item.get("pass_criterion", "")
        if criterion:
            item_num = title_text.split(")")[0] + ")" if ")" in title_text else ""
            display_criterion = f"{item_num} {criterion}" if item_num else criterion
            ctk.CTkLabel(self._body_frame, text=display_criterion,
                         font=("TH Sarabun New", 17),
                         text_color="#CCCCCC",
                         wraplength=480,
                         justify="center").pack(padx=20, pady=(0, 10))

        # ── Radio: ใช่ / ไม่ใช่ ──
        radio_frame = ctk.CTkFrame(self._body_frame, fg_color="transparent")
        radio_frame.pack(pady=(5, 10))

        ctk.CTkRadioButton(radio_frame, text=ANSWER_YES_TEXT,
                           font=("TH Sarabun New", 20),
                           variable=self._answer_var, value="yes",
                           text_color="#CCCCCC",
                           fg_color="#4A90D9",
                           hover_color="#3A7BC8",
                           command=lambda: self._on_answer_change(item)
                           ).pack(side="left", padx=(0, 40))

        ctk.CTkRadioButton(radio_frame, text=ANSWER_NO_TEXT,
                           font=("TH Sarabun New", 20),
                           variable=self._answer_var, value="no",
                           text_color="#CCCCCC",
                           fg_color="#4A90D9",
                           hover_color="#3A7BC8",
                           command=lambda: self._on_answer_change(item)
                           ).pack(side="left")

        # ── Channel checkboxes container (ซ่อนไว้ก่อน) ──
        total_ch = item.get("total_channels", 0)
        self._channels_container = ctk.CTkFrame(self._body_frame, fg_color="transparent")
        if total_ch > 0:
            self._build_channel_checkboxes(self._channels_container, total_ch, prev_ans)

        # ── หมายเหตุ ──
        self._note_frame = ctk.CTkFrame(self._body_frame, fg_color="transparent")
        self._note_frame.pack(fill="x", padx=20, pady=(5, 5))

        ctk.CTkLabel(self._note_frame, text=NOTE_LABEL_TEXT,
                     font=("TH Sarabun New", 17),
                     text_color="#AAAAAA").pack(side="left", padx=(0, 10))

        ctk.CTkEntry(self._note_frame,
                     textvariable=self._note_var,
                     font=("TH Sarabun New", 16),
                     height=35,
                     fg_color="#3a3a3a",
                     border_color="#555555",
                     text_color="white").pack(side="left", expand=True, fill="x")

        # ── Error label (ซ่อนไว้ก่อน) ──
        self._error_label = ctk.CTkLabel(self._body_frame, text="",
                                          font=("TH Sarabun New", 16),
                                          text_color="#FF5555")
        self._error_label.pack(pady=(2, 0))

        # Show checkboxes if previous answer was "no"
        self._on_answer_change(item)

        # ═══ Footer ═══

        btn_text = NEXT_BUTTON_TEXT if self._idx < len(self._items) - 1 else SUMMARY_BUTTON_TEXT
        ctk.CTkButton(self._footer_frame, text=btn_text,
                      font=("TH Sarabun New", 20, "bold"),
                      fg_color="#4A90D9", hover_color="#3A7BC8",
                      height=42, width=120, corner_radius=20,
                      command=lambda: self._try_submit(item)
                      ).pack(side="right", padx=(10, 20), pady=10)

        if self._idx > 0:
            ctk.CTkButton(self._footer_frame, text=PREVIOUS_BUTTON_TEXT,
                          font=("TH Sarabun New", 20, "bold"),
                          fg_color="transparent",
                          hover_color="#3a3a3a",
                          border_width=2,
                          border_color="#888888",
                          text_color="#CCCCCC",
                          height=42, width=120, corner_radius=20,
                          command=self._go_previous
                          ).pack(side="right", pady=10)

        win.deiconify()
        win.lift()
        win.focus_force()

    def _show_sequence_question(self, item):
        if self._card_win is None or not self._card_win.winfo_exists():
            self._build_card_window()

        win = self._card_win
        for w in self._body_frame.winfo_children():
            w.destroy()
        for w in self._footer_frame.winfo_children():
            w.destroy()

        self._sequence_ui = {}
        state = self._get_sequence_state(item)

        title_row = ctk.CTkFrame(self._body_frame, fg_color="transparent")
        title_row.pack(fill="x", padx=15, pady=(12, 5))

        title_text = item.get("title", "")
        if ")" in title_text:
            title_display = title_text.split(")", 1)[-1].strip()
        else:
            title_display = title_text

        ctk.CTkLabel(
            title_row,
            text=title_display,
            font=("TH Sarabun New", 22, "bold"),
            text_color="#4A90D9",
            wraplength=380,
            justify="left",
        ).pack(side="left", fill="x", expand=True)

        counter = f"{self._idx + 1}/{len(self._items)}"
        ctk.CTkLabel(
            title_row,
            text=counter,
            font=("TH Sarabun New", 16, "bold"),
            fg_color="#4A90D9",
            text_color="white",
            corner_radius=14,
            width=50,
            height=30,
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            title_row,
            text="─",
            font=("TH Sarabun New", 16, "bold"),
            width=30,
            height=30,
            corner_radius=15,
            fg_color="#555555",
            hover_color="#777777",
            text_color="white",
            command=self._toggle_dialog,
        ).pack(side="right", padx=(5, 0))

        criterion = item.get("pass_criterion", "")
        if criterion:
            item_num = title_text.split(")")[0] + ")" if ")" in title_text else ""
            display_criterion = f"{item_num} {criterion}" if item_num else criterion
            ctk.CTkLabel(
                self._body_frame,
                text=display_criterion,
                font=("TH Sarabun New", 17),
                text_color="#CCCCCC",
                wraplength=480,
                justify="center",
            ).pack(padx=20, pady=(0, 10))

        if not state["started"]:
            instruction = item.get("instruction", {})
            instruction_title = instruction.get("instruction_title") or title_display
            instruction_text = instruction.get("instruction_text") or SEQUENCE_PLAYER_HELP_TEXT

            ctk.CTkLabel(
                self._body_frame,
                text=instruction_title,
                font=("TH Sarabun New", 26, "bold"),
                text_color="#F2F2F2",
                wraplength=480,
                justify="left",
            ).pack(anchor="w", padx=20, pady=(10, 12))

            ctk.CTkLabel(
                self._body_frame,
                text=instruction_text,
                font=("TH Sarabun New", 18),
                text_color="#D5D5D5",
                wraplength=480,
                justify="left",
            ).pack(anchor="w", padx=20, pady=(0, 16))

            error_label = ctk.CTkLabel(
                self._body_frame,
                text="",
                font=("TH Sarabun New", 16),
                text_color="#FF5555",
            )
            error_label.pack(pady=(4, 0))

            self._sequence_ui["error_label"] = error_label

            ctk.CTkButton(
                self._footer_frame,
                text=START_BUTTON_TEXT,
                font=("TH Sarabun New", 20, "bold"),
                fg_color="#4A90D9",
                hover_color="#3A7BC8",
                height=42,
                width=120,
                corner_radius=20,
                command=lambda: self._start_sequence_playback(item),
            ).pack(side="right", padx=(10, 20), pady=10)

            if self._idx > 0:
                ctk.CTkButton(
                    self._footer_frame,
                    text=PREVIOUS_BUTTON_TEXT,
                    font=("TH Sarabun New", 20, "bold"),
                    fg_color="transparent",
                    hover_color="#3a3a3a",
                    border_width=2,
                    border_color="#888888",
                    text_color="#CCCCCC",
                    height=42,
                    width=120,
                    corner_radius=20,
                    command=self._go_previous,
                ).pack(side="right", pady=10)
        else:
            help_label = ctk.CTkLabel(
                self._body_frame,
                text=SEQUENCE_PLAYER_HELP_TEXT,
                font=("TH Sarabun New", 16),
                text_color="#BBBBBB",
                wraplength=480,
                justify="center",
            )
            help_label.pack(padx=20, pady=(0, 8))

            shortcut_label = ctk.CTkLabel(
                self._body_frame,
                text=SEQUENCE_SHORTCUT_HELP_TEXT,
                font=("TH Sarabun New", 15),
                text_color="#9A9A9A",
                wraplength=480,
                justify="center",
            )
            shortcut_label.pack(padx=20, pady=(0, 8))

            level_label = ctk.CTkLabel(
                self._body_frame,
                text="",
                font=("TH Sarabun New", 22, "bold"),
                text_color="#F2F2F2",
            )
            level_label.pack(pady=(6, 2))

            status_label = ctk.CTkLabel(
                self._body_frame,
                text="",
                font=("TH Sarabun New", 17),
                text_color="#AAAAAA",
            )
            status_label.pack(pady=(0, 12))

            seek_label = ctk.CTkLabel(
                self._body_frame,
                text="",
                font=("TH Sarabun New", 16, "bold"),
                text_color="#CCCCCC",
            )
            seek_label.pack(padx=20, pady=(0, 4))

            seek_slider = ctk.CTkSlider(
                self._body_frame,
                from_=0,
                to=max(len(state["frame_paths"]) - 1, 0),
                number_of_steps=max(len(state["frame_paths"]) - 1, 1),
                command=lambda value: self._seek_sequence_frame(item, value),
            )
            seek_slider.pack(fill="x", padx=20, pady=(0, 12))

            speed_row = ctk.CTkFrame(self._body_frame, fg_color="transparent")
            speed_row.pack(fill="x", padx=20, pady=(0, 12))

            speed_label = ctk.CTkLabel(
                speed_row,
                text="",
                font=("TH Sarabun New", 16, "bold"),
                text_color="#CCCCCC",
            )
            speed_label.pack(side="left")

            speed_control = ctk.CTkSegmentedButton(
                speed_row,
                values=[SPEED_SLOW_TEXT, SPEED_NORMAL_TEXT, SPEED_FAST_TEXT],
                font=("TH Sarabun New", 15, "bold"),
                command=lambda selected: self._set_sequence_speed(item, selected),
            )
            speed_control.pack(side="right")

            controls = ctk.CTkFrame(self._body_frame, fg_color="transparent")
            controls.pack(pady=(0, 12))

            ctk.CTkButton(
                controls,
                text=PREVIOUS_BUTTON_TEXT,
                font=("TH Sarabun New", 18, "bold"),
                fg_color="#555555",
                hover_color="#666666",
                width=100,
                height=38,
                command=lambda: self._move_sequence_frame(item, -1),
            ).pack(side="left", padx=5)

            play_button = ctk.CTkButton(
                controls,
                text="",
                font=("TH Sarabun New", 18, "bold"),
                fg_color="#4A90D9",
                hover_color="#3A7BC8",
                width=100,
                height=38,
                command=lambda: self._toggle_sequence_playback(item),
            )
            play_button.pack(side="left", padx=5)

            ctk.CTkButton(
                controls,
                text=REPLAY_BUTTON_TEXT,
                font=("TH Sarabun New", 18, "bold"),
                fg_color="#666666",
                hover_color="#777777",
                width=100,
                height=38,
                command=lambda: self._restart_sequence(item),
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                controls,
                text=NEXT_BUTTON_TEXT,
                font=("TH Sarabun New", 18, "bold"),
                fg_color="#555555",
                hover_color="#666666",
                width=100,
                height=38,
                command=lambda: self._move_sequence_frame(item, 1),
            ).pack(side="left", padx=5)

            mark_button = ctk.CTkButton(
                self._body_frame,
                text="",
                font=("TH Sarabun New", 18, "bold"),
                fg_color="#B5544E",
                hover_color="#9E4640",
                height=40,
                corner_radius=18,
                command=lambda: self._toggle_sequence_fail(item),
            )
            mark_button.pack(fill="x", padx=20, pady=(0, 12))

            ctk.CTkLabel(
                self._body_frame,
                text=SEQUENCE_FAILED_LABEL_TEXT,
                font=("TH Sarabun New", 17, "bold"),
                text_color="#DDDDDD",
            ).pack(anchor="w", padx=20)

            failed_values_label = ctk.CTkLabel(
                self._body_frame,
                text="",
                font=("TH Sarabun New", 17),
                text_color="#CCCCCC",
                wraplength=480,
                justify="left",
            )
            failed_values_label.pack(anchor="w", padx=20, pady=(0, 12))

            summary_label = ctk.CTkLabel(
                self._body_frame,
                text="",
                font=("TH Sarabun New", 18, "bold"),
                text_color="#F2F2F2",
                wraplength=480,
                justify="left",
            )
            summary_label.pack(anchor="w", padx=20, pady=(0, 8))

            error_label = ctk.CTkLabel(
                self._body_frame,
                text="",
                font=("TH Sarabun New", 16),
                text_color="#FF5555",
            )
            error_label.pack(anchor="w", padx=20, pady=(0, 4))

            summary_button = ctk.CTkButton(
                self._footer_frame,
                text=SEQUENCE_SUMMARY_BUTTON_TEXT,
                font=("TH Sarabun New", 20, "bold"),
                fg_color="#4A90D9",
                hover_color="#3A7BC8",
                height=42,
                width=120,
                corner_radius=20,
                command=lambda: self._submit_sequence_summary(item),
            )

            self._sequence_ui = {
                "level_label": level_label,
                "status_label": status_label,
                "seek_label": seek_label,
                "seek_slider": seek_slider,
                "speed_label": speed_label,
                "speed_control": speed_control,
                "play_button": play_button,
                "mark_button": mark_button,
                "failed_values_label": failed_values_label,
                "summary_label": summary_label,
                "summary_button": summary_button,
                "error_label": error_label,
            }
            self._bind_sequence_shortcuts(item)
            self._update_sequence_ui(item)

            if self._idx > 0:
                ctk.CTkButton(
                    self._footer_frame,
                    text=PREVIOUS_BUTTON_TEXT,
                    font=("TH Sarabun New", 20, "bold"),
                    fg_color="transparent",
                    hover_color="#3a3a3a",
                    border_width=2,
                    border_color="#888888",
                    text_color="#CCCCCC",
                    height=42,
                    width=120,
                    corner_radius=20,
                    command=self._go_previous,
                ).pack(side="right", pady=10)

        win.deiconify()
        win.lift()
        win.focus_force()

    def _build_channel_checkboxes(self, container, total, prev_ans=None):
        """สร้าง checkboxes 1-N"""
        ctk.CTkLabel(container, text=INVISIBLE_CHANNELS_TEXT,
                     font=("TH Sarabun New", 17, "bold"),
                     text_color="#AAAAAA").pack(anchor="w", padx=5, pady=(5, 5))

        prev_channels = set()
        if prev_ans and "invisible_channels" in prev_ans:
            prev_channels = set(prev_ans["invisible_channels"])

        cols = 9
        row_frame = None
        for i in range(1, total + 1):
            if (i - 1) % cols == 0:
                row_frame = ctk.CTkFrame(container, fg_color="transparent")
                row_frame.pack(fill="x", padx=5, pady=1)

            var = ctk.BooleanVar(value=(i in prev_channels))
            self._channel_vars[i] = var

            ctk.CTkCheckBox(row_frame, text=str(i),
                            font=("TH Sarabun New", 15),
                            variable=var,
                            width=45, height=28,
                            checkbox_width=20, checkbox_height=20,
                            fg_color="#666666",
                            hover_color="#888888",
                            text_color="#CCCCCC",
                            corner_radius=4).pack(side="left", padx=2)

    def _on_answer_change(self, item=None):
        """เมื่อเปลี่ยน radio → show/hide checkboxes"""
        if self._error_label:
            self._error_label.configure(text="")

        if self._answer_var.get() == "no" and self._channel_vars:
            # แทรก checkboxes ก่อน note_frame
            self._channels_container.pack(fill="x", padx=20, pady=(0, 5),
                                          before=self._note_frame)
        else:
            self._channels_container.pack_forget()

    def _build_card_window(self):
        """สร้าง Toplevel สำหรับคำถาม"""
        self._card_win = ctk.CTkToplevel(self)
        win = self._card_win
        win.title("")
        win.attributes("-topmost", True)
        win.resizable(False, False)

        card_w, card_h = 540, 440
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - card_w) // 2
        y = (sh - card_h) // 2
        win.geometry(f"{card_w}x{card_h}+{x}+{y}")
        win.configure(fg_color="#2a2a2a")

        win.protocol("WM_DELETE_WINDOW", lambda: None)

        # Body (scrollable)
        self._body_frame = ctk.CTkScrollableFrame(win, fg_color="transparent")
        self._body_frame.pack(fill="both", expand=True)

        # Footer
        self._footer_frame = ctk.CTkFrame(win, fg_color="transparent", height=60)
        self._footer_frame.pack(fill="x")
        self._footer_frame.pack_propagate(False)

        win.lift()
        win.focus_force()

    # ═══════════════════════════════════════════════════════════════════════
    # Validation + Submit
    # ═══════════════════════════════════════════════════════════════════════

    def _try_submit(self, item):
        """ตรวจสอบก่อน submit"""
        ans = self._answer_var.get()

        # ต้องเลือก radio ก่อน
        if ans == "":
            self._error_label.configure(text=ANSWER_REQUIRED_ERROR)
            return

        # ถ้าเลือก "ไม่ใช่" + มี channels → ต้องเลือกอย่างน้อย 1 ช่อง
        if ans == "no" and self._channel_vars:
            checked = [ch for ch, var in self._channel_vars.items() if var.get()]
            if not checked:
                self._error_label.configure(text=CHANNEL_REQUIRED_ERROR)
                return

        self._submit_from_dialog(item)

    def _submit_from_dialog(self, item):
        """บันทึกคำตอบ"""
        ans_val = self._answer_var.get()
        result = "pass" if ans_val == "yes" else "fail"
        answer = {
            "result": result,
            "note":   self._note_var.get(),
        }

        if ans_val == "no" and self._channel_vars:
            invisible = [ch for ch, var in self._channel_vars.items() if var.get()]
            answer["invisible_channels"] = invisible

        self._answers[item["item_id"]] = answer
        print(f"  → [{item['item_id']}] = {answer}")

        self._idx += 1
        self._load_current_item()

    def _go_previous(self):
        if self._idx > 0:
            self._stop_sequence_playback()
            self._idx -= 1
            self._load_current_item()

    def _finish_test(self):
        self._stop_sequence_playback()
        print("\n═══ สรุปผลการทดสอบ ═══")
        for iid, ans in self._answers.items():
            print(f"  {iid}: {ans}")
        print("═══════════════════════\n")

        if hasattr(self.app, "test_session"):
            self.app.test_session["answers"] = self._answers

        if self._card_win and self._card_win.winfo_exists():
            self._card_win.destroy()
            self._card_win = None

        self._close_popup()

        # สร้าง results data สำหรับ research_results screen
        results_data = self._build_results_data()
        
        # ดึงข้อมูล metadata
        from services.session import get_session
        from database.database import get_settings
        from datetime import datetime
        
        session = getattr(self.app, "test_session", {})
        evaluator = get_session()
        settings = get_settings() or {}
        
        now = datetime.now()
        
        # แปลง display_type ให้อ่านง่าย
        display_label = DISPLAY_TYPE_LABELS.get(session.get("display_type", ""), session.get("display_type", ""))
        period_label = session.get("period", "")
        
        # นำทางไปหน้า research_results พร้อมส่งข้อมูล
        self.app.show_screen(
            "research_results",
            bypass_auth=True,
            results=results_data,
            hospital_name=settings.get("hospital_name", "ไม่ระบุ"),
            evaluator_name=f"{evaluator.get('name', '')} {evaluator.get('lastname', '')}".strip() if evaluator else "ไม่ระบุ",
            display_type=f"{display_label} {period_label}",
            serial_number=settings.get("screen_model", "ไม่ระบุ"),
            test_date=now.strftime("%d/%m/%Y"),
            test_time=now.strftime("%H:%M"),
        )

    def _cancel_test_to_instructions(self):
        self._stop_sequence_playback()
        self._close_test_ui()
        self.app.show_screen("instructions", bypass_auth=True)

    def _cancel_test_to_home(self):
        self._stop_sequence_playback()
        self._close_test_ui()
        self.app.show_screen("home", bypass_auth=True)

    def _close_test_ui(self):
        if self._card_win and self._card_win.winfo_exists():
            self._card_win.destroy()
            self._card_win = None
        self._close_popup()

    def _build_results_data(self):
        """แปลง answers เป็นรูปแบบที่ research_results ต้องการ"""
        # ดึงข้อมูล session
        session = getattr(self.app, "test_session", {})
        dtype = session.get("display_type", "diagnostic")
        period = session.get("period", "monthly")
        
        # ดึง config ตามประเภท
        groups = TEST_CONFIG.get(dtype, {}).get(period, [])
        
        results = []
        for group in groups:
            section = {
                "section_title": group.get("group_title", ""),
                "items": []
            }
            
            for item in group.get("items", []):
                item_id = item.get("item_id", "")
                answer = self._answers.get(item_id, {})
                
                # สร้างหมายเหตุจาก invisible_channels
                note = answer.get("note", "")
                invisible = answer.get("invisible_channels", [])
                failed_levels = answer.get("failed_levels", [])
                if invisible:
                    channels_text = ", ".join(map(str, invisible))
                    if note:
                        note = INVISIBLE_NOTE_WITH_TEXT_TEMPLATE.format(channels=channels_text, note=note)
                    else:
                        note = INVISIBLE_NOTE_TEMPLATE.format(channels=channels_text)
                elif failed_levels:
                    levels_text = ", ".join(failed_levels)
                    if note:
                        note = SEQUENCE_NOTE_WITH_TEXT_TEMPLATE.format(levels=levels_text, note=note)
                    else:
                        note = SEQUENCE_NOTE_TEMPLATE.format(levels=levels_text)
                
                section["items"].append({
                    "title": item.get("title", ""),
                    "passed": answer.get("result") == "pass" if answer else None,
                    "note": note,
                })
            
            if section["items"]:
                results.append(section)
        
        return results
