HELP_TEXT = (
    "คำแนะนำในการทดสอบระบบ\n\n"
    "1. ควรเปิดหน้าจอไว้ก่อน 30 นาที\n\n"
    "2. ระยะห่างของการทดสอบตั้งแต่ระยะสายตา\n"
    "   ของผู้ทดสอบถึงหน้าจอควรมีระยะห่าง\n"
    "   ประมาณหนึ่งช่วงแขน (ประมาณ 65 ซม.)\n\n"
    "3. ทำความสะอาดหน้าจอก่อน\n"
    "   ตามที่บริษัทผู้ผลิตแนะนำการทดสอบ"
)

DISPLAY_TYPE_LABELS = {
    "diagnostic": "Diagnostic",
    "modality": "Modality",
    "clinic": "Clinical Review",
    "clinical": "Clinical Review & Electronic Health Record",
}

PERIOD_LABELS = {
    "monthly": "รายเดือน",
    "quarterly": "ราย 3 เดือน",
    "annual": "รายปี",
}

POPUP_CLOSE_TEXT = "ปิด"
ANSWER_YES_TEXT = "ใช่"
ANSWER_NO_TEXT = "ไม่ใช่"
NOTE_LABEL_TEXT = "หมายเหตุ"
INVISIBLE_CHANNELS_TEXT = "ระบุช่องที่มองไม่เห็น"
NEXT_BUTTON_TEXT = "ถัดไป"
SUMMARY_BUTTON_TEXT = "สรุปผล"
PREVIOUS_BUTTON_TEXT = "ก่อนหน้า"
START_BUTTON_TEXT = "เริ่ม"
PLAY_BUTTON_TEXT = "เล่นต่อ"
PAUSE_BUTTON_TEXT = "หยุด"
REPLAY_BUTTON_TEXT = "เล่นซ้ำ"
SPEED_SLOW_TEXT = "ช้า"
SPEED_NORMAL_TEXT = "ปกติ"
SPEED_FAST_TEXT = "เร็ว"
SEEK_LABEL_TEMPLATE = "เฟรม: {current}/{total}"
SEQUENCE_SPEED_LABEL_TEMPLATE = "ความเร็ว: {speed}"
SEQUENCE_SHORTCUT_HELP_TEXT = "คีย์ลัด: Space = เล่น/หยุด, M = ทำเครื่องหมายไม่ผ่าน"
MARK_FAIL_BUTTON_TEMPLATE = "ไม่ผ่านค่าปัจจุบัน ({level})"
UNMARK_FAIL_BUTTON_TEMPLATE = "ยกเลิกไม่ผ่าน ({level})"
SEQUENCE_SUMMARY_BUTTON_TEXT = "สรุปผล"
SEQUENCE_LEVEL_TEMPLATE = "ค่าปัจจุบัน: {level}"
SEQUENCE_STATUS_PLAYING = "สถานะ: กำลังเล่นอัตโนมัติ"
SEQUENCE_STATUS_PAUSED = "สถานะ: หยุดชั่วคราว"
SEQUENCE_STATUS_COMPLETED = "สถานะ: เล่นครบทุก frame แล้ว"
SEQUENCE_FAILED_LABEL_TEXT = "ค่าที่ทำเครื่องหมายว่าไม่ผ่าน"
SEQUENCE_FAILED_EMPTY_TEXT = "ยังไม่มีค่าที่ถูกทำเครื่องหมายว่าไม่ผ่าน"
SEQUENCE_SUMMARY_PASS_TEXT = "ผลการประเมินข้อนี้: ผ่าน"
SEQUENCE_SUMMARY_FAIL_TEMPLATE = "ผลการประเมินข้อนี้: ไม่ผ่าน ({levels})"
SEQUENCE_PLAYER_HELP_TEXT = "ระบบจะเล่น frame อัตโนมัติ และจะหยุดทันทีเมื่อกดไม่ผ่านค่าปัจจุบัน"
SEQUENCE_NOTE_TEMPLATE = "ค่า pixel ที่ไม่ผ่าน: {levels}"
SEQUENCE_NOTE_WITH_TEXT_TEMPLATE = "ค่า pixel ที่ไม่ผ่าน: {levels} | {note}"

DISPLAY_INFO_TEMPLATE = (
    "📋 การทดสอบที่กำลังทำ\n\n"
    "ประเภท: {display_name}\n"
    "รอบ: {period_name}\n"
    "จำนวนข้อ: {total_items} ข้อ\n"
    "ข้อปัจจุบัน: {current_index}"
)

ANSWER_REQUIRED_ERROR = "⚠ กรุณาเลือกคำตอบก่อน (ใช่ / ไม่ใช่)"
CHANNEL_REQUIRED_ERROR = "⚠ กรุณาระบุช่องที่มองไม่เห็นอย่างน้อย 1 ช่อง"
INVISIBLE_NOTE_TEMPLATE = "ช่องที่ไม่เห็น: {channels}"
INVISIBLE_NOTE_WITH_TEXT_TEMPLATE = "ช่องที่ไม่เห็น: {channels} | {note}"
SEQUENCE_NOT_FINISHED_ERROR = "⚠ กรุณาดู frame ให้ครบก่อนสรุปผล"
