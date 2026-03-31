"""
patterns.py — สร้าง TG-270 QC test patterns เป็น numpy array
ใช้ DDL ตรงๆ (0–255, step 15) สำหรับ 18 ช่อง
Output: BGR numpy array (h, w, 3) uint8
"""

import platform
import numpy as np
import cv2

try:
    import screeninfo
    _HAS_SCREENINFO = True
except ImportError:
    _HAS_SCREENINFO = False


# ═════════════════════════════════════════════════════════════════════════════
# ค่าคงที่
# ═════════════════════════════════════════════════════════════════════════════

# DDL 18 ค่า (0–255, step=15) ตาม TG-270 sQC
DDL_18 = list(range(0, 256, 15))

# ลำดับ patch ใน grid 3×6 แบบ serpentine
SERPENTINE = [
    [ 0,  1,  2,  3,  4,  5],
    [11, 10,  9,  8,  7,  6],
    [12, 13, 14, 15, 16, 17],
]

# สี (BGR สำหรับ cv2)
_RED   = (0, 0, 255)
_LIME  = (0, 255, 200)
_WHITE = (255, 255, 255)
_BLACK = (0, 0, 0)

_FONT = cv2.FONT_HERSHEY_SIMPLEX

COLS, ROWS = 6, 3


# ═════════════════════════════════════════════════════════════════════════════
# Screen size detection
# ═════════════════════════════════════════════════════════════════════════════

def get_screen_size(monitor_index: int = 0) -> tuple[int, int]:
    os_name = platform.system()

    if os_name == "Darwin":
        try:
            from AppKit import NSScreen          # type: ignore
            screens = NSScreen.screens()
            if monitor_index < len(screens):
                s     = screens[monitor_index]
                frame = s.frame()
                scale = s.backingScaleFactor()
                return (int(frame.size.width * scale), int(frame.size.height * scale))
        except Exception:
            pass
        try:
            import Quartz                        # type: ignore
            did = Quartz.CGMainDisplayID() if monitor_index == 0 else None
            if did is not None:
                return (int(Quartz.CGDisplayPixelsWide(did)), int(Quartz.CGDisplayPixelsHigh(did)))
        except Exception:
            pass

    elif os_name == "Windows":
        try:
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                ctypes.windll.user32.SetProcessDPIAware()
            u32 = ctypes.windll.user32
            return (int(u32.GetSystemMetrics(0)), int(u32.GetSystemMetrics(1)))
        except Exception:
            pass

    if _HAS_SCREENINFO:
        try:
            mons = screeninfo.get_monitors()
            if monitor_index < len(mons):
                m = mons[monitor_index]
                return m.width, m.height
        except Exception:
            pass

    return 1920, 1080


# ═════════════════════════════════════════════════════════════════════════════
# Internal helpers
# ═════════════════════════════════════════════════════════════════════════════

