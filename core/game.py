"""
core/game.py — GameController: điều phối luật chơi và lượt đi.

Module này cung cấp class ``GameController`` là lớp trung gian giữa UI và
các module ``BoardState`` / ``AIPlayer``. Nó quản lý lượt chơi, chế độ game
và cung cấp kết quả sau mỗi nước đi.
"""
from config import GAME_MODES, QUESTION_MODES, DIFFICULTY_DEPTH
from core.board import BoardState
from core.ai import AIPlayer


class GameController:
    """Điều phối toàn bộ luồng game Caro.

    Quản lý trạng thái người chơi hiện tại, chế độ game (PvP / PvC),
    chế độ câu hỏi và giao tiếp với ``BoardState`` và ``AIPlayer``.

    Attributes:
        mode (str): Chế độ game — ``"pvp"`` (Người vs Người) hoặc ``"pvc"`` (Người vs Máy).
        q_mode (str): Chế độ câu hỏi — ``"math"`` hoặc ``"science"``.
        ai_difficulty (str): Mức độ khó của AI — ``"easy"``, ``"medium"``, ``"hard"``.
        q_difficulty (str): Mức độ khó của câu hỏi — ``"easy"``, ``"medium"``, ``"hard"``.
        board_size (int): Kích thước bàn cờ (số hàng = số cột).
        board (BoardState): Đối tượng quản lý trạng thái bàn cờ.
        ai (AIPlayer | None): Đối tượng AI, ``None`` nếu chế độ PvP.
        player (str): Ký hiệu người chơi đang đến lượt (``"X"`` hoặc ``"O"``).
        game_over (bool): ``True`` nếu ván cờ đã kết thúc.
        winner (str | None): Ký hiệu người thắng, hoặc ``None`` nếu chưa có.
    """

    PLAYERS: tuple[str, str] = ("X", "O")

    def __init__(
        self,
        mode: str = "pvp",
        q_mode: str = "math",
        ai_difficulty: str = "medium",
        q_difficulty: str = "medium",
        board_size: int = 10,
    ) -> None:
        """Khởi tạo GameController với các cài đặt ván chơi.

        Args:
            mode (str): Chế độ game. ``"pvp"`` hoặc ``"pvc"``. Mặc định ``"pvp"``.
            q_mode (str): Chế độ câu hỏi. ``"math"`` hoặc ``"science"``. Mặc định ``"math"``.
            ai_difficulty (str): Mức độ khó của AI (nếu chế độ pvc).
                Một trong ``"easy"``, ``"medium"``, ``"hard"``. Mặc định ``"medium"``.
            q_difficulty (str): Mức độ khó của câu hỏi.
                Một trong ``"easy"``, ``"medium"``, ``"hard"``. Mặc định ``"medium"``.
            board_size (int): Kích thước bàn cờ n×n. Mặc định ``10``.
        """
        self.mode = mode
        self.q_mode = q_mode
        self.ai_difficulty = ai_difficulty
        self.q_difficulty = q_difficulty
        self.board_size = board_size

        self.board = BoardState(board_size)
        self.ai = AIPlayer(ai_difficulty) if mode == "pvc" else None

        self.player: str = "X"
        self.game_over: bool = False
        self.winner: str | None = None

    # ── Turn management ───────────────────────────────────────────────────

    def make_move(self, r: int, c: int) -> dict:
        """Đặt quân của ``self.player`` tại ô (r, c) và kiểm tra kết quả.

        Phương thức này chỉ thực hiện nước đi và trả về kết quả.
        Việc chuyển lượt phải được thực hiện bằng cách gọi ``finish_move()``
        sau khi xử lý kết quả.

        Args:
            r (int): Hàng của ô được chọn (0-indexed).
            c (int): Cột của ô được chọn (0-indexed).

        Returns:
            dict: Kết quả nước đi với cấu trúc::

                {
                    "win":           bool,              # True nếu người hiện tại thắng
                    "draw":          bool,              # True nếu hòa (bàn cờ đầy)
                    "winning_cells": list[tuple[int, int]]  # Danh sách ô thắng (rỗng nếu chưa thắng)
                }
        """
        self.board.place(r, c, self.player)
        result: dict = {"win": False, "draw": False, "winning_cells": []}

        if self.board.check_win_at(self.player, r, c):
            result["win"] = True
            result["winning_cells"] = self.board.get_winning_cells(self.player)
            self.winner = self.player
            self.game_over = True
        elif self.board.check_draw():
            result["draw"] = True
            self.game_over = True

        return result

    def finish_move(self) -> None:
        """Chuyển lượt sang người chơi kế tiếp sau khi ``make_move()`` thành công.

        Không làm gì nếu ``game_over`` là ``True``.
        Phải được gọi sau ``make_move()`` và sau khi đã xử lý hiển thị UI.
        """
        if not self.game_over:
            self._switch_player()

    def is_ai_turn(self) -> bool:
        """Kiểm tra xem đây có phải lượt của AI không.

        Returns:
            bool: ``True`` nếu chế độ PvC và người chơi hiện tại là ``"O"`` (AI),
                ``False`` trong mọi trường hợp khác.
        """
        return self.mode == "pvc" and self.player == "O"

    def get_ai_move(self) -> tuple[int, int]:
        """Yêu cầu AI tính toán và trả về nước đi tốt nhất.

        Raises:
            AssertionError: Nếu ``self.ai`` là ``None`` (chế độ PvP).

        Returns:
            tuple[int, int]: Tọa độ (row, col) mà AI muốn đặt quân.
        """
        assert self.ai is not None, "Không có AI trong chế độ PvP."
        return self.ai.choose_move(self.board)

    def reset(self) -> None:
        """Đặt lại ván chơi về trạng thái ban đầu.

        Xóa toàn bộ quân cờ, đặt lại người chơi về ``"X"``,
        xóa ``winner`` và đặt ``game_over`` về ``False``.
        Các cài đặt (mode, difficulty, board_size) được giữ nguyên.
        """
        self.board.reset()
        self.player = "X"
        self.game_over = False
        self.winner = None

    # ── Private helpers ───────────────────────────────────────────────────

    def _switch_player(self) -> None:
        """Chuyển ``self.player`` sang người chơi kia.

        ``"X"`` → ``"O"`` và ngược lại.
        """
        self.player = "O" if self.player == "X" else "X"
