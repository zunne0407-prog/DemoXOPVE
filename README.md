# Caro Logic

Game cờ Caro kết hợp thử thách câu hỏi — trả lời đúng mới được đặt cờ.

## Các Tùy Chọn Cài Đặt (Setup Options)

Tại màn hình khởi động (Setup Screen), bạn có thể tùy chỉnh các cấu hình sau trước khi tạo phòng chơi:

1. **Chế độ chơi (Game Mode)**
   - **Người vs Máy (PvE)**: Bạn đánh chữ X, máy đánh chữ O.
   - **Người vs Người (PvP)**: Solo trực tiếp trên cùng một màn hình.

2. **Kích thước bàn cờ (Board Size)**
   - **5×5 (Nhanh)**: Bàn cờ nhỏ, đánh giá nhanh.
   - **10×10 (Vừa vặn)**: Phù hợp nhất cho trải nghiệm cân bằng.
   - **15×15 (Rộng rãi)**: Thích hợp cho các ván đấu dài hơi.

3. **Loại câu hỏi (Question Mode)**
   - **Không có (XO thuần)**: Chơi giải trí Cờ Caro thông thường, click là được đánh.
   - **Toán Học (Toán sơ cấp)**: Trả lời kết quả của các biểu thức (`+`, `-`, `×`, `÷`). Hoạt động 100% Offline.
   - **Khoa Học & Đời Sống (Gemini AI)**: Gọi API tới Gemini để sinh câu hỏi trắc nghiệm hoặc trí tuệ. Cần nhập API Key.

4. **Độ khó AI (AI Difficulty - PvE)**
   - **Dễ**: AI đánh ngẫu nhiên, không phòng ngự.
   - **Trung bình**: AI biết cách tự phòng ngự, chặt đường cờ hoặc lập chuỗi 2.
   - **Khó**: AI tính xa 3-4 nước (Minimax Alpha-Beta), tạo chuỗi đôi.
   - **Ác mộng**: AI tính toán sâu với thuật toán tỉa nhánh tốc độ cao và Transposition Table.

5. **Độ khó Câu hỏi (Question Difficulty)**
   - **Dễ**: Phép cộng trừ cấp 1, hoặc các câu hỏi kiến thức phổ thông đại chúng đơn giản.
   - **Trung bình**: Có nhân chia, cấp độ phổ thông, độ khó vừa đủ.
   - **Khó**: Phép tính số lớn, hoặc câu hỏi khoa học đòi suy luận.
   - **Ác mộng**: Các câu đố cực khó, chuyên biệt và sâu về các lĩnh vực.

## Tính năng In-Game Nổi Bật

- **Dynamic Scaling UI**: Kích thước lưới bàn cờ và Text luôn trải đều màn hình, không bị thừa vùng xám.
- **Xác định mục tiêu**: Ô bạn vừa bấm sẽ sáng màu cam (Pending) trong suốt thời gian bạn suy nghĩ đáp án. Bạn có thể tự do bấm sang ô khác để đổi ý.
- **Bảng Tri thức**: Sau khi trả lời xong một câu hỏi, Form câu đố sẽ ẩn đi và hiển thị box giải thích đáp án cặn kẽ để bạn vừa chơi cờ vừa học kiến thức.
- **Tracking nước đi**: Nước cờ mới nhất luôn được Highlight màu xanh để tránh bị rối mắt khi máy đánh quá nhanh.

## Cài đặt

**Yêu cầu:** Python ≥ 3.10 (tkinter có sẵn)

```bash
# 1. Cài dependencies
pip install -r requirements.txt

# 2. Cấu hình API key (chỉ cần nếu dùng chế độ Khoa học)
copy .env.example .env
# Mở .env và điền GEMINI_API_KEY=<key của bạn>
# Lấy key miễn phí tại: https://aistudio.google.com/app/apikey

# 3. Chạy game
python main.py
```

## Cấu trúc dự án

```text
DemoXOPVE/
├── main.py              # File khởi động Game (Entry point)
├── config.py            # Cài đặt thông số toàn cục (Size, Colors, API)
├── requirements.txt     # Danh sách thư viện cần cài đặt
├── .env.example         # File mẫu chứa API Key
├── .gitignore           # File loại trừ git
│
├── data/
│   ├── question_config.py # Cấu hình Ngân hàng từ khóa cho Gemini AI
│   └── questions.py       # Bộ máy sinh câu hỏi Offline (Toán) & Online (Khoa học)
│
├── core/
│   ├── board.py         # Quản lý Trạng thái lưới bàn cờ, logic Win/Draw
│   ├── ai.py            # Trí tuệ nhân tạo (Thuật toán Alpha-Beta Pruning)
│   └── game.py          # Quản lý Flow trò chơi (Lượt đi, Chuyển phase)
│
└── ui/
    ├── theme.py          # Biến số về Màu sắc, Font chữ, Kích thước UI
    ├── board_view.py     # Widget Canvas hiển thị Bàn cờ trực quan
    ├── quiz_dialog.py    # (Cũ/Dự phòng) Popup câu hỏi
    └── app.py            # Lớp Giao diện chính (Cửa sổ App + Setup Menu)
```
