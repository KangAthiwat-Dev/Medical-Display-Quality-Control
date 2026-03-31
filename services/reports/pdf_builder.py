from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


PAGE_WIDTH, PAGE_HEIGHT = A4
FONT_NAME = "THSarabunNew"
TITLE_TEXT = "รายงานผลการประเมินคุณภาพหน้าจอแสดงผลทางการแพทย์"

DISPLAY_TYPE_LABELS = {
    "diagnostic": "Diagnostic",
    "modality": "Modality",
    "clinic": "Clinical",
    "clinical": "Clinical",
}

PERIOD_LABELS = {
    "monthly": "รายเดือน",
    "quarterly": "ราย 3 เดือน",
    "annual": "รายปี",
}


def build_evaluation_pdf(evaluation: dict, results: list[dict]) -> bytes:
    styles = _styles()
    story = [
        Paragraph(TITLE_TEXT, styles["title"]),
        Spacer(1, 4 * mm),
        Paragraph(evaluation.get("hospital_name", ""), styles["meta_bold"]),
        Paragraph(_meta_line_for_evaluation(evaluation), styles["meta"]),
        Paragraph(_date_line(evaluation), styles["meta"]),
        Spacer(1, 6 * mm),
        _evaluation_table(results, styles),
    ]
    return _build_pdf(story)


def build_comparison_pdf(current_evaluation: dict, baseline_evaluation: dict, rows_data: list[dict]) -> bytes:
    styles = _styles()
    story = [
        Paragraph(TITLE_TEXT, styles["title"]),
        Spacer(1, 4 * mm),
        Paragraph("เปรียบเทียบกับ Baseline", styles["meta_bold"]),
        Paragraph(_meta_line_for_comparison(baseline_evaluation, prefix="Baseline"), styles["meta"]),
        Paragraph(_meta_line_for_comparison(current_evaluation, prefix="ครั้งนี้"), styles["meta"]),
        Paragraph(_date_line(current_evaluation), styles["meta"]),
        Spacer(1, 6 * mm),
        _comparison_table(rows_data, styles),
    ]
    return _build_pdf(story)


def _build_pdf(story) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=14 * mm,
    )
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_footer(total_pages)
            super().showPage()
        super().save()

    def _draw_page_footer(self, total_pages):
        self.saveState()
        self.setFont(FONT_NAME, 10)
        self.drawCentredString(PAGE_WIDTH / 2, 8 * mm, f"หน้า {self._pageNumber}/{total_pages}")
        self.restoreState()


def _evaluation_table(results, styles):
    rows = [
        [
            Paragraph("หัวข้อประเมิน", styles["table_header"]),
            Paragraph("ผลการประเมิน", styles["table_header"]),
            Paragraph("หมายเหตุ", styles["table_header"]),
        ]
    ]
    spans = []
    section_rows = []

    for section in results:
        row_index = len(rows)
        rows.append([Paragraph(section.get("section_title", ""), styles["section"]), "", ""])
        spans.append(("SPAN", (0, row_index), (2, row_index)))
        section_rows.append(row_index)

        for item in section.get("items", []):
            result_text = _pass_text(item.get("passed"))
            rows.append(
                [
                    Paragraph(_to_para_text(item.get("title", "")), styles["cell"]),
                    Paragraph(result_text, styles["cell_center"]),
                    Paragraph(_to_para_text(item.get("note", "")), styles["cell"]),
                ]
            )

    table = Table(rows, colWidths=[220, 110, 175], repeatRows=1)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#555555")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    style.extend(spans)
    for row_index in section_rows:
        style.append(("BACKGROUND", (0, row_index), (-1, row_index), colors.HexColor("#EFEFEF")))
    table.setStyle(TableStyle(style))
    return table


