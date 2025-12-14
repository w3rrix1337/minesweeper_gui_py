import tkinter as tk
from tkinter import messagebox
import random

class MinesweeperGUI:
    def __init__(self, master):
        self.master = master
        master.title("Сапер (Minesweeper)")

        self.width = 0
        self.height = 0
        self.mines = 0
        self.buttons = []
        self.game_running = False
        self.mine_locations = []
        self.revealed_count = 0
        self.flag_count = 0

        self.difficulties = {
            "Новичок": (9, 9, 10),
            "Любитель": (16, 16, 40),
            "Профессионал": (30, 16, 99)
        }

        self.setup_difficulty_menu()

    def setup_difficulty_menu(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        self.menu_frame = tk.Frame(self.master)
        self.menu_frame.pack(padx=20, pady=20)

        tk.Label(self.menu_frame, text="Выберите сложность", font=('Arial', 14, 'bold')).pack(pady=10)

        for name, params in self.difficulties.items():
            text = f"{name} ({params[0]}x{params[1]}, {params[2]} мин)"
            tk.Button(self.menu_frame, text=text,
                      command=lambda w=params[0], h=params[1], m=params[2]: self.start_game(w, h, m),
                      width=30).pack(pady=5)

        tk.Button(self.menu_frame, text="Кастомная сложность",
                  command=self.setup_custom_difficulty,
                  width=30).pack(pady=10)

    def setup_custom_difficulty(self):
        custom_window = tk.Toplevel(self.master)
        custom_window.title("Кастомные настройки")

        tk.Label(custom_window, text="Ширина:").grid(row=0, column=0, padx=5, pady=5)
        self.w_entry = tk.Entry(custom_window, width=10)
        self.w_entry.grid(row=0, column=1, padx=5, pady=5)
        self.w_entry.insert(0, "10")

        tk.Label(custom_window, text="Высота:").grid(row=1, column=0, padx=5, pady=5)
        self.h_entry = tk.Entry(custom_window, width=10)
        self.h_entry.grid(row=1, column=1, padx=5, pady=5)
        self.h_entry.insert(0, "10")

        tk.Label(custom_window, text="Мины:").grid(row=2, column=0, padx=5, pady=5)
        self.m_entry = tk.Entry(custom_window, width=10)
        self.m_entry.grid(row=2, column=1, padx=5, pady=5)
        self.m_entry.insert(0, "15")

        def start_custom():
            try:
                w = int(self.w_entry.get())
                h = int(self.h_entry.get())
                m = int(self.m_entry.get())

                if w < 5 or h < 5 or m <= 0 or m >= w * h:
                    messagebox.showerror("Ошибка", "Неверные параметры. Ширина/Высота >= 5. 0 < Мины < Общее кол-во ячеек.")
                    return

                custom_window.destroy()
                self.start_game(w, h, m)
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите целые числа.")

        tk.Button(custom_window, text="Начать игру", command=start_custom).grid(row=3, column=0, columnspan=2, pady=10)

    def start_game(self, width, height, mines):
        self.width = width
        self.height = height
        self.mines = mines
        self.revealed_count = 0
        self.flag_count = 0
        self.game_running = True

        for widget in self.master.winfo_children():
            widget.destroy()

        self.status_label = tk.Label(self.master, text="Флаги: 0", font=('Arial', 12))
        self.status_label.pack(pady=5)

        self.board_frame = tk.Frame(self.master)
        self.board_frame.pack()

        self.create_board()
        self.place_mines()
        self.calculate_numbers()

        tk.Button(self.master, text="Сменить сложность", command=self.setup_difficulty_menu).pack(pady=10)

    def create_board(self):
        self.buttons = []
        for r in range(self.height):
            row = []
            for c in range(self.width):
                btn = tk.Button(self.board_frame, text="", width=2, height=1,
                                command=lambda r=r, c=c: self.on_left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.on_right_click(r, c))

                btn.grid(row=r, column=c)

                btn.is_mine = False
                btn.is_revealed = False
                btn.is_flagged = False
                btn.neighbor_mines = 0

                row.append(btn)
            self.buttons.append(row)

    def place_mines(self):
        mine_coords = random.sample([(r, c) for r in range(self.height) for c in range(self.width)], self.mines)

        for r, c in mine_coords:
            self.buttons[r][c].is_mine = True

    def calculate_numbers(self):
        for r in range(self.height):
            for c in range(self.width):
                if not self.buttons[r][c].is_mine:
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.height and 0 <= nc < self.width and self.buttons[nr][nc].is_mine:
                                count += 1
                    self.buttons[r][c].neighbor_mines = count

    def on_left_click(self, r, c):
        if not self.game_running: return
        btn = self.buttons[r][c]

        if btn.is_revealed or btn.is_flagged: return

        if btn.is_mine:
            self.game_running = False
            self.reveal_all_mines(r, c)
            messagebox.showinfo("Game Over", "💥 БУМ! Вы взорвались!")
            return

        self.reveal_cell(r, c)
        self.check_win()

    def on_right_click(self, r, c):
        if not self.game_running: return
        btn = self.buttons[r][c]

        if btn.is_revealed: return

        btn.is_flagged = not btn.is_flagged

        if btn.is_flagged:
            btn.config(text="🚩", state=tk.DISABLED, disabledforeground='red')
            self.flag_count += 1
        else:
            btn.config(text="", state=tk.NORMAL)
            self.flag_count -= 1

        self.status_label.config(text=f"Флаги: {self.flag_count}")
        self.check_win()

    def reveal_cell(self, r, c):
        if not (0 <= r < self.height and 0 <= c < self.width):
            return

        btn = self.buttons[r][c]

        if btn.is_revealed or btn.is_flagged or btn.is_mine:
            return

        btn.is_revealed = True
        self.revealed_count += 1

        mines_count = btn.neighbor_mines

        btn.config(relief=tk.SUNKEN, text=str(mines_count) if mines_count > 0 else "",
                   state=tk.DISABLED, disabledforeground=self.get_number_color(mines_count))

        if mines_count == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr != 0 or dc != 0:
                        self.reveal_cell(r + dr, c + dc)

    def reveal_all_mines(self, clicked_r, clicked_c):
        for r in range(self.height):
            for c in range(self.width):
                btn = self.buttons[r][c]
                if btn.is_mine:
                    if r == clicked_r and c == clicked_c:
                        btn.config(text="💥", bg='red', disabledforeground='black')
                    elif btn.is_flagged:
                        btn.config(text="❌", bg='orange', disabledforeground='black')
                    else:
                        btn.config(text="💣", bg='lightgray', disabledforeground='black')
                    btn.config(state=tk.DISABLED, relief=tk.SUNKEN)
                elif btn.is_flagged and not btn.is_mine:
                    btn.config(text="❌", bg='orange', disabledforeground='black', state=tk.DISABLED)

    def check_win(self):
        safe_cells = self.width * self.height - self.mines

        if self.revealed_count == safe_cells:
            self.game_running = False
            for r in range(self.height):
                for c in range(self.width):
                    btn = self.buttons[r][c]
                    btn.config(state=tk.DISABLED)
                    if btn.is_mine and not btn.is_flagged:
                        btn.config(text="🚩")

            messagebox.showinfo("Победа!", "🎉 Поздравляем! Вы выиграли!")

    def get_number_color(self, count):
        colors = {
            1: 'blue', 2: 'green', 3: 'red', 4: 'navy',
            5: 'brown', 6: 'turquoise', 7: 'black', 8: 'gray'
        }
        return colors.get(count, 'black')

if __name__ == "__main__":
    root = tk.Tk()
    game = MinesweeperGUI(root)
    root.mainloop()
