"""
core/ai.py — AIPlayer sử dụng thuật toán Alpha-Beta Pruning Minimax.

Module này cung cấp class ``AIPlayer`` với khả năng chọn nước đi tối ưu
dựa trên thuật toán Minimax kết hợp Alpha-Beta Pruning và hàm đánh giá
heuristic cho bàn cờ Caro.

Độ sâu tìm kiếm theo mức độ khó (từ ``config.DIFFICULTY_DEPTH``):
    - easy      → depth 1 (gần random, gần như không suy nghĩ)
    - medium    → depth 3
    - hard      → depth 5
    - nightmare → depth 10 (rất mạnh)
"""
import math
import copy
import concurrent.futures
from config import DIFFICULTY_DEPTH
from core.board import BoardState


# ── Hằng số heuristic ────────────────────────────────────────────────────
_WIN_SCORE = 10_000_000

#: Bảng điểm heuristic dựa trên (số quân liên tiếp, số đầu mở).
#: open_ends = 0 → bị chặn cả hai đầu; 1 → bị chặn một đầu; 2 → mở cả hai đầu.
_THREAT_SCORE: dict[tuple[int, int], int] = {
    (5, 0): _WIN_SCORE,
    (5, 1): _WIN_SCORE,
    (5, 2): _WIN_SCORE,
    (4, 2): 500_000,
    (4, 1): 50_000,
    (3, 2): 10_000,
    (3, 1): 1_000,
    (2, 2): 200,
    (2, 1): 50,
    (1, 2): 10,
    (1, 1): 2,
}


def _evaluate_candidate(
    ai_depth: int, ai_char: str, human_char: str, 
    board_state: BoardState, r: int, c: int
) -> tuple[float, int, int]:
    """Hàm chạy độc lập cho cấu trúc ProcessPoolExecutor để tính điểm một nhánh tại Root.
    
    Do Process không chia sẻ bộ nhớ, hàm này phải định nghĩa ở top-level module
    và nhận vào một bản sao của bàn cờ (deepcopy).

    Args:
        ai_depth (int): Độ sâu của thuật toán.
        ai_char (str): Ký hiệu của AI.
        human_char (str): Ký hiệu của người.
        board_state (BoardState): Bản sao bàn cờ độc lập.
        r (int): Vị trí hàng muốn đặt thử.
        c (int): Vị trí cột muốn đặt thử.
        
    Returns:
        tuple[float, int, int]: Điểm số nhánh vừa tính cùng với tọa độ (r, c).
    """
    board_state.place(r, c, ai_char)
    # Khởi tạo một AIPlayer cục bộ (nhẹ nhàng, không state UI) để dùng hàm _alpha_beta
    ai = AIPlayer()
    ai.depth = ai_depth
    ai.ai_player = ai_char
    ai.human_player = human_char
    
    score = ai._alpha_beta(board_state, ai_depth - 1, -math.inf, math.inf, False)
    return score, r, c


