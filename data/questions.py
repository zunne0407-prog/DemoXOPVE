"""
data/questions.py — Hệ thống sinh và kiểm tra câu hỏi với hai chế độ:

- **math**: Sinh phép toán tiểu học ngẫu nhiên theo độ khó (offline, không cần mạng).
- **science**: Gọi Gemini API để sinh câu hỏi khoa học / IQ và chấm đáp án.

Phụ thuộc ngoài (cần cài):
    - ``google-generativeai`` — chỉ cần cho mode ``"science"``.
"""
from __future__ import annotations

import json
import random
import re
import textwrap
import uuid
import warnings
from config import GEMINI_API_KEY, GEMINI_MODEL, MATH_CONFIG
from data.question_config import TOPIC_KEYWORDS

# ═══════════════════════════════════════════════════════════════════
#  Mode 1: Math (offline)
# ═══════════════════════════════════════════════════════════════════

def generate_math_question(difficulty: str) -> dict:
    """Sinh một phép toán số học ngẫu nhiên phù hợp với mức độ khó.

    Đảm bảo kết quả luôn là số nguyên không âm và tất cả toán hạng
    nằm trong giới hạn số chữ số cho phép của từng mức.

    Cấu hình mức độ (từ ``config.MATH_CONFIG``):

    =========  ============  ==================
    Mức độ     Tối đa        Phép toán
    =========  ============  ==================
    easy       99            ``+``, ``-``
    medium     999           ``+``, ``-``, ``×``
    hard       9999          ``+``, ``-``, ``×``, ``÷``
    =========  ============  ==================

    Args:
        difficulty (str): Mức độ khó — ``"easy"``, ``"medium"``, hoặc ``"hard"``.
            Mặc định dùng cấu hình ``"easy"`` nếu giá trị không hợp lệ.

    Returns:
        dict: Câu hỏi với cấu trúc::

            {
                "q":       str,  # Chuỗi câu hỏi, ví dụ "Tính: 23 + 47 = ?"
                "a":       int,  # Đáp án đúng (số nguyên)
                "display": str,  # Biểu thức hiển thị, ví dụ "23 + 47"
                "mode":    str   # Luôn là "math"
            }
    """
    max_val, ops = MATH_CONFIG.get(difficulty, MATH_CONFIG["easy"])
    op = random.choice(ops)

    if op == "/":
        b = random.randint(1, int(max_val ** 0.5) or 1)
        a = b * random.randint(1, max_val // b)
        answer = a // b
        display = f"{a} ÷ {b}"
    elif op == "*":
        side = int(max_val ** 0.5)
        a = random.randint(2, max(2, side))
        b = random.randint(2, max(2, side))
        answer = a * b
        display = f"{a} × {b}"
    elif op == "-":
        a = random.randint(1, max_val)
        b = random.randint(0, a)
        answer = a - b
        display = f"{a} - {b}"
    else:  # "+"
        a = random.randint(0, max_val)
        b = random.randint(0, max_val - a)
        answer = a + b
        display = f"{a} + {b}"

    return {
        "q": f"Tính: {display} = ?",
        "a": answer,
        "display": display,
        "mode": "math",
    }


# ═══════════════════════════════════════════════════════════════════
#  Mode 2: Science via Gemini API
# ═══════════════════════════════════════════════════════════════════

# Import từ điển khóa từ file config riêng (TOPIC_KEYWORDS)

_DIFFICULTY_HINT: dict[str, str] = {
    "easy":      "rất đơn giản, dành cho học sinh trung học",
    "medium":    "trung bình, dành cho người lớn bình thường",
    "hard":      "khó, cần suy luận",
    "nightmare": "rất khó, dành cho chuyên gia",
}


def _get_gemini_client():
    """Tạo và trả về đối tượng Client của Gemini SDK mới.

    Cấu hình API key từ ``config.GEMINI_API_KEY`` trước khi tạo client.

    Returns:
        google.genai.Client | None: Client đã được cấu hình,
        hoặc ``None`` nếu API key chưa được đặt hoặc thư viện chưa cài.
    """
    try:
        from google import genai
        if not GEMINI_API_KEY:
            return None
        return genai.Client(api_key=GEMINI_API_KEY)
    except ImportError:
        return None


def generate_science_question(difficulty: str = "medium") -> dict | None:
    """Gọi Gemini API để sinh một câu hỏi khoa học / IQ ngắn gọn.

    Chọn ngẫu nhiên một chủ đề từ ``_TOPICS`` và yêu cầu Gemini sinh câu hỏi
    phù hợp với mức độ khó. Response được parse từ JSON.

    Args:
        difficulty (str): Mức độ khó — ``"easy"``, ``"medium"``, ``"hard"``,
            hoặc ``"nightmare"``. Mặc định ``"medium"``.

    Returns:
        dict | None: Câu hỏi với cấu trúc::

            {
                "q":    str,  # Nội dung câu hỏi
                "mode": str   # Luôn là "science"
            }

        Trả về ``None`` nếu API key chưa cấu hình, thư viện chưa cài,
        hoặc xảy ra lỗi khi gọi API.
    """
    client = _get_gemini_client()
    if client is None:
        return None

    # Lựa chọn ngẫu nhiên một chủ đề lớn
    main_topic = random.choice(list(TOPIC_KEYWORDS.keys()))
    
    # Gom nhóm từ khóa theo độ khó tịnh tiến
    topic_dict = TOPIC_KEYWORDS[main_topic]
    pool = list(topic_dict.get("easy", []))
    
    if difficulty in ("medium", "hard", "nightmare"):
        pool.extend(topic_dict.get("medium", []))
    if difficulty in ("hard", "nightmare"):
        pool.extend(topic_dict.get("hard", []))
    if difficulty == "nightmare":
        pool.extend(topic_dict.get("nightmare", []))
        
    subtopic = random.choice(pool) if pool else main_topic
    # Tạo mã ngẫu nhiên để ép AI không lặp lại câu hỏi cũ
    seed_str = str(uuid.uuid4())[:8]

    prompt = textwrap.dedent(f"""
        Hãy tạo 1 câu hỏi trắc nghiệm hoặc câu hỏi ngắn cực kỳ dễ hiểu.
        Lĩnh vực: {main_topic}.
        CHỦ ĐỀ CỤ THỂ BẮT BUỘC PHẢI HỎI VỀ: "{subtopic}"
        Mức độ: {_DIFFICULTY_HINT.get(difficulty, "trung bình")}.
        
        Mã ngẫu nhiên định danh: {seed_str} (DÙNG ĐỂ SINH RA MỘT CÂU HỎI HOÀN TOÀN MỚI CHƯA TỪNG XUẤT HIỆN TƯƠNG ĐƯƠNG VỚI MÃ NÀY).
        
        Yêu cầu:
        - Câu hỏi rõ ràng, cực kỳ ngắn gọn tối đa 2 câu (không được dài dòng, dứt khoát không quá 40 chữ).
        - Đáp án phải là 1 từ, 1 số, hoặc 1 cụm từ tối đa 5 từ.
        - Trả lời theo đúng format JSON sau, không thêm text ngoài JSON:
        {{"question": "..."}}
    """).strip()

    try:
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        text = resp.text.strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        data = json.loads(match.group())
        return {
            "q":    data.get("question", ""),
            "mode": "science",
        }
    except Exception:
        return None


def check_science_answer(question: str, user_answer: str) -> tuple[bool, str]:
    """Gửi câu hỏi và đáp án của người dùng lên Gemini để chấm điểm.

    Gemini sẽ xác định đáp án đúng hay sai và trả về giải thích ngắn gọn.

    Args:
        question (str): Nội dung câu hỏi gốc đã được sinh bởi ``generate_science_question``.
        user_answer (str): Đáp án mà người dùng nhập vào.

    Returns:
        tuple[bool, str]: Cặp ``(correct, explanation)`` trong đó:
            - ``correct`` (bool): ``True`` nếu câu trả lời đúng, ``False`` nếu sai.
            - ``explanation`` (str): Giải thích từ AI, bao gồm đáp án đúng nếu sai.
            Trả về ``(False, "thông báo lỗi")`` nếu API không khả dụng.
    """
    client = _get_gemini_client()
    if client is None:
        return False, "Không thể kết nối Gemini API. Kiểm tra API key trong file .env."

    prompt = textwrap.dedent(f"""
        Câu hỏi: {question}
        Đáp án người dùng: {user_answer}

        Hãy chấm đáp án trên. Trả lời theo format JSON, không thêm text ngoài JSON:
        {{"correct": true/false, "explanation": "Giải thích ngắn gọn (1-2 câu), bao gồm đáp án đúng nếu sai."}}
    """).strip()

    try:
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        text = resp.text.strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return False, "Không thể phân tích phản hồi từ AI."
        data = json.loads(match.group())
        return bool(data.get("correct", False)), data.get("explanation", "")
    except Exception as exc:
        return False, f"Lỗi khi gọi API: {exc}"
