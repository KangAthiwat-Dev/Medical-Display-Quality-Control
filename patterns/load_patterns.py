from pathlib import Path
from PIL import Image, ImageOps
from constants.evaluation_questions import TEST_CONFIG


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATTERN_DIR = PROJECT_ROOT / "assets" / "patterns" / "patterns_png"
SEQUENCE_DIR = PROJECT_ROOT / "assets" / "patterns"

DISPLAY_FILE_PREFIXES = {
    "clinic": "clinical",
}

PERIOD_FILE_CODES = {
    "monthly": "m",
    "quarterly": "3m",
    "annual": "y",
}

def _build_pattern_map():
    pattern_map = {}
    sequence_map = {}

    for display_type, periods in TEST_CONFIG.items():
        for period, groups in periods.items():
            period_code = PERIOD_FILE_CODES.get(period)
            if not period_code:
                continue
            display_prefix = DISPLAY_FILE_PREFIXES.get(display_type, display_type)

            for group in groups:
                for item in group.get("items", []):
                    item_id = item.get("item_id")
                    image_index = item.get("image_index")
                    if not item_id or image_index is None:
                        continue

                    filename = f"{display_prefix}_{period_code}_{image_index}.png"
                    pattern_map[(display_type, period, item_id)] = PATTERN_DIR / filename
                    sequence_map[(display_type, period, item_id)] = (
                        SEQUENCE_DIR / f"{display_prefix}_{period_code}_{image_index}.TIFF"
                    )

    return pattern_map, sequence_map


PATTERN_MAP, SEQUENCE_MAP = _build_pattern_map()


def _fit_image_to_canvas(image: Image.Image, width: int, height: int) -> Image.Image:
    return image.resize((width, height), Image.Resampling.LANCZOS)


def load_pattern_image(display_type: str, period: str, item_id: str, width: int, height: int) -> Image.Image:
    image_path = PATTERN_MAP.get((display_type, period, item_id))
    if image_path is None:
        raise KeyError(
            f"ไม่พบ mapping ของ pattern สำหรับ display_type={display_type!r}, "
            f"period={period!r}, item_id={item_id!r}"
        )

    if not image_path.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ pattern: {image_path}")

    with Image.open(image_path) as image:
        rgb_image = image.convert("RGB")
        return _fit_image_to_canvas(rgb_image, width, height)


def has_pattern_sequence(display_type: str, period: str, item_id: str) -> bool:
    sequence_dir = SEQUENCE_MAP.get((display_type, period, item_id))
    return bool(sequence_dir and sequence_dir.exists() and sequence_dir.is_dir())


def get_pattern_sequence_frames(display_type: str, period: str, item_id: str) -> list[Path]:
    sequence_dir = SEQUENCE_MAP.get((display_type, period, item_id))
    if sequence_dir is None:
        raise KeyError(
            f"ไม่พบ mapping ของ TIFF sequence สำหรับ display_type={display_type!r}, "
            f"period={period!r}, item_id={item_id!r}"
        )

    if not sequence_dir.exists():
        raise FileNotFoundError(f"ไม่พบโฟลเดอร์ TIFF sequence: {sequence_dir}")

    frame_paths = sorted(sequence_dir.glob("*.tif"))
    if not frame_paths:
        raise FileNotFoundError(f"ไม่พบไฟล์ .tif ในโฟลเดอร์: {sequence_dir}")

    return frame_paths


def load_pattern_sequence_frame(frame_path: Path, width: int, height: int) -> Image.Image:
    with Image.open(frame_path) as image:
        rgb_image = image.convert("RGB")
        return _fit_image_to_canvas(rgb_image, width, height)


def get_frame_level(frame_path: Path) -> str:
    return frame_path.stem.rsplit("-", 1)[-1]
