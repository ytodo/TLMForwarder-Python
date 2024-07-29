import tkinter as tk
import tkinter.ttk as ttk
import subprocess
import os
import logging

# 別ファイルにあるクラスの参照
from settings import SettingsPage
from telemetry import TelemetryPage
from functions import Functions
from digipeater import DigiPeaterPage

class MainPage(tk.Frame):

	def __init__(self, master, frame_tlm, frame_dpt, frame_cvr, menu_bar, upperpane):
		tk.Frame.__init__(self, master)
	#
	# メニューボタンの表示
	#
		### menuボタンの表示
		# DIGIPEATER
		btn_dpt = tk.Button(
			menu_bar,
		    text='DIGIPEATER', width=11, height=1,
			command=lambda:DigiPeaterPage(master, frame_dpt, frame_cvr)
		)
		btn_dpt.place(x=0, y=0)

		# TELEMETRY
		btn_tlm = tk.Button(
			menu_bar,
			text='TELEMETRY', width=11, height=1,
			command=lambda:TelemetryPage(master, frame_tlm, frame_cvr)
		)
		btn_tlm.place(x=87, y=0)

		# SETTINGS
		btn_set = tk.Button(
			menu_bar,
		    text='SETTINGS', width=11, height=1,
			command=lambda:SettingsPage(master)
		)
		btn_set.place(x=174, y=0)

		### Local 又は UTC かラジオボタンで選択
		setting = SettingsPage.get_setting("Screen Time").strip()
		menu_bar.var_tm = tk.IntVar()
		if setting == 'UTC':
			menu_bar.var_tm.set(0)
		if setting == 'local':
			menu_bar.var_tm.set(1)

		# UTC
		rb_utc = tk.Radiobutton(
			menu_bar,
			value=0,
			variable=menu_bar.var_tm,									# UTC, localで同名とするとグループになる
			text='UTC',
			command=lambda:MainPage.radio_time_selected(menu_bar, menu_bar.var_tm)
		)
		rb_utc.place(x=270, y=0)

		# Local
		rb_lcl = tk.Radiobutton(
			menu_bar,
			value=1,
			variable=menu_bar.var_tm,									# 従って、一方を選択すると他方が非選択となる
			text='Local',
			command=lambda:MainPage.radio_time_selected(menu_bar, menu_bar.var_tm)
		)
		rb_lcl.place(x=320, y=0)

	#
	# 衛星名から NoradID を特定するためのドロップボックス
	#
		# 初期値の取得
		satname = SettingsPage.get_setting("LastUsed").strip()
		sat_list = Functions.tle2satname_list()							# TLE.txtを['satneme', 'noradID']の配列にする
		drop_list = []													# tle2satnmae_listの返り値を編集（衛星名のみにする）
		sat_list_sorted = sorted(sat_list)								# ABC順にソート
		for line in sat_list_sorted:
			drop_list.append(line[0])

		# ドロップダウンメニューで衛星を指定する
		global combo_sat
		label=tk.Label(upperpane, text="Satellite Name :", bg='#e0e0e0')
		label.place(x=30, y=14)
		upperpane.var_sat = tk.StringVar(value=satname)										# 選択した衛星名を保持する変数

		# コンボボックスの表示
		combo_sat=ttk.Combobox(upperpane, width=20, height=25, values=drop_list, textvariable=upperpane.var_sat)
		combo_sat.bind("<<ComboboxSelected>>", MainPage.combo_sat_selected)
		combo_sat.place(x=117, y=14)

	#
	# レポートの送り先データベースを選択して設定ファイルに登録
	#
		global combo_db
		label=tk.Label(upperpane, text="Report to :", bg='#e0e0e0')
		label.place(x=30, y=39)

		# コンボボックス初期値の取得
		setting = SettingsPage.get_setting("Report to").strip()			# 設定ファイルから初期値を読み込む
		db_list = ['https://db.satnogs.org', 'https://db-dev.satnogs.org']
		upperpane.var_db = tk.StringVar(value=setting)					# 選択した衛星名を保持する変数(初期値を持つ)

		# コンボボックスの表示
		combo_db=ttk.Combobox(upperpane, width=39, values=db_list, textvariable=upperpane.var_db)
		combo_db.set(setting)											# 上記varと二重にセット他の関数の上書き防止
		combo_db.bind("<<ComboboxSelected>>", MainPage.combo_db_selected)
		combo_db.place(x=117, y=39)

	#
	# 転送をするかしないかのチェックボックス
	#
		# 初期値の取得
		setting = SettingsPage.get_setting("Forwarding").strip()
		upperpane.var_fw = tk.BooleanVar(value=True)
		if setting == 'yes':
			upperpane.var_fw.set(True)									# 設定ファイルが yes ならチェック
		else:
			upperpane.var_fw.set(False)									# no 又は yes 以外はチェックなし

		# チェックボックスの作成
		chk = tk.Checkbutton(upperpane,
			text="Forward to SatNOGS",
			variable=upperpane.var_fw,
			bg="#e0e0e0",
			command=lambda:MainPage.chk_forward_selected(upperpane, upperpane.var_fw)
		)
		chk.place(x=420, y=12)

		# 初期値表示
		Functions.packet_num(str(0))

	# 設定ファイルの表示時間のロケールを選択したものに変更
	def radio_time_selected(menu_bar, var_tm):
		rb_tm = var_tm.get()											# ラジオボタンのどちらが押されているか取得
		target = "Screen Time"

		# value 0/1 を設定文字列に変換
		if rb_tm == 0:
			replace = "UTC"
		if rb_tm == 1:
			replace = "local"

		# 設定ファイルの(key, 変更文字列)セットを作る
		replace_set = (target, replace)
		SettingsPage.replace_setting(replace_set)
		
	# 指定した衛星のNoradIDを表示する
	def combo_sat_selected(event):
		global combo_sat
		sat_list = Functions.tle2satname_list()

		# 選択した衛星をキーワードにリストからNoradIDを抽出
		noradid = ','.join([line[1] for line in sat_list if combo_sat.get() in line])

		# ラベルとNoradIDを表示
		label=tk.Label(text="NoradID :", bg='#e0e0e0')
		label.place(x=280, y=40)
		lbl_norad=tk.Label(text=noradid, bg='#e0e0e0')
		lbl_norad.place(x=340, y=40)

		# 前回選択した衛星としてsettingsに保存
		target = "LastUsed"
		replace = combo_sat.get()
		replace_set = (target, replace)
		SettingsPage.replace_setting(replace_set)

		# logファイル等のEnding処理とアプリの再帰処理

		return noradid

	# 選択した転送先を設定ファイルに保存する
	def combo_db_selected(event):
		global combo_db
		target = "Report to"
		replace = combo_db.get()
		replace_set = (target, replace)
		SettingsPage.replace_setting(replace_set)				# 選択値で設定ファイルを書き換え

	# 転送yes/noの変更を設定ファイルに反映させる
	def chk_forward_selected(upperpane, var_fw):
		chk_fw = var_fw.get()
		target = "Forwarding"

		# 有効無効をyes/noに変換
		if chk_fw == True:
			replace = "yes"
		else:
			replace = "no"

		# 設定ファイルの(key,変更文字列)セットを作る
		replace_set = (target, replace)
		SettingsPage.replace_setting(replace_set)

	# 終了前のクリア処理
	def pre_ending(self, file_kss, file_hex, file_tlm, file_dpt):

		# KISS ファイルが存在するか
		if os.path.exists(file_kss):

			# KISS ファイルの可視化
			command = ['certutil', '-encodehex', file_kss, file_hex, '11']
			subprocess.Popen(command)
			
		# LOGファイルすべてのクローズ
		logging.shutdown()

		# LOGファイルでサイズがゼロならば削除			
		if os.path.exists(file_tlm) and os.path.getsize(file_tlm) == 0:
			os.remove(file_tlm)											# forwarding.log
		if os.path.exists(file_dpt) and os.path.getsize(file_dpt) == 0:
			os.remove(file_dpt)											# digipeater.log

		# 現在のアプリの位置を取得
		x = self.winfo_x()
		y = self.winfo_y()

		# x, yの値をTLMForwarder.iniへ保存
		target = "Window_x"
		replace_set = (target, str(x))
		SettingsPage.replace_setting(replace_set)
		target = "Window_y"
		replace_set = (target, str(y))
		SettingsPage.replace_setting(replace_set)