class AIPlayer:
    """Người chơi AI sử dụng Minimax với Alpha-Beta Pruning.

    Kết hợp cắt tỉa Alpha-Beta để giảm không gian tìm kiếm và hàm heuristic
    dựa trên phân tích chuỗi quân (count, open_ends) để đánh giá bàn cờ.

    Attributes:
        depth (int): Độ sâu tìm kiếm tối đa, phụ thuộc vào ``difficulty``.
        ai_player (str): Ký hiệu của AI (mặc định ``"O"``).
        human_player (str): Ký hiệu của người (mặc định ``"X"``).
    """

    def __init__(self, difficulty: str = "medium") -> None:
        """Khởi tạo AIPlayer với mức độ khó tương ứng.

        Args:
            difficulty (str): Một trong ``"easy"``, ``"medium"``, ``"hard"``,
                ``"nightmare"``. Mặc định ``"medium"``. Giá trị không hợp lệ
                sẽ dùng depth mặc định là 3.
        """
        self.depth = DIFFICULTY_DEPTH.get(difficulty, 3)
        self.ai_player = "O"
        self.human_player = "X"
        # Transposition table & Evaluate cache (lưu trữ theo process để tránh trùng lặp tính toán)
        self.transposition_table: dict[tuple[tuple[str, ...], ...], tuple[int, str, float]] = {}
        self._evaluate_cache: dict[tuple[tuple[str, ...], ...], float] = {}

    # ── Public ───────────────────────────────────────────────────────────

    def choose_move(self, board: BoardState) -> tuple[int, int]:
        """Chọn nước đi tốt nhất cho AI trên bàn cờ hiện tại.

        Với ``depth == 1`` dùng greedy search (nhanh hơn). Với ``depth > 1``
        dùng Alpha-Beta Pruning đầy đủ.

        Args:
            board (BoardState): Trạng thái bàn cờ hiện tại.

        Returns:
            tuple[int, int]: Tọa độ (row, col) của nước đi được chọn.
        """
        candidates = board.get_candidate_cells(radius=2)

        if self.depth == 1:
            return self._greedy_move(board, candidates)

        best_score = -math.inf
        best_move = candidates[0]

        # Áp dụng Multiprocessing (Root Move Parallelization) 
        # Cắt các nhánh candidates ra chia cho nhiều Process chạy song song
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for r, c in candidates:
                b_copy = copy.deepcopy(board)
                future = executor.submit(
                    _evaluate_candidate,
                    self.depth, self.ai_player, self.human_player,
                    b_copy, r, c
                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                score, r, c = future.result()
                if score > best_score:
                    best_score = score
                    best_move = (r, c)

        return best_move

    # ── Private: search ───────────────────────────────────────────────────

    def _alpha_beta(
        self,
        board: BoardState,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> float:
        """Thực thi thuật toán Minimax với cắt tỉa Alpha-Beta.

        Nếu ``maximizing=True`` thì đây là lượt của AI (maximizer);
        ngược lại là lượt của người (minimizer).

        Args:
            board (BoardState): Trạng thái bàn cờ hiện tại (được sửa in-place,
                cần gọi ``undo()`` sau khi thăm dò).
            depth (int): Số tầng còn lại để tìm kiếm. Trả về heuristic khi ``0``.
            alpha (float): Giá trị tốt nhất mà maximizer đã đảm bảo được.
            beta (float): Giá trị tốt nhất mà minimizer đã đảm bảo được.
            maximizing (bool): ``True`` nếu đến lượt AI, ``False`` nếu đến lượt người.

        Returns:
            float: Điểm heuristic của trạng thái bàn cờ (dương = lợi cho AI,
                âm = lợi cho người).
        """
        orig_alpha = alpha
        board_hash = tuple(tuple(row) for row in board._board)
        
        # 1. Kiểm tra Transposition Table duyệt trước
        tt_entry = self.transposition_table.get(board_hash)
        if tt_entry is not None:
            tt_depth, tt_flag, tt_value = tt_entry
            if tt_depth >= depth:
                if tt_flag == 'EXACT':
                    return tt_value
                elif tt_flag == 'LOWERBOUND':
                    alpha = max(alpha, tt_value)
                elif tt_flag == 'UPPERBOUND':
                    beta = min(beta, tt_value)
                if alpha >= beta:
                    return tt_value

        opponent = self.human_player if maximizing else self.ai_player

        if board.check_win(opponent):
            return -_WIN_SCORE if maximizing else _WIN_SCORE

        if board.check_draw() or depth == 0:
            return self._evaluate(board)

        candidates = board.get_candidate_cells(radius=2)
        if not candidates:
            return self._evaluate(board)

        # Move Ordering: Sắp xếp các nước đi tiềm năng theo điểm đánh giá nhanh
        # Giúp thuật toán tìm thấy nhánh tốt sớm hơn -> Cắt nhánh Alpha-Beta hiệu quả hơn
        candidates.sort(key=lambda move: self._quick_eval_cell(board, move[0], move[1]), reverse=True)

        if maximizing:
            val = -math.inf
            for r, c in candidates:
                board.place(r, c, self.ai_player)
                val = max(val, self._alpha_beta(board, depth - 1, alpha, beta, False))
                board.undo()
                alpha = max(alpha, val)
                if val >= beta:
                    break  # Beta cut-off
            return val
        else:
            val = math.inf
            for r, c in candidates:
                board.place(r, c, self.human_player)
                val = min(val, self._alpha_beta(board, depth - 1, alpha, beta, True))
                board.undo()
                beta = min(beta, val)
                if val <= alpha:
                    break  # Alpha cut-off
                    
        # 2. Xử lý ghi nhớ vào Transposition Table
        if val <= orig_alpha:
            flag = 'UPPERBOUND'
        elif val >= beta:
            flag = 'LOWERBOUND'
        else:
            flag = 'EXACT'
        self.transposition_table[board_hash] = (depth, flag, val)
        
        return val

    # ── Private: heuristic ────────────────────────────────────────────────

    def _quick_eval_cell(self, board: BoardState, r: int, c: int) -> float:
        """Đánh giá cực nhanh điểm cục bộ tại (r, c) để sắp xếp Move (Alpha-Beta Move Ordering)."""
        def score_for(player: str) -> float:
            board.place(r, c, player)
            s = board.size
            total = 0.0
            for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                # Đếm theo chiều dương
                count = 1
                nr, nc = r + dr, c + dc
                while 0 <= nr < s and 0 <= nc < s and board.get(nr, nc) == player:
                    count += 1
                    nr += dr
                    nc += dc
                open_ends = 0
                if 0 <= nr < s and 0 <= nc < s and board.get(nr, nc) == "":
                    open_ends += 1
                
                # Đếm theo chiều âm
                nr, nc = r - dr, c - dc
                while 0 <= nr < s and 0 <= nc < s and board.get(nr, nc) == player:
                    count += 1
                    nr -= dr
                    nc -= dc
                if 0 <= nr < s and 0 <= nc < s and board.get(nr, nc) == "":
                    open_ends += 1
                
                total += _THREAT_SCORE.get((min(count, 5), open_ends), 0)
            board.undo()
            return total

        return max(score_for(self.ai_player), score_for(self.human_player))

    def _greedy_move(
        self, board: BoardState, candidates: list[tuple[int, int]]
    ) -> tuple[int, int]:
        """Chọn nước đi tốt nhất bằng greedy search single-ply (depth=1).

        Với mỗi ô ứng viên, đánh giá điểm tấn công (nếu AI đặt) và điểm
        phòng thủ (nếu người đặt), chọn ô cho điểm cao nhất.

        Args:
            board (BoardState): Trạng thái bàn cờ hiện tại.
            candidates (list[tuple[int, int]]): Danh sách ô ứng viên để xét.

        Returns:
            tuple[int, int]: Tọa độ (row, col) tốt nhất tìm được.
        """
        best_score = -math.inf
        best_move = candidates[0]
        for r, c in candidates:
            board.place(r, c, self.ai_player)
            attack = self._evaluate(board)
            board.undo()

            board.place(r, c, self.human_player)
            defend = self._evaluate(board)
            board.undo()

            score = max(attack, defend * 0.9)
            if score > best_score:
                best_score = score
                best_move = (r, c)
        return best_move

    def _evaluate(self, board: BoardState) -> float:
        """Đánh giá toàn bộ bàn cờ bằng heuristic.

        Tính tổng điểm heuristic cho AI trừ tổng điểm của đối thủ (nhân hệ số
        1.1 để ưu tiên phòng thủ nhẹ hơn tấn công). Kết quả được lưu cache.
        """
        b_hash = tuple(tuple(row) for row in board._board)
        if b_hash in self._evaluate_cache:
            return self._evaluate_cache[b_hash]
            
        ai_score = self._score_for(board, self.ai_player)
        human_score = self._score_for(board, self.human_player)
        result = ai_score - human_score * 1.1
        
        self._evaluate_cache[b_hash] = result
        return result

    def _score_for(self, board: BoardState, player: str) -> float:
        """Tính tổng điểm heuristic của tất cả chuỗi quân thuộc ``player``.

        Duyệt qua tất cả ô và 4 hướng, dùng ``_count_line`` để tính điểm
        từ ``_THREAT_SCORE``. Mỗi chuỗi chỉ được tính một lần (tránh trùng lặp).

        Args:
            board (BoardState): Trạng thái bàn cờ.
            player (str): Ký hiệu người chơi cần tính điểm (``"X"`` hoặc ``"O"``).

        Returns:
            float: Tổng điểm heuristic của ``player`` trên toàn bàn cờ.
        """
        total = 0.0
        s = board.size
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        visited: set[tuple[int, int, int, int]] = set()

        for r in range(s):
            for c in range(s):
                if board.get(r, c) != player:
                    continue
                for dr, dc in directions:
                    key = (r, c, dr, dc)
                    if key in visited:
                        continue
                    count, open_ends = self._count_line(board, player, r, c, dr, dc)
                    for i in range(count):
                        visited.add((r + i * dr, c + i * dc, dr, dc))
                    score = _THREAT_SCORE.get((min(count, 5), open_ends), 0)
                    total += score
        return total

    def _count_line(
        self,
        board: BoardState,
        player: str,
        r: int,
        c: int,
        dr: int,
        dc: int,
    ) -> tuple[int, int]:
        """Đếm số quân liên tiếp của ``player`` bắt đầu từ (r, c) theo hướng (dr, dc),
        đồng thời đếm số đầu mở (open ends) của chuỗi đó.

        Args:
            board (BoardState): Trạng thái bàn cờ.
            player (str): Ký hiệu người chơi cần đếm.
            r (int): Hàng bắt đầu đếm (0-indexed).
            c (int): Cột bắt đầu đếm (0-indexed).
            dr (int): Bước tiến theo hàng (``-1``, ``0``, hoặc ``1``).
            dc (int): Bước tiến theo cột (``-1``, ``0``, hoặc ``1``).

        Returns:
            tuple[int, int]: Cặp ``(count, open_ends)`` trong đó:
                - ``count``: số quân liên tiếp ≥ 1.
                - ``open_ends``: số đầu mở của chuỗi, từ ``0`` đến ``2``.
        """
        s = board.size
        count = 0
        open_ends = 0

        nr, nc = r, c
        while 0 <= nr < s and 0 <= nc < s and board.get(nr, nc) == player:
            count += 1
            nr += dr
            nc += dc
        if 0 <= nr < s and 0 <= nc < s and board.get(nr, nc) == "":
            open_ends += 1

        pr, pc = r - dr, c - dc
        if 0 <= pr < s and 0 <= pc < s and board.get(pr, pc) == "":
            open_ends += 1

        return count, open_ends
