# ライブラリー呼び出し
import tkinter as tk
import tkinter.ttk as ttk
import my_icon
import logging
import subprocess
import sys
import os
from tkinter import *
from datetime import datetime, timezone
from PIL import ImageTk, Image, ImageDraw, ImageFont

# ファイル別クラスの参照
from pageset import MainPage
from settings import SettingsPage
from functions import Functions
from clientapps import SatNOGS_Client, KISSclient
from dataformat import ID53106, ID49069

VERSION = "v.1.0.18"

##########################################################
# アプリケーションクラス
##########################################################
class Main(tk.Tk):

	def	__init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

	#
	# メインウィンドウの基本フレーム設定
	#
		# [閉じる X]ボタンを無効にする
		def disable_close_button():
			pass
		self.protocol("WM_DELETE_WINDOW", disable_close_button)

		# 前回のアプリケーションフォームの立ち上げ位置を取得
		x = SettingsPage.get_setting("Window_x").strip()
		y = SettingsPage.get_setting("Window_y").strip()

		self.title("TLMForwarder " + VERSION)
		self.geometry("640x480+{}+{}".format(x, y)) 						# 位置は省略可能 +500+300
		self.resizable(True, True)
		self.configure(bg='#e0e0e0')

		photo = my_icon.get_image4icon()
		self.iconphoto(False, photo)

		### menu_bar Frameインスタンス生成
		menu_bar = tk.Frame(self.master, relief=tk.FLAT, bd=0, width=640, height=26)
		menu_bar.place(x=0, y=0)

		# widjetをレイアウトする frame(upperpane)を生成する
		upperpane = tk.Frame(self.master, relief=tk.FLAT, bd=0, width=640, height=74, bg="#e0e0e0")
		upperpane.place(x=0, y=26)

		# DigipeaterとTelemetryを表示するフレームを定義
		frame_title_back = tk.Frame(self.master, relief=tk.FLAT, bd=0, width=630, height=24, bg="white")
		frame_title_back.place(x=5, y=100)
		frame_tlm = tk.Frame(self.master, relief=tk.FLAT, bd=0, width=626, height=329, bg="red", padx=4, pady=4)
		frame_tlm.place(x=7, y=126)	# original height = 126
		frame_dpt = tk.Frame(self.master, relief=tk.FLAT, bd=0, width=626, height=329, bg="#33bb33", padx=4, pady=4)
		frame_dpt.place(x=7, y=126)	# original height = 126
		frame_cvr = tk.Frame(self.master, relief=tk.FLAT, bd=0, width=630, height=355, bg="white")
		frame_cvr.place(x=5, y=100) # original: 5, 124

	#
	# 初期画面にプライベート画像を表示する
	#
		##### 説明表示入りの画像を作成保存 #####################

		# 画像と文字を表示するためのフォント指定
		font1 = ImageFont.truetype("arial.ttf", 10)
		font2 = ImageFont.truetype("arial.ttf", 12)

		# frame2の画像を読み込む
		frame2 = Image.open("image.png")

		# テキスト指定
		label_text1 = "TLMForwarder by Y.Todo / JE3HCZ"
		label_text2 = "Please set up first"
		label_text3 = " with [SETTINGS] button\nAnd REBOOT\nafter changing the SAT."
		
		# frame2にテキストを書き込む
		draw = ImageDraw.Draw(frame2)
		draw.text((450, 335), label_text1, font=font1, fill=(255, 255, 255, 255))
		draw.text((480,   5), label_text2, font=font2, fill=(255, 255, 255, 255))
		draw.text((480,  18), label_text3, font=font2, fill=(255, 255, 255, 255))
		
		# テキストラベルと背景を透明にする
		label1 = Image.new('RGBA', (150, 50), (0, 0, 0, 0))
		draw = ImageDraw.Draw(label1)
		draw.text((0, 0), label_text1, font=font1, fill=(255, 255, 255, 255))

		label2 = Image.new('RGBA', (150, 50), (0, 0, 0, 0))
		draw = ImageDraw.Draw(label2)
		draw.text((0, 0), label_text2, font=font2, fill=(255, 255, 255, 255))
		
		label3 = Image.new('RGBA', (150, 50), (0, 0, 0, 0))
		draw = ImageDraw.Draw(label3)
		draw.text((0, 0), label_text3, font=font2, fill=(255, 255, 255, 255))

		# 透明なlabelをfreme2に貼り付ける
		frame2.paste(label1, (450, 335), mask=label1)
		frame2.paste(label2, (480,   5), mask=label2)
		frame2.paste(label3, (480,  18), mask=label3)

		# 画像を保存する
		frame2.save("result.png")

		##### 画像作成終わり ###############################

		# 画像表示用キャンバス
		self.canvas = tk.Canvas(self, relief=tk.FLAT, width=626, height=350, bg='white')
		self.canvas.place(x=5, y=100)

		# キャンバスのセンターを取得
		self.update()
		canvas_width = self.canvas.winfo_width()
		canvas_height = self.canvas.winfo_height()

		# 初期画面に画像を貼り付け
		self.img = ImageTk.PhotoImage(file="result.png")				# 画像作成で出来上がった result.pngを表示
		self.canvas.create_image(
			canvas_width / 2,											# 画像の縦横センターを指定
			canvas_height /2,											# キャンバスサイズの半分
			image=self.img
		)

	#
	# メインページWidjetの配置
	#
		# メインページインスタンス
		self.main_page = MainPage(self, frame_tlm, frame_dpt, frame_cvr, menu_bar, upperpane)

		### menu_barへ時計を表示
		def chk_time(menu_bar, dt):
			now = datetime.now()
			if menu_bar.var_tm.get() == 1:
				dt.set(now.strftime('%Y-%m-%d %H:%M:%S')) 				# リアルタイム時刻表示
				timestamp = now.strftime('%H:%M:%S')					# 受信データヘッダー部用テキスト
			else:
				dt.set(now.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
				timestamp = now.astimezone(timezone.utc).strftime('%H:%M:%S')
			menu_bar.after(1000, lambda:chk_time(menu_bar, dt))
			return timestamp

		# 時計ラベルのテキストデータとしてdtを指定
		dt = tk.StringVar()
		lb_dt=tk.Label(menu_bar, textvariable=dt, font=('Verdana', 10, 'bold'))
		lb_dt.place(x=380, y=2)
		menu_bar.after(1000, lambda:chk_time(menu_bar, dt))				# 時刻取得の再帰呼び出し

	#
	# 受信データのリアルタイム表示
	#
		### 受信したテレメトリーを表示するテキストウィジェット ###
		self.text_tlm = tk.Text(
			frame_tlm,
			width=75,
			height=18,
			bd=0,
			fg='white',
			bg='black',
			font=('Cascadia mono', 10, 'normal')
		)
		self.text_tlm.place(x=0, y=0, height=321)

		# スクロールバー
		self.vscrollbar = ttk.Scrollbar(
			frame_tlm,
			orient='vertical',
			command=self.text_tlm.yview
		)

		# スクロールバーの配置
		self.vscrollbar.place(x=602, y=0, height=320)
		self.text_tlm.configure(yscrollcommand=self.vscrollbar.set)

		### 受信したデジピーター情報をTreeviewに表示する ###
		# スタイル定義
		self.style = ttk.Style()
		self.style.theme_use('default')									# clam / alt / default / classic
		self.style.configure("Treeview.Heading", font=("Cascadia mono", 11, 'bold'),)
		self.style.configure("Treeview", font=("Cascadia mono",10, 'normal'), fieldbackground='black',)

		#Treeviewの定義
		self.tree_dpt = ttk.Treeview(
			frame_dpt,
			columns=(1, 2, 3, 4, 5),
			show='headings',
			style='Treeview'
		)

		# 列の幅、表示位置
		self.tree_dpt.column(1, width=80, anchor='w')
		self.tree_dpt.column(2, width=80, anchor='w')
		self.tree_dpt.column(3, width=80, anchor='w')
		self.tree_dpt.column(4, width=300, anchor='w')
		self.tree_dpt.column(5, width=62, anchor='w')

		# 列の見出し
		self.tree_dpt.heading(1, text='Time')
		self.tree_dpt.heading(2, text='From')
		self.tree_dpt.heading(3, text='To')
		self.tree_dpt.heading(4, text='Message')
		self.tree_dpt.heading(5, text='Delay')
		
		# ウィジェットを配置する
		self.tree_dpt.place(x=0, y=0, height=321)

		# 各アイテムの色指定 (tag=c"fg_white")
		self.tree_dpt.tag_configure("fg_white", background='black', foreground='white')
		self.tree_dpt.tag_configure("fg_orange", background='black', foreground='#f7b265')
		self.tree_dpt.tag_configure("fg_green", background='black', foreground='#adf473')
		
		# スクロールバー
		self.vscrollbar = ttk.Scrollbar(
			frame_dpt,
			orient='vertical',
			command=self.tree_dpt.yview
		)
		# スクロールバーの配置
		self.vscrollbar.place(x=602, y=0, height=320)
		self.tree_dpt.configure(yscrollcommand=self.vscrollbar.set)

		# 転送のカウンターを初期化
		self.loopcounter = 0

		#################################################
		#	各衛星毎のライブラリーモジュール呼び出し
		#################################################

		# 選択された衛星のNoradIDを取得する
		noradid = self.main_page.combo_sat_selected()

		# データフォーマットの衛星別クラス名を作成
		class_name = 'ID' + str(noradid)

		try:
			# クラス名を表す変数を定義
			class_to_call =globals()[class_name]

			# 該当クラスのインスタンスを生成
			instance = class_to_call()
		except KeyError:
			# 接続できなかった時のメッセージ（GUIへ表示）
			lbl_conn = tk.Label(
				text='この衛星に対する処理モジュールが有りません。',
				bg="#e0e0e0",
				font=("Meiryo", 9, "bold")
			)
			lbl_conn.place(x=200, y=455)

		# logファイル名に使用するUTC時刻（プログラム開始時）
		utc = datetime.now(timezone.utc) 
		log_time = utc.strftime('%Y-%m-%dT%H%M%SZ')

		# log フォルダの作成(既存でもOK)
		logdir = SettingsPage.get_setting("LogDir").strip()
		if logdir[-1] != '/' and logdir[-1] != '\\':
			logdir = logdir + '\\'
		logdir = logdir + str(noradid) + '\\'
		os.makedirs(logdir, exist_ok=True)

		# Logger Telemetry の定義
		log_tlm = logging.getLogger('log_tlm')
		log_tlm.setLevel(logging.INFO)
		fmt_tlm = logging.Formatter('%(asctime)s - %(message)s')
		file_tlm = logdir + str(noradid) + '_' + log_time + '_forwarding.log'
		fhdl_tlm = logging.FileHandler(file_tlm)
		fhdl_tlm.setFormatter(fmt_tlm)
		log_tlm.addHandler(fhdl_tlm)

		# Logger digipeaterの定義
		log_dpt = logging.getLogger('log_dpt')
		log_dpt.setLevel(logging.INFO)
		fmt_dpt = logging.Formatter('%(asctime)s - %(message)s')
		file_dpt = logdir + str(noradid) + '_' + log_time + '_digipeater.log'
		fhdl_dpt = logging.FileHandler(file_dpt)
		fhdl_dpt.setFormatter(fmt_dpt)
		log_dpt.addHandler(fhdl_dpt)

		# KISS Raw Dataファイル名の作成（時刻.kss)
		file_kss = utc.strftime(logdir + str(noradid) + '_' + log_time + '.kss')
		file_hex = utc.strftime(logdir + str(noradid) + '_' + log_time + '.hex')

		# 受信したデータを表示するコールバック関数
		def show_data(recvbuf):

			# 時計表示関数を参照してtimestampを取得
			timestamp = chk_time(menu_bar, dt)

			# データフォーマットの衛星別クラスを呼び出し、返り値を取得(port情報先頭に2bytes含む)
			self.string = instance.make_string(recvbuf, file_kss)
			string = str(self.string)

			# 返り値が空データでなければ
			if string != 'None':

				# データ長を [' '02x]を一バイトとして示す
				length = int(len(string) / 2)
				self.text_tlm.insert(INSERT, timestamp + ' [Frame Length : ' + str(length) + ']\n')

				# 表示用に16進スペース区切りの形態に変更
				str_show = ' '.join([f'{string[i]}{string[i+1]}' for i in range(0, len(string), 2)])
				self.text_tlm.insert(INSERT, str(str_show) + '\n')			# 送信データの表示
				scltlm_to_bottom()											# 最下行を表示し続ける

				# 転送設定が yes か no か判断する
				forward_flg = SettingsPage.get_setting("Forwarding").strip()
				if forward_flg == 'yes':

					# NoradIDと転送用データ文字列を持って転送ルーティンへ(返り値はタプル)
					ret = SatNOGS_Client.send_satnogs(string, noradid)

					stat_code = (str(ret).strip("()").split(', {')[0]).strip("'")
					payload = '{' + str(ret).strip('()').split(', {')[1]

					# payload送信ログの保存
					log_tlm.info(payload)
					
					# status_codeが200番台（成功）の時				
					if int(stat_code) < 300:
						self.loopcounter += 1
						res_msg = '[' + str(self.loopcounter) + ']' + 'Status Code: ' + stat_code + ' = Forwarding successful.\n'
#						print(res_msg)										# Debug

						# 転送パケット数表示
						Functions.packet_num(str(self.loopcounter))

					# upload失敗の時	
					else:
						res_msg = "Error : Data couldn't be accepted.\n"
						print("Error : Data couldn't be accepted.")			# Debug

				# 設定が転送なしの場合
				else:
					res_msg = "Not forwarded by setting.\n"

				# それぞれの状況の res_msg を表示する
				self.text_tlm.insert(INSERT, res_msg)
				self.text_tlm.insert(END, '\n')
				scltlm_to_bottom()											# 最下行を表示し続ける

			#
			# 交信データの有る場合の交信リストを作成				
			#
	
			# 時刻データを入れた dataリストを準備する
			data = []
			data.append(timestamp)

			# 外部モジュール内の関数を呼び出し、返り値を取得
			qso_data = instance.make_qso_data(recvbuf)

			# 返り値が空リストで無ければ
			if qso_data is not None:
				data = data + qso_data										# QSOデータの先頭に時刻を追加

				# 本アプリの使用者自身のQSOデータに送受とも色分けする
				callsign = SettingsPage.get_setting("Callsign").strip()
				if data[1] == callsign:
					self.tree_dpt.insert('', tk.END, values=data, tags='fg_orange')
				else:
					if data[2] == callsign:
						self.tree_dpt.insert('', tk.END, values=data, tags='fg_green')
					else:
						self.tree_dpt.insert('', tk.END, values=data, tags='fg_white')

				# 最下行を書いた後スクロールバーを下げる（すべての行が上へスクロールする）（関数定義）
				scldpt_to_bottom()

				# digipeater log の保存
				log_dpt.info(qso_data)
				

		# 受信処理を別スレッドで開始するためのインスタンス
		self.KISS_thread = KISSclient(show_data)
		self.KISS_thread.start()

		# treeviewの最下行追加時その行が見える様スクロールバーを下げる
		def scldpt_to_bottom():
			self.tree_dpt.yview_moveto('1.0')

		def scltlm_to_bottom():
			self.text_tlm.yview_moveto('1.0')

		### 再起動ボタンの配置
		btn_quit=tk.Button(menu_bar, text="Reboot", width=6, command=lambda:restarting())
		btn_quit.place(x=543, y=0)

		def restarting():

			# 終了前処理
			MainPage.pre_ending(self,file_kss, file_hex, file_tlm, file_dpt)

			# スレッドを停止
			self.KISS_thread.stop()

			# 現在のプロセスを再起動するための別プロセスを起動
			subprocess.Popen([sys.executable] + sys.argv)
			
			# 現在のプロセスを終了
			app.destroy()	

		### 終了ボタンの配置
		btn_quit=tk.Button(menu_bar, text="Quit", width=5, command=lambda:ending())
		btn_quit.place(x=595, y=0)

		def ending():
			
			# 終了前処理
			MainPage.pre_ending(self,file_kss, file_hex, file_tlm, file_dpt)

			# スレッドを停止
			self.KISS_thread.stop()

			# プログラムを終了する
			app.destroy()



# イベントループの開始
if __name__ == "__main__":
	app = Main()
	app.mainloop()

