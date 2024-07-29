############################################
#	各衛星に合ったレポートフォーマットにする
############################################

#
# GreenCube IO-117 Italy
#
class ID53106():

	#	レシーブデータの16進数表記を整理する
	def make_string(self, recvbuf, file_kss):

		# 101バイトおよび76バイトデータなら出力する
#		if recvbuf[3] == 0x92:
		if		(recvbuf[6] == 0x76 and recvbuf[7] == 0x1a) \
			or	(recvbuf[6] == 0x36 and recvbuf[7] == 0x12):

			''' パケットの種類（SatNOGSが受け取るのは上記2種のみ）
				(recvbuf[6] == 0x76 and recvbuf[7] == 0x1a) \
			or	(recvbuf[6] == 0x76 and recvbuf[7] == 0x19) \
			or	(recvbuf[6] == 0x76 and recvbuf[7] == 0x18) \
			or	(recvbuf[6] == 0x76 and recvbuf[7] == 0x5a) \
			or	(recvbuf[6] == 0x36 and recvbuf[7] == 0x12) \
			or	(recvbuf[6] == 0x36 and recvbuf[7] == 0x11) \
			or	(recvbuf[6] == 0x36 and recvbuf[7] == 0x10) \
			or	(recvbuf[6] == 0x36 and recvbuf[7] == 0x5a):

			Header	ID		Len		Type
			0x8292	0x761a	101		TLM（必要）
			0x8292	0x7619	101		TLM（不要？）
			0x8292	0x7618	101		TLM（不要？）
			0x8292	0x3612	101		TLM（必要）
			0x8292	0x3611	101		TLM (実績なし)
			0x8292	0x3610	101		TLM（不要？）
			0x8292	0x765a	 76		TLM?（不要）
			0x8292	0x365a	 76		TLM?（不要）
			0x8297	0x1d03	 --		Digi
			0x8293	0x41d8	 60		?
			0x8291	------	  6		?
			'''


			# ログファイル(kss)作成(受信したままの Raw Data)
			with open(file_kss, 'ab') as file:
				file.write(recvbuf)

			# recvbufの先頭と末尾のデリミタ0xc0及び2バイト目のコマンドデータ 0x00を省く
			transaction = ''.join(['{:02x}'.format(byte) for byte in recvbuf[2:-1]])
			
			# KISS逆変換(dbdc => c0 / dbdd => db)
			string = (transaction.replace("dbdc", "c0")).replace('dbdd', 'db')
			
			# 返り値
			return string

	#	QSOデータが有る場合表示用リストにする
	def make_qso_data(self, recvbuf):

		# 4byte目の値が0x97の場合デジピートされたユーザーデータ
		if recvbuf[3] == 0x97:

			# dataをリストとして定義
			data = []

			# 受信データをそれぞれ項目別に分ける
			items = str(recvbuf[8:]).split(',')
#			print(len(items))											# Debug
			callsign_tmp = items[0].strip('b\'')
			callsign_tmp2 = callsign_tmp
			callsings = callsign_tmp2.split('>')
			mycallsign = callsings[0]									# 自分のコールサイン
			urcallsign = callsings[1]									# 相手のコールサイン

			# 分割したデータが欠けていないかチェック
			if len(items) > 2:
				items2 = items[2][1:-5]
				index_spc = items2.find(' ', 0)
				store = items2[6:index_spc]								# 返信ディレイタイム
				mymsg = items2[index_spc+1:]
				index_n = mymsg.find("\\n", 0)							# エスケープが必要
				if index_n >= 0:
					mymsg = mymsg[0:-2]									# メッセージ
				data = [mycallsign, urcallsign, mymsg, 'Rx:' + store]	# main側で timestamp をヘッドに加える
			else:
				data = [mycallsign, urcallsign]

			return data

#
# LEDSAT Italy
#
class ID49069():

	#	レシーブデータの16進数表記を整理する
	def make_string(self, recvbuf, file_kss):

		# 101バイトおよび76バイトデータなら出力する
		if recvbuf[3] == 0x92:
#		if		(recvbuf[6] == 0x76 and recvbuf[7] == 0x1a) \
#			or	(recvbuf[6] == 0x76 and recvbuf[7] == 0x19) \
#			or	(recvbuf[6] == 0x76 and recvbuf[7] == 0x18) \
#			or	(recvbuf[6] == 0x36 and recvbuf[7] == 0x12) \
#			or	(recvbuf[6] == 0x36 and recvbuf[7] == 0x11) \
#			or	(recvbuf[6] == 0x36 and recvbuf[7] == 0x10) \
#			or	(recvbuf[6] == 0x75 and recvbuf[7] == 0x5a) \
#			or	(recvbuf[6] == 0x36 and recvbuf[7] == 0x5a):

			'''
			Header	ID		Len		Type
			0x8292	0x761a	101		TLM
			0x8292	0x7619	101		TLM
			0x8292	0x7618	101		TLM
			0x8292	0x3612	101		TLM
			0x8292	0x3611	101		TLM (実績なし)
			0x8292	0x3610	101		TLM
			0x8292	0x765a	 76		TLM?
			0x8292	0x365a	 76		TLM?
			0x8297	0x1d03	 --		Digi
			0x8293	0x41d8	 60		?
			0x8291	------	  6		?
			'''


			# ログファイル(kss)作成(受信したままの Raw Data)
			with open(file_kss, 'ab') as file:
				file.write(recvbuf)

			# recvbufの先頭と末尾のデリミタ0xc0及び2バイト目のコマンドデータ 0x00を省く
			transaction = ''.join(['{:02x}'.format(byte) for byte in recvbuf[2:-1]])
			
			# KISS逆変換(dbdc => c0 / dbdd => db)
			string = (transaction.replace("dbdc", "c0")).replace('dbdd', 'db')
			
			# 返り値
			return string

	#	QSOデータが有る場合表示用リストにする
	def make_qso_data(self, recvbuf):

		# 4byte目の値が0x97の場合デジピートされたユーザーデータ
		if recvbuf[3] == 0x97:

			# dataをリストとして定義
			data = []

			# 受信データをそれぞれ項目別に分ける
			items = str(recvbuf[8:]).split(',')
#			print(len(items))											# Debug
			callsign_tmp = items[0].strip('b\'')
			callsign_tmp2 = callsign_tmp
			callsings = callsign_tmp2.split('>')
			mycallsign = callsings[0]									# 自分のコールサイン
			urcallsign = callsings[1]									# 相手のコールサイン

			# 分割したデータが欠けていないかチェック
			if len(items) > 2:
				items2 = items[2][1:-5]
				index_spc = items2.find(' ', 0)
				store = items2[6:index_spc]								# 返信ディレイタイム
				mymsg = items2[index_spc+1:]
				index_n = mymsg.find("\\n", 0)							# エスケープが必要
				if index_n >= 0:
					mymsg = mymsg[0:-2]									# メッセージ
				data = [mycallsign, urcallsign, mymsg, 'Rx:' + store]	# main側で timestamp をヘッドに加える
			else:
				data = [mycallsign, urcallsign]

			return data


