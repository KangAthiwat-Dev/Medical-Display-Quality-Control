import cv2
from PIL import Image, ImageTk

import draw.patterns as pat


def render_pattern_image(item, canvas_width: int, canvas_height: int):
    func_name = item.get("pattern_func", "make_luminance_patches")
    gen_func = getattr(pat, func_name, pat.make_luminance_patches)

    diagnostic_step = item.get("diagnostic_step", 0)
    bgr = gen_func(canvas_width, canvas_height, diagnostic_step=diagnostic_step)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    return ImageTk.PhotoImage(pil_img)
