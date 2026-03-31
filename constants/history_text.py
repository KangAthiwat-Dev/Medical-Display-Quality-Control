HISTORY_TITLE_TEXT = "ประวัติการทดสอบ"
HISTORY_BACK_TEXT = "↩"
HISTORY_EMPTY_TEXT = "ไม่พบข้อมูล"
HISTORY_DETAIL_BUTTON_TEXT = "ดูรายละเอียด"
HISTORY_PDF_BUTTON_TEXT = "พิมพ์ PDF"

HISTORY_HOSPITAL_LABEL = "ค้นหา"
HISTORY_HOSPITAL_PLACEHOLDER = "ชื่อโรงพยาบาล"
HISTORY_DISPLAY_TYPE_LABEL = "เลือกชนิดจอ"
HISTORY_ROUND_LABEL = "รอบ"
HISTORY_DATE_FROM_LABEL = "จากวันที่"
HISTORY_DATE_TO_LABEL = "ถึงวันที่"
HISTORY_DATE_PLACEHOLDER = "วว/ดด/ปปปป"
HISTORY_DATE_ERROR_TEXT = "รูปแบบวันที่ไม่ถูกต้อง กรุณากรอกเป็น วว/ดด/ปปปป"
HISTORY_SELECTION_REQUIRED_TEXT = "กรุณาเลือกรายการก่อน"

HISTORY_TABLE_HEADERS = ["ครั้งที่", "วันที่", "โรงพยาบาล", "ชนิด", "รอบ", "ผู้ประเมิน", "รุ่นหน้าจอ"]

HISTORY_DISPLAY_TYPE_OPTIONS = [
    "ทั้งหมด",
    "หน้าจอชนิดใช้วินิจฉัยทางการแพทย์",
    "หน้าจอชนิดใช้แสดงทางการแพทย์",
    "หน้าจอตรวจทานทางการแพทย์",
]

HISTORY_ROUND_OPTIONS = [
    "ทั้งหมด",
    "การประเมินประจำเดือน",
    "การประเมินราย 3 เดือน",
    "การประเมินประจำปี",
]

DISPLAY_TYPE_FILTER_TO_KEY = {
    "ทั้งหมด": "",
    "หน้าจอชนิดใช้วินิจฉัยทางการแพทย์": "diagnostic",
    "หน้าจอชนิดใช้แสดงทางการแพทย์": "modality",
    "หน้าจอตรวจทานทางการแพทย์": "clinic",
}

DISPLAY_TYPE_KEY_TO_LABEL = {
    "diagnostic": "Diagnostic",
    "modality": "Modality",
    "clinic": "Clinical Review",
    "clinical": "Clinical Review",
}

ROUND_FILTER_TO_KEY = {
    "ทั้งหมด": "",
    "การประเมินประจำเดือน": "monthly",
    "การประเมินราย 3 เดือน": "quarterly",
    "การประเมินประจำปี": "annual",
}

ROUND_KEY_TO_LABEL = {
    "monthly": "รายเดือน",
    "quarterly": "ราย 3 เดือน",
    "annual": "รายปี",
}
