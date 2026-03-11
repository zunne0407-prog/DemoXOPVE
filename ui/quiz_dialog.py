"""
ui/quiz_dialog.py — QuizDialog: popup hỏi đáp dark-theme tùy chỉnh.

Luật:
    - Trả lời sai → hiện thông báo, giữ dialog mở, cho thử lại vô hạn (không mất lượt).
    - Người chơi có thể đổi câu (tối đa ``MAX_REROLLS`` lần) nếu thấy quá khó.
    - Dialog chỉ đóng khi trả lời ĐÚNG hoặc ấn "Bỏ qua" (cancel).
    - Với mode science, việc chấm điểm được thực hiện bất đồng bộ (thread riêng)
      để không block UI trong khi chờ Gemini API.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import threading

from ui.theme import (
    BG_PANEL, BG_SURFACE, BG_DARK,
    ACCENT, ACCENT2, COLOR_X, COLOR_O,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    FONT_SUBTITLE, FONT_BODY, FONT_SMALL,
    FONT_BUTTON, FONT_LABEL, BTN_PAD_X, BTN_PAD_Y,
)
from config import MAX_REROLLS


def ask_question(
    parent: tk.Widget,
    player: str,
    question: dict,
    q_mode: str,
    difficulty: str,
    generate_fn,
    check_fn=None,
) -> tuple[bool, bool]:
    """Mở dialog hỏi đáp và chờ cho đến khi người dùng trả lời đúng hoặc cancel.

    Hàm này blocking — nó sử dụng ``parent.wait_window()`` để giữ luồng
    chính cho đến khi cửa sổ dialog đóng.

    Args:
        parent (tk.Widget): Widget cha, dùng làm điểm tham chiếu để căn giữa dialog.
        player (str): Ký hiệu người chơi hiện tại (``"X"`` hoặc ``"O"``),
            dùng để set màu header.
        question (dict): Câu hỏi ban đầu với cấu trúc ``{"q": str, "a": int|str, ...}``.
        q_mode (str): Chế độ câu hỏi — ``"math"`` hoặc ``"science"``.
        difficulty (str): Mức độ khó, ảnh hưởng đến câu hỏi sinh mới khi đổi câu.
        generate_fn (Callable[[], dict | None]): Hàm không tham số để sinh câu hỏi mới
            khi người dùng ấn "Đổi câu". Trả về dict câu hỏi hoặc ``None`` nếu thất bại.
        check_fn (Callable[[str, str], tuple[bool, str]] | None): Hàm chấm điểm
            cho mode science. Nhận ``(question_text, user_answer)`` và trả về
            ``(correct: bool, explanation: str)``. Để ``None`` nếu không dùng mode science.

    Returns:
        tuple[bool, bool]: Cặp ``(answered_correctly, cancelled)`` trong đó:
            - ``answered_correctly`` (bool): ``True`` nếu người dùng trả lời đúng.
              Khi ``cancelled=False``, giá trị này luôn là ``True`` vì dialog
              chỉ đóng khi trả lời đúng.
            - ``cancelled`` (bool): ``True`` nếu người dùng ấn "Bỏ qua" hoặc
              đóng cửa sổ mà không trả lời đúng.
    """
    dlg = _QuizDialog(parent, player, question, q_mode, difficulty, generate_fn, check_fn)
    parent.wait_window(dlg.window)
    return dlg.result_correct, dlg.result_cancelled


class _QuizDialog:
    """Internal dialog widget — không dùng trực tiếp, dùng qua ``ask_question()``.

    Attributes:
        result_correct (bool): ``True`` nếu người dùng trả lời đúng khi đóng dialog.
        result_cancelled (bool): ``True`` nếu người dùng cancel mà không trả lời đúng.
        window (tk.Toplevel): Cửa sổ Toplevel của dialog.
    """

    def __init__(
        self,
        parent: tk.Widget,
        player: str,
        question: dict,
        q_mode: str,
        difficulty: str,
        generate_fn,
        check_fn,
    ) -> None:
        """Khởi tạo và hiển thị dialog câu hỏi.

        Args:
            parent (tk.Widget): Widget cha.
            player (str): Ký hiệu người chơi (``"X"`` hoặc ``"O"``).
            question (dict): Câu hỏi ban đầu.
            q_mode (str): Chế độ câu hỏi (``"math"`` hoặc ``"science"``).
            difficulty (str): Mức độ khó.
            generate_fn (Callable[[], dict | None]): Hàm sinh câu hỏi mới.
            check_fn (Callable | None): Hàm chấm điểm (chỉ dùng mode science).
        """
        self.parent = parent
        self.player = player
        self.question = question
        self.q_mode = q_mode
        self.difficulty = difficulty
        self.generate_fn = generate_fn
        self.check_fn = check_fn
        # Không giới hạn số lần đổi câu
        self.result_correct = False
        self.result_cancelled = False
        self._checking = False
        self._build()

    def _build(self) -> None:
        """Xây dựng toàn bộ layout giao diện dialog bao gồm header, body và buttons."""
        color = COLOR_X if self.player == "X" else COLOR_O
        w = tk.Toplevel(self.parent)
        w.withdraw()
        w.configure(bg=BG_PANEL)
        w.resizable(False, False)
        w.grab_set()
        w.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.window = w

        # Header
        hdr = tk.Frame(w, bg=color, padx=16, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"Thử thách [{self.player}]",
                 bg=color, fg=BG_DARK, font=FONT_SUBTITLE).pack(side="left")
        mode_lbl = "📐 Toán học" if self.q_mode == "math" else "🔬 Khoa học"
        tk.Label(hdr, text=mode_lbl,
                 bg=color, fg=BG_DARK, font=FONT_SMALL).pack(side="right")

        # Body
        body = tk.Frame(w, bg=BG_PANEL, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        self._q_var = tk.StringVar(value=self.question.get("q", ""))
        tk.Label(body, textvariable=self._q_var, bg=BG_PANEL, fg=TEXT_PRIMARY,
                 font=FONT_BODY, wraplength=420, justify="left").pack(anchor="w", pady=(0, 6))

        self._hint_var = tk.StringVar()
        if self.q_mode == "science" and self.question.get("hint"):
            self._hint_var.set(f"💡 {self.question['hint']}")
        tk.Label(body, textvariable=self._hint_var, bg=BG_PANEL, fg=TEXT_MUTED,
                 font=FONT_SMALL, wraplength=420, justify="left").pack(anchor="w", pady=(0, 10))

        entry_frame = tk.Frame(body, bg=BG_SURFACE, padx=2, pady=2)
        entry_frame.pack(fill="x", pady=(0, 12))
        self._entry = tk.Entry(entry_frame, font=FONT_BODY, bg=BG_SURFACE,
                               fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                               relief="flat", bd=6)
        self._entry.pack(fill="x")
        self._entry.bind("<Return>", lambda _: self._on_submit())

        self._feedback_var = tk.StringVar()
        tk.Label(body, textvariable=self._feedback_var, bg=BG_PANEL, fg=ACCENT,
                 font=FONT_SMALL, wraplength=420).pack(anchor="w", pady=(0, 10))

        # Buttons
        btn_frame = tk.Frame(body, bg=BG_PANEL)
        btn_frame.pack(fill="x")

        self._submit_btn = tk.Button(
            btn_frame, text="Trả lời ✓",
            bg=ACCENT, fg=TEXT_PRIMARY, activebackground=ACCENT2,
            font=FONT_BUTTON, relief="flat",
            padx=BTN_PAD_X, pady=BTN_PAD_Y,
            command=self._on_submit,
        )
        self._submit_btn.pack(side="left", padx=(0, 8))

        self._reroll_btn = tk.Button(
            btn_frame, text="Đổi câu",
            bg=BG_SURFACE, fg=TEXT_SECONDARY, activebackground=BG_PANEL,
            font=FONT_LABEL, relief="flat",
            padx=12, pady=BTN_PAD_Y,
            command=self._on_reroll,
        )
        self._reroll_btn.pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame, text="Bỏ qua",
            bg=BG_DARK, fg=TEXT_MUTED, activebackground=BG_PANEL,
            font=FONT_LABEL, relief="flat",
            padx=12, pady=BTN_PAD_Y,
            command=self._on_cancel,
        ).pack(side="right")

        # Loading bar (ẩn mặc định, hiện khi chờ API)
        self._progress = ttk.Progressbar(w, mode="indeterminate", length=200)

        # Căn giữa dialog so với cửa sổ cha
        w.update_idletasks()
        px = self.parent.winfo_rootx() + (self.parent.winfo_width() - w.winfo_width()) // 2
        py = self.parent.winfo_rooty() + (self.parent.winfo_height() - w.winfo_height()) // 2
        w.geometry(f"+{px}+{py}")
        w.deiconify()
        self._entry.focus_set()

    # ── Actions ───────────────────────────────────────────────────────────

    def _on_submit(self) -> None:
        """Xử lý khi người dùng ấn nút "Trả lời" hoặc Enter.

        - Mode math: so sánh int, giữ dialog mở nếu sai.
        - Mode science: gửi đáp án lên Gemini API trong thread riêng.
        """
        if self._checking:
            return
        ans = self._entry.get().strip()
        if not ans:
            return

        if self.q_mode == "math":
            try:
                correct = int(ans) == self.question["a"]
            except ValueError:
                self._feedback_var.set("⚠ Chỉ nhập số nguyên!")
                self._entry.select_range(0, "end")
                return

            if correct:
                self.result_correct = True
                self.window.destroy()
            else:
                self._feedback_var.set("❌ Sai rồi! Hãy thử lại.")
                self._entry.delete(0, "end")
                self._entry.focus_set()
        else:
            self._set_loading(True)
            threading.Thread(
                target=self._check_science_async, args=(ans,), daemon=True
            ).start()

    def _check_science_async(self, ans: str) -> None:
        """Gọi API chấm điểm trong thread riêng để không block UI.

        Args:
            ans (str): Đáp án người dùng nhập vào.
        """
        correct, explanation = self.check_fn(self.question["q"], ans)
        self.window.after(0, lambda: self._on_science_result(correct, explanation))

    def _on_science_result(self, correct: bool, explanation: str) -> None:
        """Xử lý kết quả trả về từ Gemini API sau khi chấm điểm.

        Nếu đúng: đóng dialog sau delay. Nếu sai: giữ dialog mở, hiện giải thích.

        Args:
            correct (bool): Kết quả chấm điểm từ Gemini.
            explanation (str): Giải thích kèm đáp án đúng (nếu sai).
        """
        self._set_loading(False)
        if correct:
            self._feedback_var.set("✅ " + explanation)
            self.result_correct = True
            self._submit_btn.config(state="disabled")
            self.window.after(1600, self.window.destroy)
        else:
            self._feedback_var.set("❌ Sai rồi! Hãy thử lại.")
            self._entry.delete(0, "end")
            self._entry.focus_set()

    def _on_reroll(self) -> None:
        """Xử lý khi người dùng ấn "Đổi câu" (không giới hạn số lần).

        Xóa input và feedback, rồi sinh câu hỏi mới.
        Với mode science, việc sinh câu mới được thực hiện bất đồng bộ.
        """
        if self._checking:
            return
        self._feedback_var.set("")
        self._entry.delete(0, "end")
        self._submit_btn.config(state="normal")

        if self.q_mode == "math":
            new_q = self.generate_fn()
            self._apply_question(new_q)
        else:
            self._set_loading(True)
            threading.Thread(
                target=self._reroll_science_async, daemon=True
            ).start()

    def _reroll_science_async(self) -> None:
        """Sinh câu hỏi science mới trong thread riêng khi người dùng đổi câu."""
        new_q = self.generate_fn()
        self.window.after(0, lambda: self._on_reroll_done(new_q))

    def _on_reroll_done(self, new_q: dict | None) -> None:
        """Xử lý câu hỏi mới trả về sau khi gọi API để đổi câu.

        Args:
            new_q (dict | None): Câu hỏi mới từ API, hoặc ``None`` nếu thất bại.
        """
        self._set_loading(False)
        if new_q:
            self._apply_question(new_q)
        else:
            self._feedback_var.set("⚠ Không thể tải câu hỏi mới.")

    def _apply_question(self, q: dict) -> None:
        """Cập nhật nội dung dialog với câu hỏi mới.

        Args:
            q (dict): Câu hỏi mới cần hiển thị, với ít nhất key ``"q"``
                và tùy chọn ``"hint"``.
        """
        self.question = q
        self._q_var.set(q.get("q", ""))
        hint = q.get("hint", "")
        self._hint_var.set(f"💡 {hint}" if hint else "")

    def _on_cancel(self) -> None:
        """Xử lý khi người dùng đóng dialog mà không trả lời đúng.

        Đặt ``result_cancelled = True`` và đóng cửa sổ.
        """
        self.result_cancelled = True
        self.window.destroy()

    def _set_loading(self, loading: bool) -> None:
        """Hiện hoặc ẩn thanh progress bar và quản lý trạng thái nút.

        Args:
            loading (bool): ``True`` để hiện loading spinner và disable buttons,
                ``False`` để ẩn spinner và kích hoạt lại buttons.
        """
        self._checking = loading
        if loading:
            self._progress.pack(pady=(0, 8))
            self._progress.start(12)
            self._submit_btn.config(state="disabled")
            self._reroll_btn.config(state="disabled")
        else:
            self._progress.stop()
            self._progress.pack_forget()
            self._submit_btn.config(state="normal")
            if self.rerolls_left > 0:
                self._reroll_btn.config(state="normal")
