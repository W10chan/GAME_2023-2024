import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random
import csv
import numpy as np
import pandas as pd

FILE_KABUKA = "yamato_add_noise_sd=500.csv"
#kabukadata_yamato.csv
#softbank
#yamaha
#yamato
#omuron_price
#lasertech
#sony


FILE_RECORD = "記録テスト2.csv"


class GoldTradingGame:
    def __init__(self, root,  initial_total_assets = 0, initial_balance=1000000, gold_quantity=200):
        self.root = root
        self.root.title("株取引ゲーム")

        self.xs = []
        self.ys = []

        self.game_started = False  # ゲーム開始フラグ
        self.total_assets = initial_total_assets + initial_balance
        self.gold_quantity = gold_quantity
        self.balance = initial_balance
        self.buy_quantity = 0
        self.sell_quantity = 0
        self.trading_volume = 0

        self.data = pd.read_csv(FILE_KABUKA)
        self.current_row = 0
        self.x_labels = []  # 日付のラベルをリストに格納
        self.selected_column = "DummyPrice"  # プロットしたいデータ列の名前を指定してください

        # 価格データをカンマを取り除いた数値に変換
        self.data[self.selected_column] = self.data[self.selected_column].str.replace(",", "").astype(int)
        #self.figure, self.ax = plt.subplots(figsize=(8, 4))
        #self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        #self.canvas_widget = self.canvas.get_tk_widget()
        #self.canvas_widget.pack()
        self.history = []
        self.price_history = []#取引の記録用リスト

        # 直線の初期化
        self.line = None

        self.current_day = 0  # 初期日数を設定
        self.rest_day = 0
        self.total_assets_label = None  # 総資産を表示するラベル
        self.gold_quantity_label = None  # 手持ちの金量を表示するラベル
        self.balance_label = None  # 所持金を表示するラベル
        self.previous_gold_price = None  # 一つ前の金価格を格納する変数
        self.error_label = None  # エラーメッセージ用のラベル
        self.create_gui()
        self.start_label = None  # "先月の相場" ラベル用の変数
        self.total_months = 26  # ゲームの総取引月数
        self.current_month = 0  # 現在の取引月
        

        # ゲーム終了条件
        self.game_over = False
    

    def save_to_csv(self):
        # Define the CSV file name (you can change this)
        #filename = "jikkenn.csv"

        # Create or open the CSV file in write mode
        with open(FILE_RECORD, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write the CSV header
            writer.writerow(["Day", "Stock Price", "Trading Stock", "Buy Quantity", "Sell Quantity", "Total Assets",  "Balance", "Stock Quantity"])

            # Write the data for each trading day
            for day, (gold_price, trading_volume, buy_quantity, sell_quantity, total_assets, balance, gold_quantity) in enumerate(self.price_history):
                writer.writerow([day, gold_price, trading_volume, buy_quantity, sell_quantity, total_assets, balance, gold_quantity])

    def show_error_message(self, message):
        # エラーメッセージを表示し、一定時間後に消す
        if self.error_label:
            self.error_label.destroy()
        self.error_label = tk.Label(text=message)
        self.error_label.pack()
        self.root.after(2000, self.clear_error_message)  # 2000ミリ秒（2秒）後にエラーメッセージを消す

    def clear_error_message(self):
        # エラーメッセージを消す
        if self.error_label:
            self.error_label.destroy()

    def buy_gold(self,quantity):
        # 100株単位で売買するように制限
        if quantity % 100 != 0:
            error_message = "取引数量は100株単位で指定してください。"
            print(error_message)
            self.show_error_message(error_message)
            return

        cost = quantity * self.gold_price
        if self.balance >= cost:
            self.gold_quantity += quantity
            self.balance -= cost
            self.previous_gold_price = self.gold_price  # 金価格を記録
            #self.total_assets = self.balance + cost
            self.trading_volume = quantity
            self.record_transaction(quantity, cost, "購入")
            # Append the trading data to the price history
            self.total_assets = self.balance + (self.gold_quantity * self.gold_price)
            self.price_history.append((self.gold_price, self.trading_volume, self.buy_quantity,  self.sell_quantity, self.total_assets, self.balance, self.gold_quantity))

        # Save the data to CSV at the end of each trading day
            self.save_to_csv()
            self.create_plot()
            print(f"{quantity} グラムの金を購入しました。")
        else:
            error_message = "購入するための十分な資金がありません。"
            print(error_message)
            self.show_error_message(error_message)

    def buy_gold_wrapper(self):
        # ユーザーが入力した金の数量を取得
        quantity_str = self.quantity_entry.get()
        try:
            self.buy_quantity = float(quantity_str)  # 入力が数値か確認
            if (self.buy_quantity > 0):
                self.buy_gold(self.buy_quantity)
                self.quantity_entry.delete(0, tk.END)  # エントリをクリア
            else:
                error_message = "正の株数を入力してください。"
                print(error_message)
                self.show_error_message(error_message)
        except ValueError:
            error_message = "有効な数値を入力してください。"
            print(error_message)

    def sell_gold(self, quantity):
        # 100株単位で売買するように制限
        if quantity % 100 != 0:
            error_message = "取引数量は100株単位で指定してください。"
            print(error_message)
            self.show_error_message(error_message)
            return

        if self.gold_quantity >= quantity:
            revenue = quantity * self.gold_price
            self.previous_gold_price = self.gold_price  # 金価格を記録
            self.gold_quantity -= quantity
            self.balance += revenue

        # Append the trading data to the price history
            self.total_assets = self.balance + (self.gold_quantity * self.gold_price)
            #self.total_assets = self.balance + revenue
            self.trading_volume = -quantity
            self.record_transaction(quantity, revenue, "売却")
            print(f"{quantity} 株を売却しました。")
            self.price_history.append((self.gold_price, self.trading_volume, self.buy_quantity,  self.sell_quantity, self.total_assets, self.balance, self.gold_quantity))

        # Save the data to CSV at the end of each trading day
            self.save_to_csv()
            self.create_plot()
        else:
            error_message = "売却するための十分な金がありません。"
            print(error_message)
            self.show_error_message(error_message)

    def sell_gold_wrapper(self):
        # ユーザーが入力した金の数量を取得
        quantity_str = self.quantity_entry.get()
        try:
            self.sell_quantity = float(quantity_str)  # 入力が数値か確認
            if self.sell_quantity > 0:
                #quantity = self.sell_quantity
                self.sell_gold(self.sell_quantity)
                self.quantity_entry.delete(0, tk.END)  # エントリをクリア
            else:
                error_message = "正の株数を入力してください。"
                print(error_message)
                self.show_error_message(error_message)
        except ValueError:
            error_message = "有効な数値を入力してください。"
            print(error_message)
            self.show_error_message(error_message)
    
    def next_day(self):

        # Append the trading data to the price history
        self.total_assets = self.balance + (self.gold_quantity * self.gold_price)
        self.buy_quantity = 0
        self.sell_quantity = 0
        self.trading_volume = 0
        self.price_history.append((self.gold_price, self.trading_volume, self.buy_quantity,  self.sell_quantity, self.total_assets, self.balance, self.gold_quantity))

        # Save the data to CSV at the end of each trading day
        self.save_to_csv()
        self.create_plot()


    def record_transaction(self, quantity, amount, transaction_type):
        # 取引履歴に取引の詳細を追加
        transaction_details = f"取引経過: {self.current_month} ヶ月目, 1株の価格: {self.gold_price:.0f} 円, {transaction_type}: {quantity} g, 金額: {amount:.0f} 円"
        self.history.append(transaction_details)

        # 取引履歴をテキストウィジェットに表示
        self.history_text.delete('1.0', tk.END)  # テキストウィジェットをクリア
        for entry in self.history:
            self.history_text.insert(tk.END, entry + '\n')

    def update_labels(self):
        # 総資産、手持ちの金量、所持金のラベルを更新
        total_assets = self.balance + (self.gold_quantity * self.gold_price)
        self.total_assets_label.config(text=f'総資産: {total_assets:.0f} 円')
        self.gold_quantity_label.config(text=f'手持ちの株: {self.gold_quantity:.2f} 株')
        self.balance_label.config(text=f'所持金: {self.balance:.0f} 円')

        # 取引回数を更新
        self.rest_day -= 1
        self.label_day.config(text=f'残り{self.rest_day} 回取引出来ます。')

        self.check_game_over()

        """if self.current_row >= len(self.data): #or self.current_row >= len(self.data) self.rest_day <= 0 or 
            self.game_over = True
            print("fin!")
            self.label_day = tk.Label(self.root, font=("Helvetica", 20), text=f'ゲーム終了！！責任者を呼んでください。', relief=tk.SOLID, bd=2,)  # 日付ラベルを追加"""

        # ゲーム開始ボタンを無効にしたラベルを削除
        if self.start_label:
            self.start_label.destroy()

        # 金価格をラベルに表示
        self.label_gold_price_today.config(text=f'1株当たりの価格: {self.gold_price:.0f} 円')

    def check_game_over(self):
        if self.rest_day == 0: #self.current_month > self.total_months: #self.current_row >= len(self.data)
            self.game_over = True
            print("fin!")
            self.label_day = tk.Label(self.root, font=("Helvetica", 20), text=f'ゲーム終了！！責任者を呼んでください。', relief=tk.SOLID)  # 日付ラベルを追加 , bd=2, width=25
            self.label_day.pack()
            # ゲーム終了時の適切なアクションをここで実行
            # 例: ウィンドウを閉じるなど
            self.plot_button.config(state=tk.DISABLED)
            self.buy_button.config(state=tk.DISABLED)
            self.sell_button.config(state=tk.DISABLED)

            self.game_started = True  # ゲーム開始フラグを設定
        """if self.current_month >= self.total_months or self.rest_day <= 0:
            self.game_over = True
            print("ゲーム終了")
            self.label_day = tk.Label(self.root, font=("Helvetica", 20), text=f'ゲーム終了！！責任者を呼んでください。', relief=tk.SOLID, bd=2, width=25)  # 日付ラベルを追加
    # ゲーム終了時の適切なアクションをここで実行
        # 例: ウィンドウを閉じるなど
            self.plot_button.config(state=tk.DISABLED)
            self.buy_button.config(state=tk.DISABLED)
            self.sell_button.config(state=tk.DISABLED)

            self.game_started = True  # ゲーム開始フラグを設定"""
        """if self.current_month > self.total_months:
            self.game_over = True
            print("ゲーム終了")
            self.label_day = tk.Label(self.root, font=("Helvetica", 20), text=f'ゲーム終了！！責任者を呼んでください。', relief=tk.SOLID, bd=2, width=25)  # 日付ラベルを追加
            # ゲーム終了時の適切なアクションをここで実行
            # 例: ウィンドウを閉じるなど
            self.plot_button.config(state=tk.DISABLED)
            self.buy_button.config(state=tk.DISABLED)
            self.sell_button.config(state=tk.DISABLED)

            self.game_started = True  # ゲーム開始フラグを設定"""

    def create_gui(self):

        self.label_day = tk.Label(self.root, font=("Helvetica", 20), text=f'残り {self.rest_day} 回取引できます。', relief=tk.SOLID, bd=2, width=25)  # 日付ラベルを追加
        self.label_day.pack(pady=5)

        self.label_gold_price_today = tk.Label(self.root, font=("Helvetica", 20), text=f'一株当たりの価格:', relief=tk.SOLID, bd=2, width=20)
        self.label_gold_price_today.pack(pady=5)

        #self.button_start = tk.Button(self.history_window, text='ゲーム開始', font=("Helvetica", 15), pady=15, command=self.start_game)
        #self.button_start.pack()

        # プロット領域を作成
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # メニューに「取引履歴を表示」オプションを追加
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        history_menu = tk.Menu(menubar)
        menubar.add_cascade(label="取引入力と記録", menu=history_menu)
        history_menu.add_command(label="表示", command=self.show_transaction_history)

        # 取引履歴用のウィンドウを作成
        self.history_window = tk.Toplevel(self.root)
        self.history_window.title("取引入力と履歴閲覧")
        self.history_window.geometry("400x400")

        # スペースを追加
        space_label = tk.Label(self.history_window, text='', font=("Helvetica", 10))
        space_label.pack()

        self.total_assets_label = tk.Label(self.history_window, font=("Helvetica", 20), text='総資産:', relief=tk.RIDGE, borderwidth=2)
        self.total_assets_label.pack(pady=5)

        self.gold_quantity_label = tk.Label(self.history_window, font=("Helvetica", 20), text='手持ちの株数:', relief=tk.RIDGE, borderwidth=2)
        self.gold_quantity_label.pack(pady=5)

        self.balance_label = tk.Label(self.history_window, font=("Helvetica", 20), text='所持金:', relief=tk.RIDGE, borderwidth=2)
        self.balance_label.pack(pady=5)

# スペースを追加
        space_label = tk.Label(self.history_window, text='', font=("Helvetica", 10))
        space_label.pack()

        # Create GUI elements
        self.button_start = tk.Button(self.history_window, text='ゲーム開始', font=("Helvetica", 15), pady=15, command=self.start_game)
        self.button_start.pack()
        self.quantity_label = tk.Label(self.history_window, font=("Helvetica", 10), text="取引する株数を入力してください\n取引を行わない場合は、\n次の取引日のボタンを押して、進んでください。")
        self.quantity_label.pack(pady=5)

        self.quantity_entry = tk.Entry(self.history_window, font=("Helvetica", 15))
        self.quantity_entry.pack(pady=5)

        self.buy_button = tk.Button(self.history_window, font=("Helvetica", 17), text="株を購入", command=self.buy_gold_wrapper)
        self.buy_button.pack(pady=2)

        self.sell_button = tk.Button(self.history_window, font=("Helvetica", 17), text="株を売却", command=self.sell_gold_wrapper)
        self.sell_button.pack(pady=2)

        # ボタンを作成してプロットを更新
        self.plot_button = tk.Button(self.history_window, font=("Helvetica", 17), text="次の取引日へ", command=self.next_day)
        self.plot_button.pack(pady=2)

        # スペースを追加
        space_label = tk.Label(self.history_window, text='', font=("Helvetica", 10))
        space_label.pack()

        self.history_text = tk.Text(self.history_window, height=10, width=40,  font=("Helvetica", 12))
        self.history_text.pack()

        pass

    def show_transaction_history(self):
        # 取引履歴ウィンドウを表示
        self.history_text.delete('1.0', tk.END)  # テキストウィジェットをクリア
        for entry in self.history:
            self.history_text.insert(tk.END, entry + '\n')
        self.history_window.lift()

    def start_game(self):
        # ゲーム開始ボタンが押されたときの処理
        self.rest_day = 26
        if not self.game_started:
            self.create_plot()

        # 先月の相場を表示するラベルを作成
            if self.start_label is None:
                self.start_label = tk.Label(self.root, font=("Helvetica", 17), text=f'先月の相場は {self.gold_price:.0f} 円でした。取引は来月からできます。\n次の取引日のボタンを押して、進んでください。')
                self.start_label.pack()

        # ゲーム開始ボタンを無効にする
            self.button_start.config(state=tk.DISABLED)

            # 購入ボタン、売却ボタン、plot ボタンを有効にする
            self.buy_button.config(state=tk.NORMAL)
            self.sell_button.config(state=tk.NORMAL)
            self.plot_button.config(state=tk.NORMAL)

            self.game_started = True  # ゲーム開始フラグを設定

    #def plot(self)
        

    def create_plot(self):
    # ゲームが終了している場合は更新しない
        """if self.game_over :#or self.current_row >= len(self.data)
                return"""
        if self.current_row < len(self.data):
            self.gold_price = self.data.loc[self.current_row, self.selected_column]
        #self.current_row += 1
        #mean = MEAN  # Mean of the normal distribution
        #std_dev = STDV
        #self.gold_price = random.gauss(mean, std_dev)
        self.xs.append(len(self.xs))
        if self.ys:
            self.ys.append(self.gold_price)
        else:
            self.ys.append(self.gold_price)

        self.ax.clear()
        self.ax.plot(self.xs, self.ys)

        self.ax.plot(self.current_row, self.gold_price, marker='o', color='blue')
        self.ax.set_xlabel('取引日(月)',fontname="Meiryo")
        self.ax.set_ylabel('株価(円)',fontname="Meiryo")
        self.ax.set_title('価格の推移',fontname="Meiryo")
        #self.canvas.draw()

        # 直線を描画
        if self.current_row > 0:
            prev_price = self.data.loc[self.current_row - 1, self.selected_column]
            self.line = self.ax.plot([self.current_row - 1, self.current_row], [prev_price, self.gold_price], color='green', linestyle='-', marker='o')

        # X軸の日付ラベルを設定
        self.x_labels.append(self.data.loc[self.current_row, "Day"])  # "Day" 列はCSVファイル内の日付列の名前に置き換えてください
        self.ax.set_xticks(np.arange(len(self.x_labels)))
        self.ax.set_xticklabels(self.x_labels, rotation=45, ha="right")

        self.canvas.draw()
        #self.current_row += 1

        """# Append the trading data to the price history
        self.total_assets = self.balance + (self.gold_quantity * self.gold_price)
        self.price_history.append((self.gold_price, self.trading_volume, self.buy_quantity,  self.sell_quantity, self.total_assets, self.balance, self.gold_quantity))

        # Save the data to CSV at the end of each trading day
        self.save_to_csv()"""""

        self.buy_quantity = 0
        self.sell_quantity = 0
        self.trading_volume = 0
        self.current_month += 1
        self.update_labels()  # ラベルを更新
        self.current_row += 1
        # ゲーム終了条件をチェック
        #self.check_game_over()




if __name__ == "__main__":
    root = tk.Tk()
    app = GoldTradingGame(root)
    root.mainloop()
