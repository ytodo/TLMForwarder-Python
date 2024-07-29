import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

###########################################################
#			設定ページ例有ると及びエントリー
###########################################################
class SettingsPage(tk.Toplevel, tk.Frame):

	# 新しいウィンドウ(Settings)の生成
	def __init__(self, master):
		tk.Toplevel.__init__(self, master)

		# 現在のアプリの位置を取得
		x = (master.winfo_x() + 200)
		y = (master.winfo_y() + 100)

		# SUBウィンドウの定義
		self.geometry('530x550+{}+{}'.format(x, y))
		self.title('Settings')
		self.configure(bg="#e0e0e0")
		self.grab_set()
		self.focus_set()

		# エントリー用widjetの作成
		self.create_widjet()

	# ウィンドウ内の項目を生成
	def create_widjet(self):
	
		self.label1 = tk.Label(self, text="設定情報を入力してください。", padx = 50, bg="#e0e0e0")
		self.label1.pack(padx=5, pady=5)

		# ラベルリストの定義
		fields = [
			("Callsign", 30, 40),
			("Latitude", 30, 80),
			("Longitude", 30, 120),
			("Height", 30, 160),
			("KISS Address", 30, 200),
			("KISS Port", 30, 240),	
			("TLE Source", 60, 280),
			("Report to", 30, 320),
			("Screen Time", 30, 360),
			("Forwarding", 30, 400),
			("LastUsed", 30, 440),
			("LogDir", 50, 480)
		]

		# フォーム全体にラベル･エントリーを配置、entriesに(text, entry)を追加格納
		def makeform(self, fields):

			# 他の関数内で使用できる様グローバル化
			global entries
			entries = []

			# この関数が終了するまでファイルは開いておく
			f = open("TLMForwarder.ini", mode='r', encoding="UTF-8")

			# fieldsで定義した順番にラベルとエントリーを構成する
			for text, width, posy in fields: 

				# ループに合わせて一行ずつファイルから読む
				line = f.readline().split(': ')
				data = line[1].replace('\n', '')

				# ラベルとエントリーの配置
				label=tk.Label(self, text=text, bg="#e0e0e0")
				entry=tk.Entry(self, width=width)
				entry.insert(0, data)							# 読み込んだデータを規定値として表示
				label.place(x=30, y=posy)
				entry.place(x=110, y=posy)

				# fields リストの順に entries 配列にデータを入れる
				entries.append((text, entry))

			# Settingsに表示されていない座標だけリスト外で配列に加える
			entries.append(('Window_x', entry))
			entries.append(('Window_y', entry))

			# ファイルのクローズ
			f.close
			return entries

		# ディレクトリーを選択した時実行
		def select_directory(entry):

			# ディレクトリの選択ダイアログを表示
			directory = filedialog.askdirectory()

			# 選択したディレクトリーをentryの第2要素へ代入
			entry[1].delete(0, tk.END)
			entry[1].insert(0, directory)

		# ディレクトリ選択ボタンを作成
		btn_dirs = []
		for i in range(len(fields)):
			btn_dir = tk.Button(self, text="参照", command=lambda i=i: select_directory(entries[i]), width=8)
			btn_dir.place(x=420, y=480)
			btn_dirs.append(btn_dir)

		# 保存ボタンが押された時実行されるメソッドを定義
		def store_file(entries):

			# 設定ファイルを書き込みモードで開く
			with open("TLMForwarder.ini", mode='w') as f:
				f.truncate(0)

			# entriesのそれぞれの項目毎にでーた
			for entry in entries:
				field = entry[0]
				data = entry[1].get()	
				with open("TLMForwarder.ini", mode='a') as f:
					f.write('{}: {}\n'.format(field, data))
				
			label=tk.Label(self, text="保存しました。", bg="#e0e0e0")
			label.place(x=400, y=65)

		# makeformの関数呼び出し
		ents = makeform(self, fields)

		# entsの呼び出しを実行し、返り値のentries をstore_file関数に渡す
		self.btn_store = tk.Button(self, text="保存", width=6, command=(lambda e=ents: store_file(e)))
		self.btn_close = tk.Button(self, text="閉じる", width=6, command=self.destroy)
		self.btn_store.place(x=400, y=40)
		self.btn_close.place(x=460, y=40)

	# 設定ファイルからひとつの設定値をkeyで読み出す
	def get_setting(key):

		# 設定ファイルからすべてのラインを読み込む
		with open("TLMForwarder.ini", 'r') as f:
			lines = f.readlines()
			lines_strip = [line.strip() for line in lines]			# すべてのラインの\nを取り除く
			setting = [line for line in lines_strip if key in line]	# ピュアなデータラインからkeyで示された設定値を分別
			setting_split = setting[0].split(': ')
			setval = setting_split[1]
		return setval
	
	# 運用中変更した設定を書き込む(Report to, Screen Time, Forwarding)
	def replace_setting(replace_set):
		target, replace = replace_set

		# 設定ファイルからすべてのラインを読み込む
		with open("TLMForwarder.ini", 'r') as fr:
			tmp_list = []											# この関数内でのみ使用
			for line in fr:
				if line.find(target) != -1:							# 例:Report toが見つかったら 
					tmp_list.append((target)+": "+replace+"\n")		# 変更後の値を：で繋いで改行する
				else:
					tmp_list.append(line)							# その他の行は読んだまま

		with open("TLMForwarder.ini", 'w') as fw:
			for i in range(len(tmp_list)):
				fw.write(tmp_list[i])								# 編集後のリストをファイルに書き込む

