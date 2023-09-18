import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random


MEAN = 6782
STDV = 385

class GoldTradingGame:
    def __init__(self, root,  initial_total_assets = 0, initial_balance=1000000, gold_quantity=0):
        self.root = root
        self.root.title("金取引ゲーム")

        self.xs = []
        self.ys = []

        self.total_assets = initial_total_assets + initial_balance
        self.gold_quantity = gold_quantity
        self.balance = initial_balance
        self.history = []
        self.price_history = []

        self.current_day = 0  # 初期日数を設定
        self.total_assets_label = None  # 総資産を表示するラベル
        self.gold_quantity_label = None  # 手持ちの金量を表示するラベル
        self.balance_label = None  # 所持金を表示するラベル
        self.create_gui()

        self.start_label = None  # "先月の相場" ラベル用の変数

    def buy_gold(self, quantity):
        cost = quantity * self.gold_price
        if self.total_assets >= cost:
            self.gold_quantity += quantity
            self.balance -= cost
            self.create_plot()
            print(f"{quantity} グラムの金を購入しました。")
        else:
            print("購入するための十分な資金がありません。")

    def buy_gold_wrapper(self):
        # ユーザーが入力した金の数量を取得
        quantity_str = self.quantity_entry.get()
        try:
            quantity = float(quantity_str)  # 入力が数値か確認
            if quantity > 0:
                self.buy_gold(quantity)
                self.quantity_entry.delete(0, tk.END)  # エントリをクリア
            else:
                print("正の金の数量を入力してください。")
        except ValueError:
            print("有効な数値を入力してください。")

    def sell_gold(self, quantity):
        if self.gold_quantity >= quantity:
            revenue = quantity * self.gold_price
            self.gold_quantity -= quantity
            self.balance += revenue
            self.create_plot()
            print(f"{quantity} グラムの金を売却しました。")
        else:
            print("売却するための十分な金がありません。")

    def sell_gold_wrapper(self):
        # ユーザーが入力した金の数量を取得
        quantity_str = self.quantity_entry.get()
        try:
            quantity = float(quantity_str)  # 入力が数値か確認
            if quantity > 0:
                self.sell_gold(quantity)
                self.quantity_entry.delete(0, tk.END)  # エントリをクリア
            else:
                print("正の金の数量を入力してください。")
        except ValueError:
            print("有効な数値を入力してください。")

    def update_labels(self):
        # 総資産、手持ちの金量、所持金のラベルを更新
        total_assets = self.balance + (self.gold_quantity * self.gold_price)
        self.total_assets_label.config(text=f'総資産: {total_assets:.0f} 円')
        self.gold_quantity_label.config(text=f'手持ちの金量: {self.gold_quantity:.2f} グラム')
        self.balance_label.config(text=f'所持金: {self.balance:.0f} 円')

    def create_gui(self):
        self.total_assets_label = tk.Label(self.root, text='総資産:')
        self.total_assets_label.pack()

        self.gold_quantity_label = tk.Label(self.root, text='手持ちの金量:')
        self.gold_quantity_label.pack()

        self.balance_label = tk.Label(self.root, text='所持金:')
        self.balance_label.pack()

        # プロット領域を作成
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create GUI elements
        self.label_gold_price_today = tk.Label(self.root, text='今日の金価格:')
        self.label_gold_price_today.pack()

        self.label_day = tk.Label(self.root, text=f'取引日: {self.current_day} ヶ月目')  # 日付ラベルを追加
        self.label_day.pack()

        self.quantity_label = tk.Label(self.root, text="金のグラム数:")
        self.quantity_label.pack()

        self.quantity_entry = tk.Entry(self.root)
        self.quantity_entry.pack()

        self.buy_button = tk.Button(self.root, text="金を購入", command=self.buy_gold_wrapper)
        self.buy_button.pack()

        self.sell_button = tk.Button(self.root, text="金を売却", command=self.sell_gold_wrapper)
        self.sell_button.pack()

        # ボタンを作成してプロットを更新
        self.plot_button = ttk.Button(self.root, text="次の取引日", command=self.create_plot)
        self.plot_button.pack()

        self.button_start = tk.Button(self.root, text='ゲーム開始', command=self.start_game)
        self.button_start.pack()

    def start_game(self):
        # ゲーム開始ボタンが押されたときの処理
        mean = MEAN  # 先月の相場
        std_dev = STDV
        self.gold_price = random.gauss(mean, std_dev)
        self.xs.append(len(self.xs))
        if self.ys:
            self.ys.append(self.gold_price)
        else:
            self.ys.append(self.gold_price)

        # 先月の相場を表示するラベルを作成
        if self.start_label is None:
            self.start_label = tk.Label(self.root, text=f'先月の相場: {self.gold_price:.0f} 円')
            self.start_label.pack()

        # ゲーム開始ボタンを無効にする
        self.button_start.config(state=tk.DISABLED)

    def create_plot(self):
        mean = MEAN  # Mean of the normal distribution
        std_dev = STDV
        self.gold_price = random.gauss(mean, std_dev)
        self.xs.append(len(self.xs))
        if self.ys:
            self.ys.append(self.gold_price)
        else:
            self.ys.append(self.gold_price)

        self.ax.clear()
        self.ax.plot(self.xs, self.ys)
        self.ax.set_xlabel('取引日(月)')
        self.ax.set_ylabel('金価格(円)')
        self.ax.set_title('金価格の推移')
        self.canvas.draw()

        # 取引日付を更新
        self.current_day += 1
        self.label_day.config(text=f'取引経過: {self.current_day} ヶ月目')

        # ゲーム開始ボタンを無効にしたラベルを削除
        if self.start_label:
            self.start_label.destroy()

        # 金価格をラベルに表示
        self.label_gold_price_today.config(text=f'今日の金価格: {self.gold_price:.0f} 円')
        self.update_labels()  # ラベルを更新

if __name__ == "__main__":
    root = tk.Tk()
    app = GoldTradingGame(root)
    root.mainloop()
