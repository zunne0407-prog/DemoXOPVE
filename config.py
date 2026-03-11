"""
config.py — Global settings for Caro Logic Game.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Board ─────────────────────────────────────────────
BOARD_SIZES = [5, 7, 10, 13, 15]
DEFAULT_BOARD_SIZE = 5
WIN_CONDITION = 5          # Số quân liên tiếp để thắng
AI_DELAY_MS = 400          # Delay (ms) trước khi AI đánh

# ── AI Difficulty (Alpha-Beta depth) ──────────────────
DIFFICULTY_DEPTH = {
    "easy":      1,
    "medium":    2,
    "hard":      3,
    "nightmare": 5
}

# ── Game Mode ─────────────────────────────────────────
GAME_MODES = {
    "pvp": "Người vs Người",
    "pvc": "Người vs Máy",
}

# ── Question Mode ─────────────────────────────────────
QUESTION_MODES = {
    "math":    "Toán tiểu học",
    "science": "Khoa học (AI)",
    "none":    "Không có (XO thuần)",
}

# ── Gemini API ────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemma-3-27b-it"
MAX_REROLLS    = 3          # Số lần đổi câu tối đa mỗi lượt

# ── Math Question Limits ──────────────────────────────
MATH_CONFIG = {
    #    (max_val,  ops)
    "easy":   (99,   ["+", "-"]),
    "medium": (999,  ["+", "-", "*"]),
    "hard":   (9999, ["+", "-", "*", "/"]),
    "nightmare": (99999, ["+", "-", "*", "/"]),
}
