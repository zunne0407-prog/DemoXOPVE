"""
ui/theme.py — Bảng màu, font và style constants (Sáng - Light theme).
"""

# ── Colors (Light Theme) ──────────────────────────────────────────────────
BG_DARK     = "#f0f2f5"      # Nền chính (xám nhạt rất mềm)
BG_PANEL    = "#ffffff"      # Panel / sidebar (trắng tinh)
BG_SURFACE  = "#e4e6eb"      # Card / cell surface (xám nhạt)
BG_HOVER    = "#d8dadf"      # Cell hover
BG_WIN      = "#ffdb58"      # Ô thắng (vàng)
BG_LAST     = "#cce5ff"      # Ô vừa đánh (xanh dương nhạt)
BG_PENDING  = "#ffe0b2"      # Ô đang chờ trả lời câu hỏi (cam nhạt)

ACCENT      = "#0064d2"      # Màu nhấn chính (xanh dương đậm đậm chút)
ACCENT2     = "#004b9e"      # Màu nhấn phụ khi hover

TEXT_PRIMARY   = "#1c1e21"   # Chữ chính (đen than)
TEXT_SECONDARY = "#606770"   # Chữ phụ (xám đậm)
TEXT_MUTED     = "#8d949e"   # Chữ mờ

# Màu sắc X/O sẽ tĩnh trên bàn cờ. 
# Nhưng bản thân board_view đang vẽ chữ X / O lên,
# Vì nền sáng, ta dùng màu đậm cho X/O.
COLOR_X = "#d32f2f"          # Quân X: Đỏ đậm
COLOR_O = "#1976d2"          # Quân O: Xanh dương đậm

# ── Fonts ─────────────────────────────────────────────────────────────────
FONT_FAMILY   = "Segoe UI"
FONT_TITLE    = (FONT_FAMILY, 22, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 14, "bold")
FONT_BODY     = (FONT_FAMILY, 11)
FONT_SMALL    = (FONT_FAMILY, 9)
FONT_CELL     = (FONT_FAMILY, 18, "bold")
FONT_STATUS   = (FONT_FAMILY, 12, "bold")
FONT_LABEL    = (FONT_FAMILY, 10)
FONT_BUTTON   = (FONT_FAMILY, 11, "bold")

# ── Sizes ─────────────────────────────────────────────────────────────────
CELL_SIZE    = 38     # px mỗi ô bàn cờ (hơi nhỏ lại xíu để vừa màn hình có sidebar)
CELL_PAD     = 2      # khoảng cách giữa các ô
CORNER_R     = 4      # Bo góc ô
BTN_PAD_X    = 18
BTN_PAD_Y    = 8