def _draw_line_pairs(img, x, y, w, h, bg_ddl, orientation="vertical", num_lines=6):
    fg = min(bg_ddl + 40, 255) if bg_ddl < 128 else max(bg_ddl - 40, 0)
    fg_color = (fg, fg, fg)
    bg_color = (bg_ddl, bg_ddl, bg_ddl)

    cv2.rectangle(img, (x, y), (x + w - 1, y + h - 1), bg_color, -1)

    if orientation == "vertical":
        line_w = max(1, w // (num_lines * 2))
        for i in range(num_lines):
            bx = x + i * line_w * 2
            cv2.rectangle(img, (bx, y), (min(bx + line_w - 1, x + w - 1), y + h - 1), fg_color, -1)
    else:
        line_h = max(1, h // (num_lines * 2))
        for i in range(num_lines):
            by = y + i * line_h * 2
            cv2.rectangle(img, (x, by), (x + w - 1, min(by + line_h - 1, y + h - 1)), fg_color, -1)


def _draw_subpixel_lines(img, x, y, w, h, bg_ddl, orientation="vertical"):
    fg = min(bg_ddl + 40, 255) if bg_ddl < 128 else max(bg_ddl - 40, 0)

    x1, y1 = max(0, x), max(0, y)
    x2 = min(x + w, img.shape[1])
    y2 = min(y + h, img.shape[0])

    img[y1:y2, x1:x2] = bg_ddl

    if orientation == "vertical":
        for col in range(x1, x2, 2):
            img[y1:y2, col] = fg
    else:
        for row in range(y1, y2, 2):
            img[row, x1:x2] = fg


def _put_text_center(img, text, cx, cy, font_scale, color, thickness=1, font=_FONT):
    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    cv2.putText(img, text, (cx - tw // 2, cy + th // 2), font, font_scale, color, thickness, cv2.LINE_AA)


# ═════════════════════════════════════════════════════════════════════════════
# Shared layout: วาด grid 18 patches
# ═════════════════════════════════════════════════════════════════════════════

# เพิ่ม highlight_patch=None เข้ามาเป็นตัวเลือก
def _draw_18_patches(img, screen_w, screen_h, sf, show_numbers=True, show_border=True, border_color=_RED, highlight_patch=None, highlight_grad=False):
    margin_x = int(screen_w * 0.04)
    margin_y = int(screen_h * 0.02)
    title_h  = int(screen_h * 0.05)

    grid_left   = margin_x
    grid_right  = screen_w - margin_x
    grid_top    = margin_y + title_h
    grid_bottom = int(screen_h * 0.58)

    grid_w = grid_right - grid_left
    grid_h = grid_bottom - grid_top
    gap    = int(min(screen_w, screen_h) * 0.008)

    num_lbl_space = int(screen_h * 0.03)

    patch_w = (grid_w - gap * (COLS + 1)) // COLS
    patch_h = (grid_h - gap * (ROWS + 1) - num_lbl_space * ROWS) // ROWS

    _put_text_center(img, "TG270-sQC", screen_w // 2, margin_y + title_h // 2, max(0.8, 1.3 * sf), _WHITE, thickness=2)

    border_pad = gap // 2
    
    # คืนชีพกรอบใหญ่: ฟังก์ชันอื่นที่ส่ง show_border=True จะได้กรอบใหญ่นี้
    if show_border:
        cv2.rectangle(img,
                      (grid_left - border_pad, grid_top - border_pad),
                      (grid_right + border_pad, grid_bottom + border_pad),
                      border_color, 3)

    for row in range(ROWS):
        for col in range(COLS):
            pidx = SERPENTINE[row][col]
            ddl  = DDL_18[pidx]
            pnum = pidx + 1

            cx = grid_left + gap + col * (patch_w + gap)
            cy = grid_top  + gap + row * (patch_h + num_lbl_space + gap)

            py1 = cy
            py2 = py1 + patch_h

            # 1. วาดกรอบ Patch สีเทา
            cv2.rectangle(img, (cx, py1), (cx + patch_w, py2), (ddl, ddl, ddl), -1)

            # 2. วาดกรอบแดง เล็งเฉพาะกล่องที่ระบุใน highlight_patch
            if highlight_patch == pnum:
                cv2.rectangle(img, (cx, py1), (cx + patch_w, py2), border_color, 3)

            text_color = _WHITE if ddl < 128 else _BLACK
            _put_text_center(img, str(ddl), cx + patch_w // 2, py1 + int(patch_h * 0.15), max(0.4, 0.5 * sf), text_color, thickness=1)

            lp_w = max(16, patch_w // 5)
            lp_h = max(12, patch_h // 3)
            
            _draw_line_pairs(img, cx + 4, py1 + 4, lp_w, lp_h, ddl, "vertical", num_lines=6)
            _draw_line_pairs(img, cx + patch_w - lp_w - 4, py2 - lp_h - 4, lp_w, lp_h, ddl, "vertical", num_lines=6)

            # โชว์ตัวเลข 1-18 ตามการตั้งค่า
            if show_numbers:
                _put_text_center(img, str(pnum), cx + patch_w // 2, py2 + num_lbl_space // 2, max(0.45, 0.7 * sf), _LIME, thickness=2)

    # กล่องดำ / ขาว
    box_gap_y = int(screen_h * 0.04)
    box_top   = grid_bottom + border_pad + box_gap_y
    box_h     = int(screen_h * 0.22)
    box_w     = int(screen_w * 0.24)

    # 1. หาจุดกึ่งกลางหน้าจอแนวนอน
    center_x = screen_w // 2
    # 2. กำหนดระยะห่างระหว่างกล่องดำกับกล่องขาว (ตรงกลาง)
    center_gap = int(screen_w * 0.02) # นายน้อยเพิ่มลดเลข 0.02 เพื่อปรับความห่างได้ครับ
    # 3. คำนวณตำแหน่งแนวนอน (X) ใหม่ให้อยู่โซนกลาง
    bx = center_x - box_w - (center_gap // 2) # กล่องดำอยู่ซ้ายของจุดกึ่งกลาง
    wx = center_x + (center_gap // 2)         # กล่องขาวอยู่ขวาของจุดกึ่งกลาง
    # วาดกล่องดำ
    cv2.rectangle(img, (bx, box_top), (bx + box_w, box_top + box_h), _BLACK, -1)
    # วาดกล่องขาว
    cv2.rectangle(img, (wx, box_top), (wx + box_w, box_top + box_h), _WHITE, -1)

    # Gradient bar
    grad_h = int(screen_h * 0.06)
    grad_y = screen_h - grad_h
    # แนวนอน: แก้ตรงนี้ครับ ให้เริ่มที่ขอบซ้ายสุด (0) และกว้างเต็มจอ (screen_w)
    grad_x = 0
    grad_w = screen_w - 27 * gap

    for px_off in range(grad_w):
        val = int(px_off * 255 / max(grad_w - 1, 1))
        cv2.line(img, (grad_x + px_off, grad_y), (grad_x + px_off, grad_y + grad_h), (val, val, val))

    # >>> เพิ่มโค้ดตรงนี้: ถ้าเปิด highlight_grad ให้วาดกรอบแดงทับ <<<
    if highlight_grad:
        # ความหนาเส้นคือ 3
        cv2.rectangle(img, (grad_x, grad_y), (grad_x + grad_w, grad_y + grad_h), border_color, 4)

    return {
        "grid_left": grid_left, "grid_right": grid_right,
        "grid_top": grid_top, "grid_bottom": grid_bottom,
        "border_pad": border_pad,
        "margin_x": margin_x, "margin_y": margin_y,
        "grad_y": grad_y, "grad_h": grad_h,
        "grad_x": grad_x, "grad_w": grad_w,
    }

# --> Diagnostic Luminance Patterns Month <--
# --> sQC <--
# ═════════════════════════════════════════════════════════════════════════════
# Pattern 1 & 2
# ═════════════════════════════════════════════════════════════════════════════

def make_luminance_patches(screen_w: int, screen_h: int, diagnostic_step: int = 0) -> np.ndarray:
    bg  = 34
    img = np.full((screen_h, screen_w, 3), bg, dtype=np.uint8)
    sf  = screen_w / 1920.0

    layout = _draw_18_patches(img, screen_w, screen_h, sf, show_numbers=True, show_border=True, border_color=_RED)

    rb_w = int(screen_w * 0.05)
    rb_h = int(screen_h * 0.06) 
    rb_y = layout["grad_y"] - (rb_h - layout["grad_h"])
    rb_x1 = layout["grad_x"] + layout["grad_w"] + int(screen_w * 0.01)
    
    _draw_subpixel_lines(img, rb_x1, rb_y, rb_w, rb_h, 0, "vertical")
    rb_x2 = rb_x1 + rb_w + 7
    _draw_subpixel_lines(img, rb_x2, rb_y, rb_w, rb_h, 255, "horizontal")

    return img


# ═════════════════════════════════════════════════════════════════════════════
# Pattern 3
# ═════════════════════════════════════════════════════════════════════════════

def make_spatial_resolution(screen_w: int, screen_h: int, diagnostic_step: int = 0) -> np.ndarray:
    bg  = 34
    img = np.full((screen_h, screen_w, 3), bg, dtype=np.uint8)
    sf  = screen_w / 1920.0

    layout = _draw_18_patches(img, screen_w, screen_h, sf, show_numbers=False, show_border=False)

    rb_w  = int(screen_w * 0.05)
    rb_h  = int(screen_h * 0.06) 
    rb_y  = layout["grad_y"] - (rb_h - layout["grad_h"])
    rb_x1 = layout["grad_x"] + layout["grad_w"] + int(screen_w * 0.01)

    _draw_subpixel_lines(img, rb_x1, rb_y, rb_w, rb_h, 0, "vertical")
    rb_x2 = rb_x1 + rb_w + int(screen_w * 0.005)
    _draw_subpixel_lines(img, rb_x2, rb_y, rb_w, rb_h, 255, "horizontal")

    pad = 4
    cv2.rectangle(img, (rb_x1 - pad, rb_y - pad), (rb_x2 + rb_w + pad, rb_y + rb_h + pad), _RED, 2)

    return img

# --> Diagnostic Luminance Patterns Month End <--

# --> Diagnostic Luminance Patterns 3 Month <--
# TODO: Implement 3-month
def add_vertical_stripes(img, x1, x2, y1, y2, v1, v2, period):
    w = x2 - x1
    xs = np.arange(w)
    stripe = np.where((xs % period) < (period // 2), v1, v2).astype(np.uint8)
    patch = np.tile(stripe, (y2 - y1, 1))
    img[y1:y2, x1:x2] = patch[:, :, None]


def add_horizontal_stripes(img, x1, x2, y1, y2, v1, v2, period):
    h = y2 - y1
    ys = np.arange(h)
    stripe = np.where((ys % period) < (period // 2), v1, v2).astype(np.uint8)
    patch = np.tile(stripe[:, None], (1, x2 - x1))
    img[y1:y2, x1:x2] = patch[:, :, None]


def make_pattern(width=1920, height=1080):
    img = np.full((height, width, 3), 58, dtype=np.uint8)

    # main center gradient
    x0, x1 = 160, width - 160
    y0, y1 = 70, height - 60
    main_w = x1 - x0
    main_h = y1 - y0

    gx = np.linspace(0, 1, main_w, dtype=np.float32)[None, :]
    gy = np.linspace(0, 1, main_h, dtype=np.float32)[:, None]

    base = 18 + 220 * gy
    vignette = -22 * np.abs(gx - 0.5)
    panel = np.clip(base + vignette, 0, 255).astype(np.uint8)
    img[y0:y1, x0:x1] = panel[:, :, None]

    # left/right side bars
    side_grad = np.linspace(10, 240, height, dtype=np.uint8)[:, None]
    img[:, :110] = side_grad[:, :, None]
    img[:, width - 110:] = np.flipud(side_grad)[:, :, None]

    # top dark band
    img[65:110, x0:x1] = 5

    # horizontal luminance steps
    steps = 16
    step_h = (y1 - y0) // steps
    for i in range(steps):
        yy0 = y0 + i * step_h
        yy1 = y0 + (i + 1) * step_h if i < steps - 1 else y1
        val = int(12 + (235 - 12) * i / (steps - 1))
        img[yy0:yy1, x0:x1] = np.clip(img[yy0:yy1, x0:x1].astype(np.int16) * 0.55 + val * 0.45, 0, 255)

    # left block a bit flatter
    img[y0:y1, x0:540] = np.clip(img[y0:y1, x0:540].astype(np.int16) * 0.9, 0, 255).astype(np.uint8)

    # right-side fine vertical frequency area
    add_vertical_stripes(img, 1220, 1700, 110, y1, 30, 70, 6)
    add_vertical_stripes(img, 1450, 1760, 110, y1, 25, 95, 4)

    # top sample boxes
    top_boxes = [
        (350, 445, 8, 'h'),
        (540, 635, 6, 'h'),
        (1090, 1185, 5, 'v'),
        (1320, 1435, 10, 'v'),
        (1600, 1715, 16, 'v'),
    ]
    for bx0, bx1, period, mode in top_boxes:
        cv2.rectangle(img, (bx0, 12), (bx1, 58), (70, 70, 70), -1)
        if mode == 'h':
            add_horizontal_stripes(img, bx0, bx1, 12, 58, 210, 80, period)
        else:
            add_vertical_stripes(img, bx0, bx1, 12, 58, 215, 90, period)

    # bottom highlighted boxes
    green = (180, 255, 80)
    bottom_boxes = [
        (350, 455, 1020, 1080, 'h', 8),
        (535, 640, 1020, 1080, 'h', 4),
        (720, 825, 1020, 1080, 'solid', 0),
        (1090, 1195, 1020, 1080, 'v', 3),
        (1280, 1385, 1020, 1080, 'v', 8),
        (1470, 1580, 1020, 1080, 'v', 16),
    ]
    for i, (bx0, bx1, by0, by1, mode, period) in enumerate(bottom_boxes, start=1):
        cv2.rectangle(img, (bx0, by0), (bx1, by1), green, 4)
        inner_x0, inner_x1 = bx0 + 6, bx1 - 6
        inner_y0, inner_y1 = by0 + 6, by1 - 6
        img[inner_y0:inner_y1, inner_x0:inner_x1] = 180
        if mode == 'h':
            add_horizontal_stripes(img, inner_x0, inner_x1, inner_y0, inner_y1, 210, 100, period)
        elif mode == 'v':
            add_vertical_stripes(img, inner_x0, inner_x1, inner_y0, inner_y1, 220, 90, period)

        cv2.putText(
            img, str(i), (bx0 - 35, by0 + 45),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, green, 2, cv2.LINE_AA
        )

    # top text
    cv2.putText(
        img, "TG270-pQC", (865, 35),
        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (110, 110, 110), 2, cv2.LINE_AA
    )

    return img
# --> Diagnostic Luminance Patterns 3 Month End <--



# ═════════════════════════════════════════════════════════════════════════════
# Quick test
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    w, h = 1920, 1080

    img1 = make_luminance_patches(w, h)
    cv2.imwrite("preview_luminance.png", img1)
    print(f"✅ preview_luminance.png  ({w}×{h})")

    # img2 = make_spatial_resolution(w, h)
    # cv2.imwrite("preview_spatial.png", img2)
    # print(f"✅ preview_spatial.png    ({w}×{h})")

    # img3 = make_pattern(w, h)
    # cv2.imwrite("preview_pqc.png", img3)
    # print(f"✅ preview_pqc.png    ({w}×{h})")

    # img4 = make_luminance_patches_3_month_3(w, h)
    # cv2.imwrite("preview_luminance_3_month.png", img4)
    # print(f"✅ preview_luminance_3_month.png    ({w}×{h})")

    print(f"   Screen detection: {get_screen_size()}")