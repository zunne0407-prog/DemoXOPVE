import tkinter as tk
from tkinter import messagebox, simpledialog
import random

# Ngân hàng câu hỏi tư duy (đáp án là số nguyên)
QUESTIONS = [
    {"q": "Dãy số: 1, 1, 2, 3, 5, 8, ... Số tiếp theo là bao nhiêu?", "a": 13},
    {"q": "Nếu 3 con mèo bắt 3 con chuột trong 3 phút. Hỏi 100 con mèo bắt 100 con chuột trong bao nhiêu phút?", "a": 3},
    {"q": "Một hồ nước có bèo dại. Mỗi ngày bèo nở gấp đôi ngày hôm trước. Ngày 10 bèo nở kín hồ. Hỏi ngày thứ mấy bèo nở được nửa hồ?", "a": 9},
    {"q": "Có bao nhiêu chữ số 9 xuất hiện trong các số từ 1 đến 100?", "a": 20},
    {"q": "Trong một cuộc chạy thi, nếu bạn vượt qua người đang xếp thứ 2 thì bạn đang xếp thứ mấy?", "a": 2},
    {"q": "Một bác nông dân có 17 con cừu. Tất cả trừ 9 con đều chết. Hỏi bác nông dân còn lại bao nhiêu con cừu sống?", "a": 9},
    {"q": "Năm nay anh 10 tuổi, em 5 tuổi. Hỏi khi anh 20 tuổi thì em bao nhiêu tuổi?", "a": 15},
    {"q": "Tháng nào trong năm có 28 ngày?", "a": 12}, # Mẹo: Tháng nào cũng có ít nhất 28 ngày
    {"q": "Bạn đang ở trong 1 căn phòng tối có 1 cây nến, 1 bếp lò, 1 cây đèn dầu. Quẹt diêm của bạn chỉ còn 1 que. Bạn sẽ thắp sáng vật nào đầu tiên? (Nhập: 1.Cây nến, 2.Bếp lò, 3.Đèn dầu, 4.Que diêm)", "a": 4}
]

class CaroLogicGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Caro Logic - Mất Lượt AI Đánh 2 Lần")
        
        # Cài đặt ban đầu
        self.board_size = 10
        self.win_condition = 5
        self.board = [['' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 'X'
        self.extra_turns = 0 # Số lượt đi thêm (do đối thủ trả lời sai)
        self.buttons = []
        
        # Hỏi chế độ chơi ngay khi mở
        answer = messagebox.askyesno("Chế độ chơi", "Bạn có muốn chơi với Máy tính không?\n\nYes = Người vs Máy\nNo = Người vs Người")
        self.mode = '2' if answer else '1'
        
        self.setup_ui()

    def setup_ui(self):
        # Tạo lưới nút bấm cho bàn cờ
        for r in range(self.board_size):
            row_buttons = []
            for c in range(self.board_size):
                btn = tk.Button(self.root, text='', font=('Consolas', 20, 'bold'), width=3, height=1,
                                command=lambda row=r, col=c: self.on_click(row, col))
                btn.grid(row=r, column=c, padx=1, pady=1)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    def on_click(self, r, c):
        # Ô đã được đánh
        if self.board[r][c] != '':
            return
        
        # Ngăn người chơi bấm lung tung khi đang là lượt của máy tính
        if self.mode == '2' and self.current_player == 'O':
            return
            
        # Rút câu hỏi
        q = random.choice(QUESTIONS)
        ans = simpledialog.askinteger(
            f"Thử thách cho [{self.current_player}]", 
            f"Trả lời đúng để đánh cờ. Sai sẽ bị mất lượt và đối thủ được đi 2 lần!\n\nCâu hỏi:\n{q['q']}\n\n(Chỉ nhập số nguyên)"
        )
        
        if ans is None: # Người chơi bấm Cancel
            return
            
        if ans == q['a']:
            messagebox.showinfo("Chính xác!", "Trí tuệ tuyệt vời! Bạn được phép đặt cờ.")
            self.make_move(r, c)
        else:
            messagebox.showerror("Sai rồi!", f"Đáp án đúng là: {q['a']}.\nBạn đã MẤT LƯỢT. Đối thủ được đi 2 LẦN liên tiếp!")
            self.switch_turn(opponent_gets_extra=True)

    def make_move(self, r, c):
        self.board[r][c] = self.current_player
        color = "blue" if self.current_player == 'X' else "red"
        self.buttons[r][c].config(text=self.current_player, fg=color)
        
        # Kiểm tra thắng/hòa
        if self.check_win(self.current_player):
            messagebox.showinfo("Trò chơi kết thúc", f"Tuyệt vời! [{self.current_player}] đã chiến thắng!")
            self.root.quit()
            return
        if self.check_draw():
            messagebox.showinfo("Trò chơi kết thúc", "Bàn cờ đã kín. Hòa nhau!")
            self.root.quit()
            return

        # Xử lý lượt đi thêm
        if self.extra_turns > 0:
            self.extra_turns -= 1
            if self.mode == '1' and self.extra_turns > 0:
                 messagebox.showinfo("Được đánh tiếp", f"[{self.current_player}] được đánh thêm 1 lần nữa do đối thủ trả lời sai!")
            elif self.mode == '2' and self.current_player == 'O':
                 # Nếu máy tính còn lượt đi thêm, delay một chút rồi đánh tiếp
                 self.root.after(600, self.ai_move)
        else:
            self.switch_turn()

    def switch_turn(self, opponent_gets_extra=False):
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self.extra_turns = 1 if opponent_gets_extra else 0
        
        # Thông báo nếu chơi 2 người mà đối phương được thưởng lượt
        if opponent_gets_extra and self.mode == '1':
             messagebox.showinfo("Lượt của đối thủ", f"Đến lượt [{self.current_player}]. Bạn được đánh 2 ô liên tiếp!")

        # Kích hoạt máy tính đánh
        if self.mode == '2' and self.current_player == 'O':
            self.root.after(600, self.ai_move)

    def ai_move(self):
        empty_cells = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if self.board[r][c] == '']
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.make_move(r, c)

    def check_win(self, player):
        b = self.board
        w = self.win_condition
        s = self.board_size
        
        for r in range(s):
            for c in range(s - w + 1):
                if all(b[r][c+i] == player for i in range(w)): return True
                
        for c in range(s):
            for r in range(s - w + 1):
                if all(b[r+i][c] == player for i in range(w)): return True
                
        for r in range(s - w + 1):
            for c in range(s - w + 1):
                if all(b[r+i][c+i] == player for i in range(w)): return True
                
        for r in range(w - 1, s):
            for c in range(s - w + 1):
                if all(b[r-i][c+i] == player for i in range(w)): return True
                
        return False

    def check_draw(self):
        for row in self.board:
            if '' in row: return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = CaroLogicGame(root)
    # Căn giữa cửa sổ trên màn hình
    root.eval('tk::PlaceWindow . center')
    root.mainloop()