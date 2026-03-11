"""
core/board.py — Quản lý trạng thái bàn cờ Caro.

Module này cung cấp class ``BoardState`` dùng để lưu trữ trạng thái bàn cờ,
thực hiện các nước đi, hoàn tác (undo), kiểm tra thắng/hòa và tính toán
các ô ứng viên cho AI tìm kiếm Alpha-Beta.
"""
from config import WIN_CONDITION


class BoardState:
    """Biểu diễn và quản lý trạng thái bàn cờ Caro n×n.

    Lưu trữ ma trận ô cờ, lịch sử các nước đi (để hỗ trợ undo cho AI),
    và cung cấp các phương thức kiểm tra thắng/hòa có tối ưu hiệu năng.

    Attributes:
        size (int): Số hàng và cột của bàn cờ.
        win (int): Số quân liên tiếp cần thiết để thắng (từ ``config.WIN_CONDITION``).
    """

    def __init__(self, size: int) -> None:
        """Khởi tạo bàn cờ trống kích thước ``size`` × ``size``.

        Args:
            size (int): Số hàng / cột của bàn cờ. Phải là số nguyên dương.
        """
        self.size = size
        self.win = WIN_CONDITION
        self._board: list[list[str]] = [[""] * size for _ in range(size)]
        self._history: list[tuple[int, int]] = []

    # ── Public interface ──────────────────────────────────────────────────

    def place(self, r: int, c: int, player: str) -> None:
        """Đặt quân cờ của ``player`` lên ô (r, c) và ghi vào lịch sử.

        Args:
            r (int): Chỉ số hàng (0-indexed).
            c (int): Chỉ số cột (0-indexed).
            player (str): Ký hiệu người chơi, ``"X"`` hoặc ``"O"``.
        """
        self._board[r][c] = player
        self._history.append((r, c))

    def undo(self) -> tuple[int, int] | None:
        """Hoàn tác nước đi cuối cùng trong lịch sử.

        Được dùng bởi thuật toán Alpha-Beta để khôi phục trạng thái bàn cờ
        sau khi thăm dò một nước đi.

        Returns:
            tuple[int, int] | None: Tọa độ (row, col) của ô vừa được hoàn tác,
            hoặc ``None`` nếu lịch sử rỗng.
        """
        if not self._history:
            return None
        r, c = self._history.pop()
        self._board[r][c] = ""
        return r, c

    def get(self, r: int, c: int) -> str:
        """Trả về giá trị tại ô (r, c).

        Args:
            r (int): Chỉ số hàng (0-indexed).
            c (int): Chỉ số cột (0-indexed).

        Returns:
            str: ``"X"``, ``"O"``, hoặc ``""`` nếu ô trống.
        """
        return self._board[r][c]

    def is_empty(self, r: int, c: int) -> bool:
        """Kiểm tra ô (r, c) có đang trống không.

        Args:
            r (int): Chỉ số hàng (0-indexed).
            c (int): Chỉ số cột (0-indexed).

        Returns:
            bool: ``True`` nếu ô trống, ``False`` nếu đã có quân.
        """
        return self._board[r][c] == ""

    def get_empty_cells(self) -> list[tuple[int, int]]:
        """Trả về danh sách tất cả ô trống trên bàn cờ.

        Returns:
            list[tuple[int, int]]: Danh sách các tọa độ (row, col) còn trống.
        """
        return [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self._board[r][c] == ""
        ]

    def get_candidate_cells(self, radius: int = 2) -> list[tuple[int, int]]:
        """Trả về các ô trống nằm trong vòng ``radius`` ô quanh quân đã đặt.

        Thay vì tìm kiếm toàn bộ bàn cờ O(n²), AI chỉ xét các ô gần khu vực
        đang có quân — giúp giảm mạnh không gian tìm kiếm của Alpha-Beta.
        Nếu bàn cờ chưa có quân nào, trả về ô trung tâm.

        Args:
            radius (int): Bán kính tìm kiếm tính bằng số ô. Mặc định ``2``.

        Returns:
            list[tuple[int, int]]: Danh sách các ô ứng viên (row, col).
        """
        if not self._history:
            mid = self.size // 2
            return [(mid, mid)]

        candidates: set[tuple[int, int]] = set()
        for hr, hc in self._history:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    nr, nc = hr + dr, hc + dc
                    if (
                        0 <= nr < self.size
                        and 0 <= nc < self.size
                        and self._board[nr][nc] == ""
                    ):
                        candidates.add((nr, nc))
        return list(candidates)

    def check_win(self, player: str) -> bool:
        """Kiểm tra toàn bộ bàn cờ xem ``player`` có đạt ``WIN_CONDITION``
        quân liên tiếp theo bất kỳ hướng nào không.

        Phức tạp hơn ``check_win_at`` nhưng toàn diện hơn; dùng để xác nhận
        trạng thái cuối game.

        Args:
            player (str): Ký hiệu người chơi cần kiểm tra (``"X"`` hoặc ``"O"``).

        Returns:
            bool: ``True`` nếu ``player`` đã thắng, ``False`` nếu chưa.
        """
        b = self._board
        w = self.win
        s = self.size
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(s):
            for c in range(s):
                if b[r][c] != player:
                    continue
                for dr, dc in directions:
                    if self._check_line(b, player, r, c, dr, dc, w, s):
                        return True
        return False

    def check_win_at(self, player: str, r: int, c: int) -> bool:
        """Kiểm tra nhanh liệu ``player`` có thắng sau khi đặt quân tại (r, c).

        Chỉ xét các hướng đi qua ô (r, c) vừa được đặt — nhanh hơn nhiều
        so với ``check_win``. Dùng ngay sau mỗi nước đi trong game thực.

        Args:
            player (str): Ký hiệu người chơi (``"X"`` hoặc ``"O"``).
            r (int): Hàng của quân vừa đặt (0-indexed).
            c (int): Cột của quân vừa đặt (0-indexed).

        Returns:
            bool: ``True`` nếu ``player`` thắng, ``False`` nếu chưa.
        """
        b = self._board
        w = self.win
        s = self.size
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for sign in (1, -1):
                nr, nc = r + sign * dr, c + sign * dc
                while 0 <= nr < s and 0 <= nc < s and b[nr][nc] == player:
                    count += 1
                    nr += sign * dr
                    nc += sign * dc
            if count >= w:
                return True
        return False

    def check_draw(self) -> bool:
        """Kiểm tra xem bàn cờ đã đầy hay chưa (điều kiện hòa).

        Returns:
            bool: ``True`` nếu tất cả ô đều đã được đánh (hòa), ``False`` nếu còn ô trống.
        """
        return all(
            self._board[r][c] != ""
            for r in range(self.size)
            for c in range(self.size)
        )

    def get_winning_cells(self, player: str) -> list[tuple[int, int]]:
        """Tìm và trả về tọa độ các ô tạo thành chuỗi thắng của ``player``.

        Dùng để highlight ô thắng trên giao diện sau khi game kết thúc.

        Args:
            player (str): Ký hiệu người chơi thắng cuộc (``"X"`` hoặc ``"O"``).

        Returns:
            list[tuple[int, int]]: Danh sách ``WIN_CONDITION`` tọa độ (row, col)
            liên tiếp tạo thành chuỗi thắng, hoặc ``[]`` nếu không tìm thấy.
        """
        b = self._board
        w = self.win
        s = self.size
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(s):
            for c in range(s):
                if b[r][c] != player:
                    continue
                for dr, dc in directions:
                    cells = [(r + i * dr, c + i * dc) for i in range(w)]
                    if all(
                        0 <= nr < s and 0 <= nc < s and b[nr][nc] == player
                        for nr, nc in cells
                    ):
                        return cells
        return []

    def reset(self) -> None:
        """Xóa toàn bộ quân cờ và lịch sử, đặt lại bàn cờ về trạng thái ban đầu."""
        self._board = [[""] * self.size for _ in range(self.size)]
        self._history.clear()

    # ── Private helpers ───────────────────────────────────────────────────

    @staticmethod
    def _check_line(
        b: list[list[str]],
        player: str,
        r: int,
        c: int,
        dr: int,
        dc: int,
        w: int,
        s: int,
    ) -> bool:
        """Kiểm tra xem có ``w`` quân liên tiếp của ``player`` bắt đầu từ (r, c)
        theo hướng (dr, dc) không.

        Args:
            b (list[list[str]]): Ma trận bàn cờ hiện tại.
            player (str): Ký hiệu cần kiểm tra.
            r (int): Hàng bắt đầu.
            c (int): Cột bắt đầu.
            dr (int): Bước tiến theo hàng (``-1``, ``0``, hoặc ``1``).
            dc (int): Bước tiến theo cột (``-1``, ``0``, hoặc ``1``).
            w (int): Số quân liên tiếp cần kiểm tra.
            s (int): Kích thước bàn cờ (để kiểm tra biên).

        Returns:
            bool: ``True`` nếu tồn tại đúng ``w`` quân liên tiếp, ``False`` nếu không.
        """
        for i in range(w):
            nr, nc = r + i * dr, c + i * dc
            if not (0 <= nr < s and 0 <= nc < s) or b[nr][nc] != player:
                return False
        return True
