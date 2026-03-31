import customtkinter as ctk

from constants.test_text import (
    NEXT_BUTTON_TEXT,
    PAUSE_BUTTON_TEXT,
    PLAY_BUTTON_TEXT,
    PREVIOUS_BUTTON_TEXT,
    REPLAY_BUTTON_TEXT,
    SEEK_LABEL_TEMPLATE,
    SEQUENCE_SPEED_LABEL_TEMPLATE,
    SPEED_FAST_TEXT,
    SPEED_NORMAL_TEXT,
    SPEED_SLOW_TEXT,
)

class SequenceSeekBarWidget(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_seek=None,
        on_prev=None,
        on_play_toggle=None,
        on_replay=None,
        on_next=None,
        on_speed_change=None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color="#1D1D1D",
            corner_radius=4,
            border_width=1,
            border_color="#3A3A3A",
            height=92,
            **kwargs,
        )
        self._on_seek = on_seek
        self._on_prev = on_prev
        self._on_play_toggle = on_play_toggle
        self._on_replay = on_replay
        self._on_next = on_next
        self._on_speed_change = on_speed_change

        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=18, pady=(12, 4))

        self.seek_label = ctk.CTkLabel(
            top_row,
            text="",
            font=("TH Sarabun New", 18, "bold"),
            text_color="#E6E6E6",
        )
        self.seek_label.pack(side="left")

        self.speed_label = ctk.CTkLabel(
            top_row,
            text="",
            font=("TH Sarabun New", 16, "bold"),
            text_color="#BFBFBF",
        )
        self.speed_label.pack(side="right")

        self.seek_slider = ctk.CTkSlider(
            self,
            from_=0,
            to=1,
            number_of_steps=1,
            command=self._handle_seek,
        )
        self.seek_slider.pack(fill="x", padx=18, pady=(0, 8))

        self.mark_status_label = ctk.CTkLabel(
            self,
            text="",
            font=("TH Sarabun New", 18, "bold"),
            text_color="#E14D4D",
        )
        self.mark_status_label.pack(pady=(0, 6))

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkButton(
            controls,
            text=PREVIOUS_BUTTON_TEXT,
            font=("TH Sarabun New", 18, "bold"),
            fg_color="#555555",
            hover_color="#666666",
            width=92,
            height=34,
            command=self._handle_prev,
        ).pack(side="left", padx=(0, 6))

        self.play_button = ctk.CTkButton(
            controls,
            text=PLAY_BUTTON_TEXT,
            font=("TH Sarabun New", 18, "bold"),
            fg_color="#4A90D9",
            hover_color="#3A7BC8",
            width=92,
            height=34,
            command=self._handle_play_toggle,
        )
        self.play_button.pack(side="left", padx=6)

        ctk.CTkButton(
            controls,
            text=REPLAY_BUTTON_TEXT,
            font=("TH Sarabun New", 18, "bold"),
            fg_color="#666666",
            hover_color="#777777",
            width=92,
            height=34,
            command=self._handle_replay,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            controls,
            text=NEXT_BUTTON_TEXT,
            font=("TH Sarabun New", 18, "bold"),
            fg_color="#555555",
            hover_color="#666666",
            width=92,
            height=34,
            command=self._handle_next,
        ).pack(side="left", padx=6)

        self.speed_control = ctk.CTkSegmentedButton(
            controls,
            values=[SPEED_SLOW_TEXT, SPEED_NORMAL_TEXT, SPEED_FAST_TEXT],
            font=("TH Sarabun New", 15, "bold"),
            command=self._handle_speed_change,
        )
        self.speed_control.pack(side="right")

        self._bind_children_recursive(self)

    def _bind_children_recursive(self, widget):
        for child in widget.winfo_children():
            try:
                child.bind("<Enter>", self._relay_enter, add="+")
                child.bind("<Leave>", self._relay_leave, add="+")
            except NotImplementedError:
                pass
            self._bind_children_recursive(child)

    def _relay_enter(self, event=None):
        self.event_generate("<Enter>")

    def _relay_leave(self, event=None):
        self.event_generate("<Leave>")

    def _handle_seek(self, value):
        if self._on_seek:
            self._on_seek(value)

    def _handle_prev(self):
        if self._on_prev:
            self._on_prev()

    def _handle_play_toggle(self):
        if self._on_play_toggle:
            self._on_play_toggle()

    def _handle_replay(self):
        if self._on_replay:
            self._on_replay()

    def _handle_next(self):
        if self._on_next:
            self._on_next()

    def _handle_speed_change(self, value):
        if self._on_speed_change:
            self._on_speed_change(value)

    def update_state(
        self,
        *,
        current,
        total,
        speed_label,
        playing,
        slider_to,
        slider_steps,
        mark_status_text="",
    ):
        self.seek_label.configure(
            text=SEEK_LABEL_TEMPLATE.format(current=current, total=total)
        )
        self.speed_label.configure(
            text=SEQUENCE_SPEED_LABEL_TEMPLATE.format(speed=speed_label)
        )
        self.mark_status_label.configure(text=mark_status_text)
        self.play_button.configure(text=PAUSE_BUTTON_TEXT if playing else PLAY_BUTTON_TEXT)
        self.seek_slider.configure(to=slider_to, number_of_steps=slider_steps)
        self.seek_slider.set(current - 1)
        self.speed_control.set(speed_label)
