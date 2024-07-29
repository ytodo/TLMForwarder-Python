# ライブラリー呼び出し
import tkinter as tk
import requests
import threading
from tkinter import *
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SHUT_RDWR

# ファイル別クラスの参照
from settings import SettingsPage
from functions import Functions

# 設定ファイルよりアドレスとポートを取得する
IPADDR = SettingsPage.get_setting("KISS Address").strip()
PORT = int(SettingsPage.get_setting("KISS Port").strip())
BUFSIZE = 2048

#########################################
# KISS Portより受信データを取得（別スレッド）
#########################################
class KISSclient():

	def __init__(self, callback):
		super().__init__()

		# データをメインスレッドに転送
		self.callback = callback

		# データ受信専用スレッドの定義
		self.thread = threading.Thread(target=self.run)
		self.stop_event = threading.Event()

	# サブスレッドの開始
	def start(self):							# メインスレッドから開始操作
		self.thread.start()

	# サブスレッドの停止フラグ発生
	def stop(self):								# メインスレッドから停止操作
		self.stop_event.set()

	# スレッド開始とともに自動的に実行される
	def run(self):

		# ソケットを生成
		sock = socket(AF_INET, SOCK_STREAM)

		# 接続時、モデムが起動していない時のエラー処理を加える
		try:
			sock.connect((IPADDR, PORT))

			# 接続完了した時の表示
			lbl_conn = tk.Label(
				text="Connected to KISS Port",
				fg="green",
				bg="#e0e0e0",
				font=("Courie", 9	, 'bold')
			)
			lbl_conn.place(x=10, y=456)

		except:
			# 接続できなかった時のメッセージ（GUIへ表示）
			lbl_conn = tk.Label(
				text='先にSoundmodemを起動してください',
				bg="#e0e0e0",
				font=("Meiryo", 9, "bold")
			)
			lbl_conn.place(x=10, y=455)

			# GUIを起動させずにアラームを発する場合
			print('\n先にSoundmodemを起動してください\n')						# Debug

		sock.settimeout(1)

		# データ受信
		while True:

			# stop_eventがセットされたら切断する
			if self.stop_event.is_set():
				break
			
			try:

			# パケットを受信			
				recvbuf = sock.recv(BUFSIZE)

			except OSError:
				continue


			# 受信データがなければ切断
			if not recvbuf:
				break
			
			# 最後の行が空行であれば除外
			if recvbuf[-1] == '':
				recvbuf = recvbuf[:-1]

			# コールバック関数を呼び出し、受信したデータを渡す
			self.callback(recvbuf)


######################################
# SatNOGSへの転送プロトコル
######################################
class SatNOGS_Client():

	def send_satnogs(string, noradid):

		#
		# ペイロードの値を設定ファイルから取得
		#
		callsign = SettingsPage.get_setting("Callsign").strip()				# コールサイン
		dt = datetime.utcnow()
		timeStamp = dt.	strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'			# 転送時刻
		longitude = SettingsPage.get_setting("Longitude").strip()			# 軽度
		latitude = SettingsPage.get_setting("Latitude").strip()				# 緯度

		# 接続する転送先のデータベースURL
		url = SettingsPage.get_setting("Report to").strip()
		database = (url + '/api/telemetry/?')

		# UDPソケットを作成します
		sock = socket(AF_INET, SOCK_DGRAM)

		payload = {
			'noradID': int(noradid),
			'source': callsign,
			'timestamp': timeStamp,
			'frame': string,
			'locator': 'longLat',
			'longitude': longitude,
			'latitude': latitude
		}

		# 取得データをデータベースへ送信		
		try:
#			print(payload)													# Debug

	    	# テレメトリ情報をサーバーに転送します
			res = requests.post(database, data = payload, timeout = int(1))
			res_status = res.raise_for_status()								# 200番台以外の時、例外を起こし停止

		except Exception as exc:
			print('res.text :' + res.text)
			print('Error{}').format(exc)

		finally:
			# 例外処理でなかったら(stat_code == 200番台)
			if res_status == None: 				
				stat_code = str(res.status_code)

			# ソケットを閉じる
			sock.close()	

		return stat_code, payload
