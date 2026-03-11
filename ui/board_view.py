"""
ui/board_view.py — BoardView: Canvas widget hiển thị bàn cờ Caro.

Module này cung cấp class ``BoardView`` kế thừa ``tk.Canvas``, vẽ lưới bàn cờ
với các hiệu ứng hover, highlight ô thắng, và xử lý click chuột.
"""
import tkinter as tk
from ui.theme import (
    BG_DARK, BG_PANEL, BG_SURFACE, BG_HOVER, BG_WIN, BG_LAST, BG_PENDING,
    ACCENT, ACCENT2, COLOR_X, COLOR_O,
    CELL_PAD, FONT_FAMILY,
)


class BoardView(tk.Canvas):
    """Widget Canvas hiển thị bàn cờ Caro n×n.

    Vẽ lưới ô cờ bằng ``tk.Canvas``, hỗ trợ:
    - Hover highlight khi di chuột qua ô trống.
    - Đặt quân cờ có màu khác nhau cho X và O.
    - Highlight ô thắng bằng màu vàng sau game kết thúc.
    - Callback ``on_cell_click(row, col)`` khi người dùng click ô trống.

    Attributes:
        size (int): Số hàng và cột của bàn cờ.
        step (int): Khoảng cách giữa các ô tính bằng pixel (``CELL_SIZE + CELL_PAD``).
        on_cell_click (Callable[[int, int], None]): Hàm callback nhận (row, col).
    """

    def __init__(
        self,
        parent: tk.Widget,
        size: int,
        on_cell_click,
        **kwargs,
    ) -> None:
        """Khởi tạo BoardView và vẽ lưới bàn cờ trống.

        Args:
            parent (tk.Widget): Widget cha chứa canvas này.
            size (int): Số hàng / cột của bàn cờ.
            on_cell_click (Callable[[int, int], None]): Hàm callback được gọi
                khi người dùng click vào một ô trống. Nhận ``(row, col)`` là int.
            **kwargs: Các tham số bổ sung truyền thẳng cho ``tk.Canvas``.
        """
        self.size = size
        
        # Cố định kích thước bàn cờ trên màn hình khoảng 500x500 px
        self.board_pixel_size = 500
        self.step = self.board_pixel_size // size
        self.cell_size = self.step - CELL_PAD
        
        # Scale font chữ theo tỉ lệ của ô vuông
        self.font_size = max(8, int(self.cell_size * 0.6))
        self.font_cell = (FONT_FAMILY, self.font_size, "bold")
        
        total_pixels = self.step * size + CELL_PAD

        super().__init__(
            parent,
            width=total_pixels,
            height=total_pixels,
            bg=BG_DARK,
            highlightthickness=0,
            **kwargs,
        )

        self.on_cell_click = on_cell_click
        self._cell_ids: dict[tuple[int, int], int] = {}
        self._text_ids: dict[tuple[int, int], int] = {}
        self._hover: tuple[int, int] | None = None
        self._last_move: tuple[int, int] | None = None
        self._pending_cell: tuple[int, int] | None = None
        self._state: dict[tuple[int, int], str] = {}
        self._disabled: bool = False

        self._draw_grid()
        self.bind("<Motion>",   self._on_motion)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_click)

    # ── Public ────────────────────────────────────────────────────────────

    def place_piece(self, r: int, c: int, player: str) -> None:
        """Hiển thị quân cờ của ``player`` tại ô (r, c).

        Với Light Theme, màu nền ô giữ nguyên (BG_SURFACE), chỉ vẽ ký tự có màu.

        Args:
            r (int): Hàng của ô (0-indexed).
            c (int): Cột của ô (0-indexed).
            player (str): Ký hiệu người chơi — ``"X"`` hoặc ``"O"``.
        """
        # Xóa highlight của quân vừa đánh trước đó (nếu có)
        if self._last_move:
            lr, lc = self._last_move
            if (lr, lc) in self._state:
                self._redraw_cell(lr, lc, BG_SURFACE)
                last_player = self._state[(lr, lc)]
                color = COLOR_X if last_player == "X" else COLOR_O
                self._draw_text(lr, lc, last_player, color)

        self._state[(r, c)] = player
        self._last_move = (r, c)
        
        color = COLOR_X if player == "X" else COLOR_O
        self._redraw_cell(r, c, BG_LAST)
        self._draw_text(r, c, player, color)

    def highlight_winner(self, cells: list[tuple[int, int]]) -> None:
        """Tô vàng các ô tạo thành chuỗi thắng.

        Args:
            cells (list[tuple[int, int]]): Danh sách tọa độ (row, col) của các ô thắng.
        """
        for r, c in cells:
            self._redraw_cell(r, c, BG_WIN)
            player = self._state.get((r, c), "")
            if player:
                color = COLOR_X if player == "X" else COLOR_O
                self._draw_text(r, c, player, color)

    def set_pending(self, r: int | None, c: int | None) -> None:
        """Tô màu ô đang được chọn để trả lời câu hỏi."""
        if self._pending_cell:
            pr, pc = self._pending_cell
            self._pending_cell = None
            if (pr, pc) not in self._state:
                self._redraw_cell(pr, pc, BG_SURFACE)
        
        if r is not None and c is not None:
            self._pending_cell = (r, c)
            self._redraw_cell(r, c, BG_PENDING)

    def reset(self) -> None:
        """Xóa toàn bộ quân cờ và vẽ lại lưới bàn cờ trống.

        Xóa state nội bộ, xóa các text trên canvas và trả tất cả ô về màu nền mặc định.
        """
        self._state.clear()
        self._hover = None
        self._pending_cell = None
        for r in range(self.size):
            for c in range(self.size):
                self._redraw_cell(r, c, BG_SURFACE)
                tid = self._text_ids.pop((r, c), None)
                if tid:
                    self.delete(tid)

    def set_disabled(self, disabled: bool) -> None:
        """Bật hoặc tắt khả năng click vào bàn cờ.

        Dùng để ngăn người dùng click khi đang là lượt của AI
        hoặc khi đang chờ phản hồi từ API.

        Args:
            disabled (bool): ``True`` để vô hiệu hóa, ``False`` để kích hoạt lại.
        """
        self._disabled = disabled

    # ── Drawing helpers ───────────────────────────────────────────────────

    def _draw_grid(self) -> None:
        """Vẽ lưới bàn cờ ban đầu với tất cả ô trống màu nền mặc định."""
        self._disabled = False
        for r in range(self.size):
            for c in range(self.size):
                self._redraw_cell(r, c, BG_SURFACE)

    def _cell_bbox(self, r: int, c: int) -> tuple[int, int, int, int]:
        """Tính viền của một ô.

        Args:
            r (int): Hàng của ô (0-indexed).
            c (int): Cột của ô (0-indexed).

        Returns:
            tuple[int, int, int, int]: ``(x1, y1, x2, y2)`` là pixel
            góc trên-trái và góc dưới-phải của ô.
        """
        x1 = CELL_PAD + c * self.step
        y1 = CELL_PAD + r * self.step
        return x1, y1, x1 + self.cell_size, y1 + self.cell_size

    def _redraw_cell(self, r: int, c: int, fill: str) -> None:
        """Vẽ hoặc cập nhật màu nền của ô (r, c).

        Tạo mới item canvas nếu chưa tồn tại, cập nhật màu nếu đã có.

        Args:
            r (int): Hàng của ô (0-indexed).
            c (int): Cột của ô (0-indexed).
            fill (str): Màu nền hex, ví dụ ``"#1a1a2e"``.
        """
        x1, y1, x2, y2 = self._cell_bbox(r, c)
        item_id = self._cell_ids.get((r, c))
        if item_id:
            self.itemconfig(item_id, fill=fill)
        else:
            item_id = self.create_rectangle(
                x1, y1, x2, y2,
                fill=fill,
                outline="",
                tags=("cell", f"{r},{c}"),
            )
            self._cell_ids[(r, c)] = item_id

    def _draw_text(self, r: int, c: int, text: str, color: str) -> None:
        """Vẽ hoặc cập nhật ký tự quân cờ ở tâm ô (r, c).

        Args:
            r (int): Hàng của ô (0-indexed).
            c (int): Cột của ô (0-indexed).
            text (str): Ký tự cần hiển thị (``"X"`` hoặc ``"O"``).
            color (str): Màu chữ hex.
        """
        x1, y1, x2, y2 = self._cell_bbox(r, c)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        tid = self._text_ids.get((r, c))
        if tid:
            self.itemconfig(tid, text=text, fill=color)
        else:
            tid = self.create_text(cx, cy, text=text, fill=color, font=self.font_cell)
            self._text_ids[(r, c)] = tid

    def _rc_from_xy(self, x: int, y: int) -> tuple[int, int] | None:
        """Chuyển đổi tọa độ pixel (x, y) thành chỉ số ô (row, col).

        Args:
            x (int): Tọa độ pixel theo chiều ngang.
            y (int): Tọa độ pixel theo chiều dọc.

        Returns:
            tuple[int, int] | None: ``(row, col)`` nếu pixel nằm trong một ô hợp lệ,
            hoặc ``None`` nếu nằm ngoài lưới hoặc trong vùng CELL_PAD.
        """
        c = (x - CELL_PAD) // self.step
        r = (y - CELL_PAD) // self.step
        if 0 <= r < self.size and 0 <= c < self.size:
            x1, y1, x2, y2 = self._cell_bbox(r, c)
            if x1 <= x <= x2 and y1 <= y <= y2:
                return r, c
        return None

    # ── Events ────────────────────────────────────────────────────────────

    def _on_motion(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        """Xử lý sự kiện di chuột: highlight ô đang hover, bỏ highlight ô cũ.

        Args:
            event (tk.Event): Sự kiện chuột từ Tkinter chứa ``event.x``, ``event.y``.
        """
        pos = self._rc_from_xy(event.x, event.y)
        if pos == self._hover:
            return
        if self._hover and self._hover not in self._state:
            color = BG_PENDING if self._hover == self._pending_cell else BG_SURFACE
            self._redraw_cell(*self._hover, color)
        self._hover = pos
        if pos and pos not in self._state:
            if pos != self._pending_cell:
                self._redraw_cell(*pos, BG_HOVER)

    def _on_leave(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        """Xử lý sự kiện chuột rời khỏi canvas: bỏ highlight ô hiện tại.

        Args:
            event (tk.Event): Sự kiện Leave từ Tkinter.
        """
        if self._hover and self._hover not in self._state:
            color = BG_PENDING if self._hover == self._pending_cell else BG_SURFACE
            self._redraw_cell(*self._hover, color)
        self._hover = None

    def _on_click(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        """Xử lý sự kiện click chuột: gọi ``on_cell_click`` nếu ô hợp lệ.

        Không làm gì nếu board đang bị disable, hoặc ô đã có quân.

        Args:
            event (tk.Event): Sự kiện click chuột từ Tkinter chứa ``event.x``, ``event.y``.
        """
        if self._disabled:
            return
        pos = self._rc_from_xy(event.x, event.y)
        if pos and pos not in self._state:
            self.on_cell_click(*pos)
