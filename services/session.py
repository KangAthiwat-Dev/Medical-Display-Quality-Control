import os
import json

SESSION_FILE = os.path.join(os.path.dirname(__file__), "..", "session", "session.json")

def _save(data: dict):
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def set_evaluator_session(user: dict):
    """เก็บ Session ของผู้ประเมินที่เข้าสู่ระบบสำเร็จ"""
    user_data = dict(user)
    user_data.pop("password", None) # ห้ามเก็บรหัสลงไฟล์เด็ดขาด
    _save(user_data)

def clear_session():
    """ออกจากระบบ"""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def get_session():
    """ดึงข้อมูลผู้ถูกเข้าสู่ระบบปัจจุบัน"""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return None

def is_evaluator_logged_in() -> bool:
    """เช็คว่าปัจจุบันมี session ของผู้ประเมินอยู่หรือไม่"""
    sess = get_session()
    return sess is not None
