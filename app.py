import os
import platform
import time
import customtkinter as ctk

from constants.evaluation_questions import TEST_CONFIG
from screens.home import HomeScreen
from screens.select_type import SelectTypeScreen
from screens.admin_login import AdminLoginScreen
from screens.register import RegisterScreen
from screens.evaluator_list import EvaluatorListScreen
from screens.evaluator_login import EvaluatorLoginScreen
from screens.history import HistoryScreen
from screens.evaluator_edit import EvaluatorEditScreen
from screens.history_details import HistoryDetailScreen
from screens.comparison import ComparisonScreen
from screens.criteria import CriteriaScreen
from screens.after_save import AfterSaveScreen
from screens.pdf_preview import PdfPreviewScreen
from screens.test_assessor_login import AssessorLoginScreen
from screens.instructions import InstructionsScreen
from screens.test import TestScreen
from screens.research_results import ResultScreen

# Load font
here = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(here, "assets", "fonts", "THSarabunNew.ttf")
ctk.FontManager.load_font(font_path)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._perf_enabled = os.environ.get("MEDICAL_PERF", "").strip() not in ("", "0", "false", "False")
        self._perf_last_screen = None
        self.title("Medical Display Quality Control")
        
        system = platform.system()
        if system == "Windows":
            # ✅ เต็มพื้นที่แบบเสถียร (เหมือน maximize)
            self.state("zoomed")

        elif system == "Darwin":  # macOS
            # ✅ fullscreen จริง (ไม่มี menu bar)
            self.attributes("-fullscreen", True)

        elif system == "Linux":
            # Linux บาง distro fullscreen เพี้ยน → ใช้ zoomed ก่อน
            try:
                self.state("zoomed")
            except:
                self.attributes("-fullscreen", True)
        
        self.resizable(width=False, height=False)
        self.minsize(width=1280, height=720)
        self.configure(fg_color=("#F0F0F0", "#222222"))

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Register screens
        self.register_screens()
        self._preload_screens()

        # Show home screen
        self.show_screen("home")

    def _perf_log(self, message: str):
        if self._perf_enabled:
            print(f"[PERF] {message}")

    def _preload_screens(self):
        """Pre-create all screens at startup (trade startup time for runtime speed)."""
        t0 = time.perf_counter()
        for name, factory in (self.screen_definitions or {}).items():
            if name in self.screens:
                continue
            try:
                self.screens[name] = factory(master=self)
            except TypeError:
                # Some factories may not accept master as kwarg
                self.screens[name] = factory(self)

        # Optional warmup hook (implemented per-screen where needed)
        for s in self.screens.values():
            if hasattr(s, "warmup"):
                try:
                    s.warmup()
                except Exception:
                    # Warmup must never block app startup due to incidental failures
                    pass

        if self._perf_enabled:
            self._perf_log(f"preload_screens count={len(self.screens)} ms={(time.perf_counter() - t0) * 1000:.1f}")

    def handle_login(self, username, password):
        # ดึงฟังก์ชันเช็ครหัสผ่านที่เราเพิ่งทำไปมาใช้
        from database.database import verify_admin_login
        
        if verify_admin_login(username, password):
            self.show_screen("register")
        else:
            # ดึง instance หน้าจอที่ระบบจำไว้มาขอดู error
            if "admin_login" in self.screens:
                self.screens["admin_login"].show_error("Username หรือ Password ไม่ถูกต้อง")

    # Register screens
    def register_screens(self):
        # Lazy Loading
        self.screen_definitions = {
            "home": HomeScreen,
            "select_type": lambda master: SelectTypeScreen(
                master,
                back_command=self.go_back,
                confirm_command=self.handle_select_type
            ),
            "test_assessor_login": lambda master: AssessorLoginScreen(
                master,
                back_command=self.go_back,
                next_command=lambda: self.show_screen("instructions")
            ),
            "instructions": lambda master: InstructionsScreen(
                master,
                back_command=self.go_back,
                next_command=self.handle_start_test
            ),
            "test": lambda master: TestScreen(
                master,
                back_command=self.go_back,
            ),
            "admin_login": lambda master: AdminLoginScreen(master, login_command=self.handle_login),
            "register": lambda master: RegisterScreen(
                master,
                back_command=lambda: self.show_screen("admin_login"),
                save_hospital_command=self.handle_save_hospital,
                add_evaluator_command=self.handle_add_evaluator,
                # Admin ที่ตั้งค่าอยู่สามารถกดรายชื่อดูได้ทันทีโดยไม่ต้องไปติดด่านเช็ค Session
                view_evaluators_command=lambda: self.handle_view_evaluators(bypass_auth=True)
            ),
            "evaluator_login": lambda master: EvaluatorLoginScreen(
                master, 
                login_command=self.handle_evaluator_login
            ),
            "evaluator_list": lambda master: EvaluatorListScreen(
                master,
                back_command=self.go_back,
                delete_command=self.handle_delete_evaluator,
            ),
            "evaluator_edit": lambda master: EvaluatorEditScreen(
                master,
                back_command=self.go_back 
            ),
            "history": lambda master: HistoryScreen(
                master,
                back_command=self.go_back,
                detail_command=self.handle_view_history_detail,
                pdf_command=self.handle_export_history_records,
                search_command=lambda hospital, display_type, round_no, date_from="", date_to="": self.handle_view_history(
                    hospital, display_type, round_no, date_from=date_from, date_to=date_to, bypass_auth=True
                )
            ),
            "history_details": lambda master, **kwargs: HistoryDetailScreen(
                master,
                back_command=self.go_back,
                baseline_command=self.handle_open_baseline_comparison,
                export_command=self.handle_export_history_detail,
                **kwargs
            ),
            "comparison": lambda master, **kwargs: ComparisonScreen(
                master,
                back_command=self.handle_back_from_comparison,
                export_command=self.handle_export_comparison,
                **kwargs
            ),
            "criteria": lambda master, **kwargs: CriteriaScreen(
                master,
                back_command=self.go_back,
                **kwargs
            ),
            "after_save": lambda master, **kwargs: AfterSaveScreen(
                master,
                home_command=lambda: self.show_screen("home", bypass_auth=True),
                **kwargs
            ),
            "pdf_preview": lambda master, **kwargs: PdfPreviewScreen(
                master,
                back_command=self.go_back,
                **kwargs
            ),
            "research_results": lambda master, **kwargs: ResultScreen(
                master,
                retry_command=lambda: self.show_screen("test", bypass_auth=True),
                discard_command=lambda: self.show_screen("home", bypass_auth=True),
                save_command=self.handle_save_results,
                **kwargs
            ),
        }
        self.screens = {}  # Cache

    def handle_save_results(self, results):
        """บันทึกผลการประเมินลงฐานข้อมูล"""
        from database.database import get_eval_rank, get_evaluation, save_evaluation, set_as_baseline
        from services.session import get_session
        from datetime import datetime
        
        session = getattr(self, "test_session", {})
        evaluator = get_session()
        settings = self._get_settings()
        raw_answers = session.get("answers", {})

        db_answers = {}
        for item_id, answer in raw_answers.items():
            failed_values = answer.get("failed_levels", [])
            invisible_channels = answer.get("invisible_channels", [])
            failed_channels = invisible_channels or failed_values

            db_answers[item_id] = {
                "passed": answer.get("result") == "pass",
                "failed_channels": failed_channels,
                "notes": answer.get("note", ""),
            }

        overall_pass = all(ans.get("passed", False) for ans in db_answers.values()) if db_answers else False
        
        # สร้างข้อมูลสำหรับบันทึก
        evaluation_data = {
            "hospital_name": settings.get("hospital_name", ""),
            "screen_type": session.get("display_type", ""),
            "screen_model": settings.get("screen_model", ""),
            "period": session.get("period", ""),
            "evaluator_name": f"{evaluator.get('name', '')} {evaluator.get('lastname', '')}" if evaluator else "",
            "eval_datetime": datetime.now().isoformat(),
            "results": results,
            "answers": db_answers,
            "overall_pass": overall_pass,
        }
        
        eval_id = save_evaluation(evaluation_data)
        rank = get_eval_rank(session.get("display_type", ""), session.get("period", ""), eval_id)
        if rank == 1:
            set_as_baseline(eval_id)

        saved_evaluation = get_evaluation(eval_id)
        self.test_session["eval_id"] = eval_id
        self.test_session["saved_evaluation"] = saved_evaluation

        print(f"บันทึกผลการประเมินสำเร็จ")
        return {
            "evaluation_id": eval_id,
            "rank": rank,
            "is_first": rank == 1,
            "evaluation": saved_evaluation,
        }

    def _get_settings(self):
        """ดึงข้อมูล settings จากฐานข้อมูล"""
        from database.database import get_settings
        return get_settings() or {}

    def handle_save_hospital(self, name, serial):
        from database.database import save_settings
        save_settings(name, serial)
        print(f"บันทึกโรงพยาบาล: {name}, รหัส/รุ่น: {serial} สำเร็จ")

    def handle_add_evaluator(self, first, last, pw):
        from database.database import add_user
        err = add_user(first, last, pw)
        if err and "register" in self.screens:
            self.screens["register"].show_eval_error(err)
        else:
            print(f"เพิ่มผู้ประเมิน: {first} {last} สำเร็จ")
            if "register" in self.screens:
                self.screens["register"].clear_evaluator_fields()

    def handle_delete_evaluator(self, evaluator_data, evaluator_password="", admin_username="", admin_password=""):
        from database.database import delete_user, verify_admin_login, verify_user_password

        user_id = evaluator_data.get("id", 0)
        if not user_id:
            return "ไม่พบข้อมูลผู้ประเมิน"

        is_valid = False
        if evaluator_password:
            is_valid = verify_user_password(user_id, evaluator_password)
        elif admin_username and admin_password:
            is_valid = verify_admin_login(admin_username, admin_password)

        if not is_valid:
            return "รหัสยืนยันไม่ถูกต้อง"

        delete_user(user_id)
        self.handle_view_evaluators(bypass_auth=True)
        return None

    def handle_evaluator_login(self, display_name, password):
        from database.database import verify_login
        from services.session import set_evaluator_session
        
        user = verify_login(display_name, password)
        if user:
            # เก็บ JSON ลง session ตรวจสอบว่าเคยเข้าเวทีประเมินหรือยัง
            set_evaluator_session(user)
            
            # วาร์ปไปยังหน้าที่จำไว้ก่อนที่จะโดนเตะมาหน้า login หรือให้ไป select_type
            route = getattr(self, "pending_route", "select_type")
            if route == "evaluator_list_hook":
                self.handle_view_evaluators(bypass_auth=True)
            elif route == "history_hook":
                self.handle_view_history(bypass_auth=True)
            else:
                self.show_screen(route, bypass_auth=True)
        else:
            if "evaluator_login" in self.screens:
                self.screens["evaluator_login"].show_error("ชื่อ-นามสกุล หรือ รหัสผ่าน ไม่ถูกต้อง")

    def handle_view_evaluators(self, bypass_auth=False):
        from database.database import get_all_users
        users = get_all_users()
        
        # แปลงโครงสร้างข้อมูล (dict) จากตารางฐานข้อมูล ให้ตรงกับ format ที่ List Screen รอรับ (เพิ่ม id เพื่อใช้อ้างอิงการแก้ไข)
        mapped_evaluators = [{"id": user["id"], "first": user["name"], "last": user["lastname"]} for user in users]
        
        # แสดงหน้าต่าง
        self.show_screen("evaluator_list", bypass_auth=bypass_auth)
        
        # พอหน้าต่างแสดงขึ้นมาปุ๊บ ให้ยัดข้อมูล (inject) ใส่ตารางทันที
        if "evaluator_list" in self.screens:
            self.screens["evaluator_list"].set_evaluators(mapped_evaluators)

    def handle_view_history(self, hospital="", display_type="", round_no="", date_from="", date_to="", bypass_auth=False):
        from database.database import search_evaluations
        
        c_type = display_type or ""
        c_round = round_no or ""
        
        records = search_evaluations(
            hospital=hospital,
            screen_type=c_type,
            period=c_round,
            date_from=date_from,
            date_to=date_to,
        )
        
        mapped = []
        for r in records:
            dt = r.get("eval_datetime", "")
            dt_only = dt.split()[0] if dt else ""
            mapped.append({
                "id": r.get("id"),
                "rank": r.get("rank", 1),
                "date": dt_only,
                "hospital": r.get("hospital_name", ""),
                "display_type": r.get("screen_type", ""),
                "round": r.get("period", ""),
                "evaluator": r.get("evaluator_name", ""),
                "display_model": r.get("screen_model", "")
            })
            
        self.show_screen("history", bypass_auth=bypass_auth)
        
        if "history" in self.screens:
            self.screens["history"].set_records(mapped)

    def handle_view_history_detail(self, record):
        if not record:
            return
        self.show_screen("history_details", bypass_auth=True, evaluation_id=record.get("id"))

    def handle_open_baseline_comparison(self, current_evaluation, baseline_record):
        from database.database import get_evaluation

        if not current_evaluation or not baseline_record:
            return

        baseline_evaluation = get_evaluation(baseline_record.get("id"))
        if not baseline_evaluation:
            return

        self.show_screen(
            "comparison",
            bypass_auth=True,
            current_evaluation=current_evaluation,
            baseline_evaluation=baseline_evaluation,
        )

    def handle_export_history_detail(self, evaluation, results):
        from services.reports.pdf_builder import build_evaluation_pdf

        if not evaluation:
            return

        pdf_bytes = build_evaluation_pdf(evaluation, results or [])
        filename = self._make_pdf_filename(
            prefix="evaluation",
            hospital_name=evaluation.get("hospital_name", ""),
            suffix=evaluation.get("eval_datetime", ""),
        )
        self.show_screen(
            "pdf_preview",
            bypass_auth=True,
            pdf_bytes=pdf_bytes,
            title_text="Preview รายงานผลการประเมิน",
            default_filename=filename,
        )

    def handle_export_comparison(self, current_evaluation, baseline_evaluation, rows_data):
        from services.reports.pdf_builder import build_comparison_pdf

        if not current_evaluation or not baseline_evaluation:
            return

        pdf_bytes = build_comparison_pdf(current_evaluation, baseline_evaluation, rows_data or [])
        filename = self._make_pdf_filename(
            prefix="comparison",
            hospital_name=current_evaluation.get("hospital_name", ""),
            suffix=current_evaluation.get("eval_datetime", ""),
        )
        self.show_screen(
            "pdf_preview",
            bypass_auth=True,
            pdf_bytes=pdf_bytes,
            title_text="Preview รายงานเปรียบเทียบ Baseline",
            default_filename=filename,
        )

    def handle_export_history_records(self, records):
        from database.database import get_evaluation
        from services.reports.pdf_builder import build_evaluation_pdf
        from services.reports.pdf_merge import merge_pdf_bytes

        if not records:
            return

        if isinstance(records, dict):
            records = [records]

        evaluations = []
        for record in records:
            evaluation_id = record.get("id")
            if not evaluation_id:
                continue
            evaluation = get_evaluation(evaluation_id)
            if evaluation:
                evaluations.append(evaluation)

        if not evaluations:
            return

        pdf_documents = []
        for evaluation in evaluations:
            results = self._build_history_results(evaluation)
            pdf_documents.append(build_evaluation_pdf(evaluation, results))

        pdf_bytes = merge_pdf_bytes(pdf_documents)
        filename = self._make_pdf_filename(
            prefix="history_batch",
            hospital_name=evaluations[0].get("hospital_name", ""),
            suffix=evaluations[0].get("eval_datetime", ""),
        )
        self.show_screen(
            "pdf_preview",
            bypass_auth=True,
            pdf_bytes=pdf_bytes,
            title_text="Preview รายงานผลการประเมินหลายรายการ",
            default_filename=filename,
        )

    def handle_back_from_comparison(self, current_evaluation=None):
        if current_evaluation and current_evaluation.get("id"):
            self.show_screen(
                "history_details",
                bypass_auth=True,
                is_back=True,
                evaluation_id=current_evaluation.get("id"),
            )
            return
        self.go_back()

    def _make_pdf_filename(self, prefix, hospital_name, suffix):
        safe_hospital = (hospital_name or "report").replace(" ", "_")
        safe_suffix = (suffix or "").replace(":", "-").replace("/", "-").replace(" ", "_")
        return f"{prefix}_{safe_hospital}_{safe_suffix}.pdf".strip("_")

    def _build_history_results(self, evaluation):
        dtype = evaluation.get("screen_type", "")
        period = evaluation.get("period", "")
        answers = evaluation.get("answers", {})
        groups = TEST_CONFIG.get(dtype, {}).get(period, [])

        results = []
        for group in groups:
            items = group.get("items")
            if not items:
                continue

            section = {
                "section_title": group.get("group_title", ""),
                "items": [],
            }

            for item in items:
                item_id = item.get("item_id", "")
                answer = answers.get(item_id, {})
                passed = answer.get("passed")
                failed_channels = answer.get("failed_channels", [])
                notes = answer.get("notes", "") or ""
                question_type = item.get("question_type", "")

                if failed_channels:
                    failed_text = ", ".join(map(str, failed_channels))
                    if question_type == "yes_no_channels_text":
                        notes = f"ค่า pixel ที่ไม่ผ่าน: {failed_text}" if not notes else f"ค่า pixel ที่ไม่ผ่าน: {failed_text} | {notes}"
                    else:
                        notes = f"ช่องที่ไม่เห็น: {failed_text}" if not notes else f"ช่องที่ไม่เห็น: {failed_text} | {notes}"

                section["items"].append(
                    {
                        "title": item.get("title", ""),
                        "passed": passed,
                        "note": notes,
                    }
                )

            results.append(section)
        return results

    def handle_select_type(self, display_type: str, period: str):
        from services.session import get_session
        from database.database import get_settings

        display_type = "clinic" if display_type == "clinical" else display_type
        
        # เก็บ display_type และ period ไว้เพื่อใช้สร้าง test_items
        self._test_display_type = display_type
        self._test_period       = period
        
        session = get_session()
        if session:
            eval_name = f"{session.get('name', '')} {session.get('lastname', '')}".strip()
        else:
            eval_name = "ไม่พบข้อมูลผู้ประเมิน"
            
        settings = get_settings() or {}
        hospital_name = settings.get("hospital_name", "ไม่ได้ระบุ")
        serial_number = settings.get("screen_model", "ไม่ได้ระบุ")
        
        # แปลง Keyword ให้อ่านง่าย
        type_mapper = {
            "diagnostic": "Diagnostic",
            "modality": "Modality",
            "clinic": "Clinical Review & Electronic Health Record"
        }
        display_label = type_mapper.get(display_type, display_type)
        
        # แสดงหน้าจอ
        self.show_screen("test_assessor_login", bypass_auth=True)
        
        # ดันค่าเข้าหน้าจอ
        if "test_assessor_login" in self.screens:
            self.screens["test_assessor_login"].update_info(
                display_type=f"{display_label} {period}",
                hospital_name=hospital_name,
                serial_number=serial_number,
                evaluator_name=eval_name
            )

    def handle_start_test(self):
        """อ่าน config ตามชนิดจอ + รอบ แล้วเปิดหน้า test"""
        dtype  = getattr(self, "_test_display_type", "diagnostic")
        period_raw = getattr(self, "_test_period", "monthly")

        # แปลงชื่อภาษาไทยจาก UI → key ใน config
        period_map = {
            "การประเมินรายเดือน":    "monthly",
            "การประเมินราย 3 เดือน": "quarterly",
            "การประเมินรายปี":       "annual",
        }
        period = period_map.get(period_raw, period_raw)

        # เก็บ session ไว้ใน app (test.py จะอ่าน)
        self.test_session = {
            "display_type": dtype,
            "period":       period,
            "answers":      {},
        }

        self.show_screen("test", bypass_auth=True)

    def go_back(self):
        """วิทยายุทธดึงประวัติ ย้อนกลับหน้าล่าสุด"""
        if hasattr(self, "history") and self.history:
            prev = self.history.pop()
            self.show_screen(prev, bypass_auth=True, is_back=True)
        else:
            self.show_screen("home", bypass_auth=True)

    # Show function
    def show_screen(self, screen_name: str, bypass_auth=False, is_back=False, **kwargs):
        t0_total = time.perf_counter()
        # ── INTERCEPT PROTECTED ROUTES ── (ดักทุกหน้าต่างที่ต้องใช้สิทธิผู้ประเมิน)
        protected_routes = ["history", "history_hook", "evaluator_list", "evaluator_list_hook", "select_type", "evaluator_edit"]
        if screen_name in protected_routes and not bypass_auth:
            from services.session import is_evaluator_logged_in
            if not is_evaluator_logged_in():
                # จำไว้ว่าเป้าหมายสุดท้ายคือที่ไหน แล้วบังคับเลี้ยวไปหน้าล็อกอินผู้ประเมิน
                self.pending_route = screen_name
                screen_name = "evaluator_login"

        # ดักจับคำขอที่มาจากพฤติกรรม sidebar button hook (ซึ่งตอนนี้ถูกปลด auth มาแล้ว)
        if screen_name == "evaluator_list_hook":
            self.handle_view_evaluators(bypass_auth=True)
            return
            
        if screen_name == "history_hook":
            self.handle_view_history(bypass_auth=True)
            return
            
        # ── TRACK HISTORY ──
        if not is_back and getattr(self, "current_screen", None) and self.current_screen != screen_name:
            if not hasattr(self, "history"):
                self.history = []
            # ไม่แทรกหน้า Login ลงประวัติการเดินทาง (ป้องกันบักเตะวนลูป)
            if self.current_screen != "evaluator_login":
                if not self.history or self.history[-1] != self.current_screen:
                    self.history.append(self.current_screen)

        prev_screen_name = getattr(self, "current_screen", None)
        self.current_screen = screen_name

        # Lazy Loading
        t0_lazy = time.perf_counter()
        if screen_name not in self.screens:
            if screen_name in self.screen_definitions:
                self.screens[screen_name] = self.screen_definitions[screen_name](master=self)
            else:
                print(f"Error: Screen '{screen_name}' not registered.")
                return
        t1_lazy = time.perf_counter()

        screen = self.screens[screen_name]
        screen.grid(row=0, column=0, sticky="nsew")
        screen.lift()
        
        # Lifecycle: on_show
        t0_show = time.perf_counter()
        if hasattr(screen, "on_show"):
            screen.on_show(**kwargs)
        t1_show = time.perf_counter()
            
        t0_idle = time.perf_counter()
        self.update_idletasks()
        t1_idle = time.perf_counter()
        
        # Hide previous screen (and call its on_hide only)
        t0_hide = time.perf_counter()
        prev_screen = self.screens.get(prev_screen_name) if prev_screen_name else None
        if prev_screen is not None and prev_screen is not screen:
            if hasattr(prev_screen, "on_hide"):
                prev_screen.on_hide()
            prev_screen.grid_forget()

        # Hide all other screens without triggering lifecycle work
        for s in self.screens.values():
            if s is screen or s is prev_screen:
                continue
            s.grid_forget()
        t1_hide = time.perf_counter()

        t1_total = time.perf_counter()
        if self._perf_enabled:
            created = "hit" if (t1_lazy - t0_lazy) < 0.0005 else "miss"
            self._perf_log(
                "screen="
                f"{screen_name} prev={prev_screen_name} "
                f"lazy={created} "
                f"lazy_ms={(t1_lazy - t0_lazy) * 1000:.1f} "
                f"on_show_ms={(t1_show - t0_show) * 1000:.1f} "
                f"idle_ms={(t1_idle - t0_idle) * 1000:.1f} "
                f"hide_ms={(t1_hide - t0_hide) * 1000:.1f} "
                f"total_ms={(t1_total - t0_total) * 1000:.1f}"
            )

if __name__ == "__main__":
    app = App()
    app.mainloop()