def _comparison_table(rows_data, styles):
    rows = [
        [
            Paragraph("หัวข้อประเมิน", styles["table_header"]),
            Paragraph("Baseline", styles["table_header"]),
            Paragraph("ครั้งนี้", styles["table_header"]),
            Paragraph("ผลการเปรียบเทียบ", styles["table_header"]),
            Paragraph("คำอธิบายเพิ่มเติมจากการเปรียบเทียบ", styles["table_header"]),
        ]
    ]
    spans = []
    section_rows = []

    for section in rows_data:
        row_index = len(rows)
        rows.append([Paragraph(section.get("section_title", ""), styles["section"]), "", "", "", ""])
        spans.append(("SPAN", (0, row_index), (4, row_index)))
        section_rows.append(row_index)

        for item in section.get("items", []):
            rows.append(
                [
                    Paragraph(_to_para_text(item.get("title", "")), styles["cell"]),
                    Paragraph(_to_para_text(item.get("baseline_text", "")), styles["cell_center"]),
                    Paragraph(_to_para_text(item.get("current_text", "")), styles["cell_center"]),
                    Paragraph(_to_para_text(item.get("compare_text", "")), styles["cell"]),
                    Paragraph(_to_para_text(item.get("description", "")), styles["cell"]),
                ]
            )

    table = Table(rows, colWidths=[107, 62, 52, 128, 161], repeatRows=1)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#555555")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    style.extend(spans)
    for row_index in section_rows:
        style.append(("BACKGROUND", (0, row_index), (-1, row_index), colors.HexColor("#EFEFEF")))
    table.setStyle(TableStyle(style))
    return table


def _pass_text(passed):
    if passed is True:
        return "ผ่าน"
    if passed is False:
        return "ไม่ผ่าน"
    return "-"


def _meta_line_for_evaluation(evaluation):
    display_type = DISPLAY_TYPE_LABELS.get(evaluation.get("screen_type", ""), evaluation.get("screen_type", ""))
    period = PERIOD_LABELS.get(evaluation.get("period", ""), evaluation.get("period", ""))
    return (
        f"{display_type} {period}    หมายเลขครุภัณฑ์    {evaluation.get('screen_model', '')}    "
        f"ผู้ประเมิน    {evaluation.get('evaluator_name', '')}    "
        f"{_date_parts(evaluation.get('eval_datetime', ''))[0]}    {_date_parts(evaluation.get('eval_datetime', ''))[1]}"
    )


def _meta_line_for_comparison(evaluation, prefix):
    display_type = DISPLAY_TYPE_LABELS.get(evaluation.get("screen_type", ""), evaluation.get("screen_type", ""))
    period = PERIOD_LABELS.get(evaluation.get("period", ""), evaluation.get("period", ""))
    rank = evaluation.get("rank", "-")
    if evaluation.get("id"):
        try:
            from database.database import get_eval_rank
            rank = get_eval_rank(evaluation.get("screen_type", ""), evaluation.get("period", ""), evaluation.get("id"))
        except Exception:
            pass
    return (
        f"{prefix} (ครั้งที่ {rank} ):    {evaluation.get('hospital_name', '')}    "
        f"ผู้ประเมิน    {evaluation.get('evaluator_name', '')}    "
        f"{_date_parts(evaluation.get('eval_datetime', ''))[0]}    {_date_parts(evaluation.get('eval_datetime', ''))[1]}"
    ).replace("  ", " ")


def _date_line(evaluation):
    date_text, time_text = _date_parts(evaluation.get("eval_datetime", ""))
    return f"วันที่พิมพ์:    {date_text}    {time_text}"


def _date_parts(value):
    if not value:
        return "", ""
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            from datetime import datetime
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M:%S")
        except ValueError:
            continue
    return value, ""


def _to_para_text(value):
    return str(value or "").replace("\n", "<br/>")


def _styles():
    _register_font()
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=20,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "meta": ParagraphStyle(
            "meta",
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=10.5,
            leading=12,
            alignment=TA_LEFT,
        ),
        "meta_bold": ParagraphStyle(
            "meta_bold",
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=11,
            leading=12,
            alignment=TA_CENTER,
        ),
        "section": ParagraphStyle(
            "section",
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=10.5,
            leading=12,
            alignment=TA_LEFT,
        ),
        "cell": ParagraphStyle(
            "cell",
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=10,
            leading=12,
            alignment=TA_LEFT,
        ),
        "cell_center": ParagraphStyle(
            "cell_center",
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
        ),
    }


def _register_font():
    if FONT_NAME in pdfmetrics.getRegisteredFontNames():
        return

    font_path = Path(__file__).resolve().parents[2] / "assets" / "fonts" / "THSarabunNew.ttf"
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(font_path)))
