"""
ui/app.py — App: cửa sổ chính tích hợp màn hình cài đặt và màn hình game.

Module này chứa class ``App`` kế thừa ``tk.Tk``, là điểm kết nối giữa
tiểu hệ thống UI (``BoardView``, Sidebar Quiz) và lõi game (``GameController``).

Phản hồi yêu cầu của user, Quiz Dialog đã được gộp chung vào màn hình chính
bên phải bàn cờ (thành một sidebar) để tránh mở pop-up gây khó chịu.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os

from config import (
    BOARD_SIZES,
    DEFAULT_BOARD_SIZE,
    GAME_MODES,
    QUESTION_MODES,
    DIFFICULTY_DEPTH,
    GEMINI_API_KEY,
)
from core.game import GameController
from ui.board_view import BoardView
from ui.theme import (
    BG_DARK, BG_PANEL, BG_SURFACE,
    ACCENT, ACCENT2, COLOR_X, COLOR_O,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BUTTON,
    FONT_LABEL, FONT_STATUS, FONT_SMALL, BTN_PAD_X, BTN_PAD_Y,
)
from data.questions import (
    generate_math_question,
    generate_science_question,
    check_science_answer,
)


class App(tk.Tk):
    """Cửa sổ chính của ứng dụng Caro Logic.

    Quản lý hai màn hình:
    - **Setup Screen**: Chọn thông số.
    - **Game Screen (Hợp nhất)**: Hiển thị Panel Bàn Cờ bên trái và Panel Câu Hỏi bên phải.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("Caro Logic")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        
        # Lắng nghe sự kiện bấm dấu X mảng đóng cửa sổ
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._game_mode_var  = tk.StringVar(value="pvp")
        self._q_mode_var     = tk.StringVar(value="math")
        self._q_diff_var     = tk.StringVar(value="medium")
        self._ai_diff_var    = tk.StringVar(value="medium")
        self._board_size_var = tk.IntVar(value=DEFAULT_BOARD_SIZE)

        self._controller: GameController | None = None
        self._board_view:  BoardView | None = None

        # Trạng thái chờ trả lời câu hỏi
        self._pending_move: tuple[int, int] | None = None
        self._current_question: dict | None = None
        self._checking_answer: bool = False

        self._show_setup_screen()
        self.eval("tk::PlaceWindow . center")

    def _on_closing(self) -> None:
        """Đóng tất cả các window và ép buộc kết thúc mọi process ngầm."""
        self.destroy()
        os._exit(0)  # Đảm bảo multiprocessing pool và thread đều bị đóng

    # ════════════════════════════════════════════════════
    #  SETUP SCREEN
    # ════════════════════════════════════════════════════

    def _show_setup_screen(self) -> None:
        self._clear()
        frame = tk.Frame(self, bg=BG_DARK, padx=40, pady=30)
        frame.pack()

        tk.Label(frame, text="♟  CARO LOGIC", bg=BG_DARK, fg=ACCENT,
                 font=FONT_TITLE).pack(pady=(0, 4))
        tk.Label(frame, text="Sáng suốt — Chinh phục đối thủ",
                 bg=BG_DARK, fg=TEXT_MUTED, font=FONT_LABEL).pack(pady=(0, 24))

        self._section(frame, "Chế độ chơi")
        rf = tk.Frame(frame, bg=BG_DARK)
        rf.pack(fill="x", pady=(4, 14))
        for val, label in GAME_MODES.items():
            tk.Radiobutton(rf, text=label, variable=self._game_mode_var, value=val,
                           bg=BG_DARK, fg=TEXT_PRIMARY, selectcolor=BG_SURFACE,
                           activebackground=BG_DARK, font=FONT_BODY).pack(side="left", padx=8)

        self._section(frame, "Kích thước bàn cờ")
        sf = tk.Frame(frame, bg=BG_DARK)
        sf.pack(fill="x", pady=(4, 14))
        for sz in BOARD_SIZES:
            tk.Radiobutton(sf, text=f"{sz}×{sz}", variable=self._board_size_var, value=sz,
                           bg=BG_DARK, fg=TEXT_PRIMARY, selectcolor=BG_SURFACE,
                           activebackground=BG_DARK, font=FONT_BODY).pack(side="left", padx=8)

        self._section(frame, "Loại câu hỏi")
        qf = tk.Frame(frame, bg=BG_DARK)
        qf.pack(fill="x", pady=(4, 4))
        for val, label in QUESTION_MODES.items():
            tk.Radiobutton(qf, text=label, variable=self._q_mode_var, value=val,
                           bg=BG_DARK, fg=TEXT_PRIMARY, selectcolor=BG_SURFACE,
                           activebackground=BG_DARK, font=FONT_BODY).pack(side="left", padx=8)

        if not GEMINI_API_KEY:
            tk.Label(frame, text="⚠ Chưa cấu hình GEMINI_API_KEY — Khoa học sẽ không hoạt động",
                     bg=BG_DARK, fg=ACCENT, font=FONT_LABEL).pack(anchor="w", pady=(0, 8))

        self._section(frame, "Độ khó Câu hỏi")
        qdf = tk.Frame(frame, bg=BG_DARK)
        qdf.pack(fill="x", pady=(4, 14))
        for val in DIFFICULTY_DEPTH:
            tk.Radiobutton(qdf, text=val.capitalize(), variable=self._q_diff_var, value=val,
                           bg=BG_DARK, fg=TEXT_PRIMARY, selectcolor=BG_SURFACE,
                           activebackground=BG_DARK, font=FONT_BODY).pack(side="left", padx=8)

        self._section(frame, "Độ khó AI (nếu chơi với Máy)")
        adf = tk.Frame(frame, bg=BG_DARK)
        adf.pack(fill="x", pady=(4, 20))
        for val in DIFFICULTY_DEPTH:
            tk.Radiobutton(adf, text=val.capitalize(), variable=self._ai_diff_var, value=val,
                           bg=BG_DARK, fg=TEXT_PRIMARY, selectcolor=BG_SURFACE,
                           activebackground=BG_DARK, font=FONT_BODY).pack(side="left", padx=8)

        tk.Button(frame, text="▶  Bắt đầu trò chơi",
                  bg=ACCENT, fg="#ffffff", activebackground=ACCENT2,
                  font=FONT_BUTTON, relief="flat",
                  padx=BTN_PAD_X, pady=BTN_PAD_Y,
                  command=self._start_game).pack(fill="x")

    def _section(self, parent: tk.Widget, text: str) -> None:
        tk.Label(parent, text=text, bg=BG_DARK, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

    # ════════════════════════════════════════════════════
    #  GAME SCREEN
    # ════════════════════════════════════════════════════

    def _start_game(self) -> None:
        self._clear()  # Xóa màn hình cũ TRƯỚC khi tạo controller
        self._controller = GameController(
            mode          = self._game_mode_var.get(),
            q_mode        = self._q_mode_var.get(),
            ai_difficulty = self._ai_diff_var.get(),
            q_difficulty  = self._q_diff_var.get(),
            board_size    = self._board_size_var.get(),
        )
        self._build_game_screen()

    def _build_game_screen(self) -> None:
        """Xây dựng layout mới: Bảng điều khiển Quiz (Sidebar) bên phải bàn cờ."""
        ctrl = self._controller

        # Main Layout: 2 cột
        self._main_panes = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_DARK, bd=0, sashwidth=2)
        self._main_panes.pack(fill="both", expand=True)

        # ── Cột Trái: Bàn Cờ ──────────────────────────────────────────
        left_frame = tk.Frame(self._main_panes, bg=BG_DARK)
        self._main_panes.add(left_frame, minsize=400)

        # Top bar
        top = tk.Frame(left_frame, bg=BG_PANEL, padx=16, pady=10)
        top.pack(fill="x")
        tk.Label(top, text="♟ Caro Logic", bg=BG_PANEL, fg=ACCENT, font=FONT_SUBTITLE).pack(side="left")

        # Board
        board_container = tk.Frame(left_frame, bg=BG_DARK, pady=12)
        board_container.pack()
        self._board_view = BoardView(board_container, ctrl.board_size, self._on_cell_click)
        self._board_view.pack(padx=16, pady=8)

        # Status bar
        self._status_var = tk.StringVar()
        status_bar = tk.Frame(left_frame, bg=BG_PANEL, padx=16, pady=8)
        status_bar.pack(fill="x", side="bottom")
        self._status_dot = tk.Label(status_bar, text="●", bg=BG_PANEL, fg=COLOR_X, font=FONT_STATUS)
        self._status_dot.pack(side="left")
        tk.Label(status_bar, textvariable=self._status_var, bg=BG_PANEL, fg=TEXT_PRIMARY, font=FONT_LABEL).pack(side="left", padx=6)

        # ── Cột Phải: Sidebar Quiz & Điều Khiển ───────────────────────
        right_frame = tk.Frame(self._main_panes, bg=BG_PANEL, width=320, padx=16, pady=16)
        self._main_panes.add(right_frame, minsize=300)

        # Info
        info = f"{GAME_MODES[ctrl.mode]}\nCâu hỏi: {ctrl.q_difficulty.capitalize()}  |  AI: {ctrl.ai_difficulty.capitalize()}"
        tk.Label(right_frame, text=info, bg=BG_PANEL, fg=TEXT_MUTED, font=FONT_LABEL, justify="left").pack(anchor="w", pady=(0, 20))

        # Box hiển thị câu hỏi
        self._quiz_box = tk.Frame(right_frame, bg=BG_SURFACE, padx=12, pady=12)
        self._quiz_box.pack(fill="x", pady=(0, 20))

        self._q_hdr_var = tk.StringVar(value="Hãy chọn 1 ô để đánh cờ")
        self._q_hdr_lbl = tk.Label(self._quiz_box, textvariable=self._q_hdr_var, bg=BG_SURFACE, fg=ACCENT, font=FONT_SUBTITLE)
        self._q_hdr_lbl.pack(anchor="w", pady=(0, 8))

        self._q_var = tk.StringVar(value="")
        tk.Label(self._quiz_box, textvariable=self._q_var, bg=BG_SURFACE, fg=TEXT_PRIMARY, font=FONT_BODY, wraplength=230, justify="left").pack(anchor="w", pady=(0, 6))

        # Ô nhập đáp án
        self._entry_frame = tk.Frame(self._quiz_box, bg=BG_PANEL, padx=2, pady=2)
        self._entry = tk.Entry(self._entry_frame, font=FONT_BODY, bg=BG_PANEL, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, relief="flat", bd=4)
        self._entry.pack(fill="x")
        self._entry.bind("<Return>", lambda _: self._on_quiz_submit())
        
        self._feedback_var = tk.StringVar()
        self._feedback_lbl = tk.Label(self._quiz_box, textvariable=self._feedback_var, bg=BG_SURFACE, fg=ACCENT, font=FONT_SMALL, wraplength=230, justify="left")

        # Nút Quiz
        self._quiz_btn_frame = tk.Frame(self._quiz_box, bg=BG_SURFACE)
        
        self._submit_btn = tk.Button(self._quiz_btn_frame, text="Trả lời ✓", bg=ACCENT, fg="#ffffff", activebackground=ACCENT2, font=FONT_BUTTON, relief="flat", command=self._on_quiz_submit)
        self._submit_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        self._reroll_btn = tk.Button(self._quiz_btn_frame, text="Đổi câu", bg=BG_DARK, fg=TEXT_SECONDARY, activebackground=BG_PANEL, font=FONT_LABEL, relief="flat", command=self._on_quiz_reroll)
        self._reroll_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))

        self._cancel_btn = tk.Button(self._quiz_box, text="Bỏ chọn ô", bg=BG_DARK, fg=TEXT_MUTED, font=FONT_LABEL, relief="flat", command=self._cancel_quiz)

        # Loading bar (ẩn mặc định, hiện khi chờ API)
        self._progress = ttk.Progressbar(self._quiz_box, mode="indeterminate")

        # App controls
        tk.Button(right_frame, text="🔄 Chơi ván mới", bg=BG_SURFACE, fg=TEXT_PRIMARY, relief="flat", font=FONT_LABEL, pady=6, command=self._new_game).pack(fill="x", side="bottom", pady=(8, 0))
        tk.Button(right_frame, text="🏠 Về Menu chính", bg=BG_SURFACE, fg=TEXT_PRIMARY, relief="flat", font=FONT_LABEL, pady=6, command=self._show_setup_screen).pack(fill="x", side="bottom")

        # Knowledge box (Nằm dưới phần Quiz)
        self._know_box = tk.Frame(right_frame, bg=BG_SURFACE, padx=12, pady=12)
        tk.Label(self._know_box, text="📖 Kiến thức bổ sung", bg=BG_SURFACE, fg=ACCENT, font=FONT_SUBTITLE).pack(anchor="w", pady=(0, 8))
        self._know_var = tk.StringVar(value="")
        tk.Label(self._know_box, textvariable=self._know_var, bg=BG_SURFACE, fg=TEXT_PRIMARY, font=FONT_BODY, wraplength=230, justify="left").pack(anchor="w")

        self._reset_quiz_ui()
        self._update_status()
        if ctrl.is_ai_turn():
            self._trigger_ai()

    def _update_status(self) -> None:
        ctrl = self._controller
        if ctrl is None:
            return
        color = COLOR_X if ctrl.player == "X" else COLOR_O
        self._status_dot.config(fg=color)
        if ctrl.is_ai_turn():
            self._status_var.set("Máy tính đang suy nghĩ...")
        else:
            if self._pending_move:
                self._status_var.set(f"Đang chờ [{ctrl.player}] giải đố để đặt cờ!")
            else:
                self._status_var.set(f"Lượt của [{ctrl.player}] — Hãy click một ô trên bàn cờ")

    # ── Game Flow / Board Click ───────────────────────────────────────────

    def _on_cell_click(self, r: int, c: int) -> None:
        ctrl = self._controller
        if ctrl is None or ctrl.game_over or ctrl.is_ai_turn():
            return
            
        if getattr(self, "_checking_answer", False):
            return
            
        if self._pending_move == (r, c):
            return
        
        self._pending_move = (r, c)
        
        if ctrl.q_mode == "none":
            self._handle_correct_answer()
            return
            
        self._board_view.set_pending(r, c)
        self._update_status()

        # Hiển thị UI giải đố
        self._q_hdr_var.set(f"Thử thách cho [{ctrl.player}]")
        self._q_hdr_lbl.config(fg=COLOR_X if ctrl.player == "X" else COLOR_O)
        self._entry_frame.pack(fill="x", pady=(12, 6))
        self._feedback_lbl.pack(anchor="w", pady=(0, 6))
        self._quiz_btn_frame.pack(fill="x", pady=(6, 8))
        self._cancel_btn.pack(fill="x")
        self._entry.focus_set()

        self._generate_and_show_question()

    def _generate_and_show_question(self) -> None:
        self._set_loading(True)
        self._feedback_var.set("")
        self._entry.delete(0, "end")
        
        self._question_req_id = getattr(self, "_question_req_id", 0) + 1
        req_id = self._question_req_id
        
        if hasattr(self, "_know_box"):
            self._know_box.pack_forget()
        
        def _bg_gen():
            q = generate_math_question(self._controller.q_difficulty) if self._controller.q_mode == "math" else generate_science_question(self._controller.q_difficulty)
            self.after(0, lambda: self._apply_question(q, req_id))
            
        threading.Thread(target=_bg_gen, daemon=True).start()

    def _apply_question(self, q: dict | None, req_id: int) -> None:
        if getattr(self, "_question_req_id", 0) != req_id:
            return
        self._set_loading(False)
        if q is None:
            self._feedback_var.set("⚠ Lỗi tải câu hỏi. Hãy ấn Đổi câu.")
            return

        self._current_question = q
        self._q_var.set(q.get("q", ""))

    # ── Quiz Actions ──────────────────────────────────────────────────────

    def _on_quiz_submit(self) -> None:
        if self._checking_answer or not self._current_question or not self._pending_move:
            return
            
        ans = self._entry.get().strip()
        if not ans:
            return

        ctrl = self._controller
        if ctrl.q_mode == "math":
            try:
                correct = int(ans) == self._current_question["a"]
            except ValueError:
                self._feedback_var.set("⚠ Chỉ nhập số nguyên!")
                self._entry.select_range(0, "end")
                return

            if correct:
                explanation = f"Phép toán: {self._current_question['display']}\nĐáp án đúng: {self._current_question['a']}"
                self._handle_correct_answer(explanation)
            else:
                self._feedback_var.set("❌ Sai rồi! Hãy thử lại.")
                self._entry.delete(0, "end")
                self._entry.focus_set()
        else:
            self._set_loading(True)
            threading.Thread(
                target=self._check_science_async, args=(None, self._current_question["q"], ans), daemon=True
            ).start()

    def _check_science_async(self, dummy, q_text: str, ans: str) -> None:
        correct, explanation = check_science_answer(q_text, ans)
        self.after(0, lambda: self._on_science_result(correct, explanation))

    def _on_science_result(self, correct: bool, explanation: str) -> None:
        self._set_loading(False)
        if correct:
            self._handle_correct_answer(explanation)
        else:
            self._feedback_var.set("❌ Sai rồi! Hãy thử lại.")
            self._entry.delete(0, "end")
            self._entry.focus_set()

    def _handle_correct_answer(self, explanation: str = "") -> None:
        """User trả lời đúng -> Đặt cờ -> Chuyển lượt"""
        if not self._pending_move or not self._controller: return
        r, c = self._pending_move
        ctrl = self._controller

        result = ctrl.make_move(r, c)
        self._board_view.place_piece(r, c, ctrl.player)
        
        if getattr(self, "_know_box", None) and explanation:
            self._know_var.set(explanation)
            self._know_box.pack(fill="x", pady=(0, 20))
            
        self._reset_quiz_ui()

        if result["win"]:
            self._board_view.highlight_winner(result["winning_cells"])
            who = "Máy tính" if (ctrl.mode == "pvc" and ctrl.winner == "O") else f"Người chơi [{ctrl.winner}]"
            messagebox.showinfo("🎉 Chiến thắng!", f"{who} đã chiến thắng!")
            return
        elif result["draw"]:
            messagebox.showinfo("⚖ Hòa!", "Bàn cờ đầy — Hai bên hòa nhau!")
            return

        ctrl.finish_move()
        self._update_status()

        if ctrl.is_ai_turn():
            self._trigger_ai()

    def _on_quiz_reroll(self) -> None:
        if self._checking_answer: return
        self._generate_and_show_question()

    def _cancel_quiz(self) -> None:
        """Hủy nước đi hiện tại, trở về chọn ô"""
        if self._checking_answer: return
        self._reset_quiz_ui()
        self._update_status()

    def _reset_quiz_ui(self) -> None:
        self._pending_move = None
        self._current_question = None
        if hasattr(self, "_board_view") and self._board_view:
            self._board_view.set_pending(None, None)
            
        if not hasattr(self, "_q_hdr_var"):
            return
            
        self._q_hdr_var.set("Hãy chọn 1 ô để đánh cờ")
        self._q_hdr_lbl.config(fg=TEXT_SECONDARY)
        self._q_var.set("")
        self._entry_frame.pack_forget()
        self._feedback_lbl.pack_forget()
        self._quiz_btn_frame.pack_forget()
        self._cancel_btn.pack_forget()
        self._progress.pack_forget()

    def _set_loading(self, loading: bool) -> None:
        self._checking_answer = loading
        if loading:
            self._submit_btn.config(state="disabled")
            self._reroll_btn.config(state="disabled")
            self._cancel_btn.config(state="disabled")
            self._progress.pack(fill="x", pady=(8, 0))
            self._progress.start(12)
        else:
            self._submit_btn.config(state="normal")
            self._reroll_btn.config(state="normal")
            self._cancel_btn.config(state="normal")
            self._progress.stop()
            self._progress.pack_forget()

    # ── AI Flow ───────────────────────────────────────────────────────────

    def _trigger_ai(self) -> None:
        ctrl = self._controller
        if ctrl is None or ctrl.game_over: return
        self._board_view.set_disabled(True)
        self.after(400, self._ai_move_step)

    def _ai_move_step(self) -> None:
        ctrl = self._controller
        if ctrl is None or ctrl.game_over: return

        r, c = ctrl.get_ai_move()
        result = ctrl.make_move(r, c)
        self._board_view.place_piece(r, c, ctrl.player)

        if result["win"]:
            self._board_view.highlight_winner(result["winning_cells"])
            messagebox.showinfo("🤖 Máy thắng!", "Máy tính đã chiến thắng!")
            return
        elif result["draw"]:
            messagebox.showinfo("⚖ Hòa!", "Bàn cờ đầy — Hai bên hòa nhau!")
            return

        ctrl.finish_move()
        self._update_status()
        self._board_view.set_disabled(False)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _new_game(self) -> None:
        if self._controller: self._controller.reset()
        if self._board_view: self._board_view.reset()
        if hasattr(self, "_know_box"):
            self._know_box.pack_forget()
        self._reset_quiz_ui()
        self._update_status()
        if self._controller and self._controller.is_ai_turn():
            self._trigger_ai()

    def _clear(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._board_view = None
        self._controller = None
