# ライブラリー呼び出し
import tkinter as tk
import tkinter.ttk as ttk
import urllib.request

# ファイル別クラスの呼び出し
from settings import SettingsPage

class Functions(tk.Frame, tk.Tk):

	# ダウンロードしたTLEファイルから satname:noradID リストを作る
	def tle2satname_list():
		
		# 設定ファイルからURLを読み TLE.txt名でダウンロード
		tle_url = SettingsPage.get_setting("TLE Source")
		filename = "TLE.txt"
		urllib.request.urlretrieve(tle_url, filename)	
		
		sat_list = []

		f = open("TLE.txt", 'r')
		num = 0		# ヘッダー部を含む行番号
		row = 0		# データ部のみの行番号
		headnum = 0

		for line in f:

			# 特定の文字列で行数を判断しヘッダー部を省く
			if 'www.amsat.org/tle/dailytle.txt' in line:							
				headnum = num + 2									# 衛星のみのリスト以前の最終行数を取得

			# 衛星: NoradIDリストの作成
			if num > headnum and headnum != 0:						# ヘッダー部をジャンプする
				if row % 3 == 0:									# 3行ごとに読む(衛星名)
					sat = line.strip().split()	
				if row % 3 == 2:									# 1行飛ばして3行目を読む
					sat.append(line.strip().split()[1])				# [1]は3行目の配列中NoradID
					sat_list.append(sat)							# ['satneme', 'noradID']の配列
				row += 1
			num += 1
		
		# sat_listを呼び出し元へ返す
		return sat_list


	# 転送パケット数を表示する
	def packet_num(pnum):
		
		# 転送パケット数表示
		label=tk.Label(text="Forwarded Packets :", bg="#e0e0e0")
		label.place(x=440, y=65)
		label_packets =tk.Label(text=pnum, bg="#e0e0e0", width=6)
		label_packets.place(x=560, y=65)


