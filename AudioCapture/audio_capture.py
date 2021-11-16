"""
This client application captures and saves audio data

Requierment:
	python >3.6
	pyaudio (https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
"""

import sys, os
import math
import numpy as np

import argparse
import configparser

import time
import datetime

import socket
from threading import Thread
from collections import deque

import wave
import pyaudio as pa

# 設定ファイルのデフォルトの名前
FILENAME_CONFIG_DEFAULT = './config/config-sample.txt'

class AudioCapture:
	
	audio_chunk = 160 # 1024 / 44100 ~ 25 msec
	socket_buffer_size = 1024
	socket_message_format = 'utf-8'

	# データを保存するフラグ
	recording = False

	def __init__(self, config_filename):
		
		# 設定ファイルを読み込み
		self.load_config(config_filename)

		# 保存場所のフォルダがない場合は作成
		if os.path.exists(self.save_dir) == False:
			os.makedirs(self.save_dir)

		# PyAudioを初期化
		self.p = pa.PyAudio()
		self.list_audio_devices()

	# 処理開始
	def start(self):

		# 別スレッドでオーディオの処理を開始
		thread_audio = Thread(target=self.process_audio)
		thread_audio.setDaemon(True)
		thread_audio.start()

		# メインスレッドでサーバへの接続処理と受信処理を開始
		self.process_connection()
	
	# 音声デバイスの情報を表示
	def list_audio_devices(self):

		print('----------audio device info-----------')

		for x in range(0, self.p.get_device_count()):
			d = self.p.get_device_info_by_index(x)
			if d['maxInputChannels'] > 0:
				print(u'%d : %s (ch.=%d)' % (d['index'], d['name'], d['maxInputChannels']))
		
		print('--------------------------------------')

		# Defaultの番号を使用
		if self.audio_device_number == -1:
			self.audio_device_number = self.p.get_default_input_device_info()['index']
			print('Use default device -> %d' % self.audio_device_number)

	def load_config(self, config_filename):

		# 設定ファイルを読み込む
		config = configparser.ConfigParser()
		config.read(config_filename)

		self.server_ip = config.get('Connection', 'server_ip')
		self.server_port = config.getint('Connection', 'server_port')

		self.sensor_id = config.getint('Sensor', 'sensor_id')
		self.sensor_type = config.get('Sensor', 'sensor_type')
		self.sensor_name = config.get('Sensor', 'sensor_name')

		self.audio_device_number = config.getint('Sensor', 'device_number')

		device_bps = config.getint('Sensor', 'device_bps')
		if device_bps == 16:
			self.audio_format = pa.paInt16
			self.audio_format_str = 'int16'
			self.ref_max = np.power(2, 15) - 1
		elif device_bps == 24:
			self.audio_format = pa.paInt24
			self.audio_format_str = 'int24'
			self.ref_max = np.power(2, 23) - 1
		self.audio_channel = config.getint('Sensor', 'device_channel')
		self.audio_rate = config.getint('Sensor', 'device_sampling_rate')

		self.save_dir = config.get('Save', 'save_dir')
		self.save_data_interval_minute = config.getint('Save', 'save_data_interval_minute')

		# 保存場所のフォルダがない場合は作成
		if os.path.exists(self.save_dir) == False:
			os.makedirs(self.save_dir)
	
		print('----------config-----------')
		print('server_ip : %s' % self.server_ip)
		print('server_port : %d' % self.server_port)
		print('sensor_id : %d' % self.sensor_id)
		print('sensor_type : %s' % self.sensor_type)
		print('sensor_name : %s' % self.sensor_name)
		print('audio_device_number (-1 -> default): %d' % self.audio_device_number)
		print('audio_format : %s' % self.audio_format_str)
		print('audio_channel : %d' % self.audio_channel)
		print('audio_rate : %d' % self.audio_rate)
		print('save_dir : %s' % self.save_dir)
		print('save_data_interval_minute : %d' % self.save_data_interval_minute)
		print('---------------------------')
	
	# サーバに接続
	def process_connection(self):

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		while True:
			try:
				self.s.connect((self.server_ip, self.server_port))
				break
			except ConnectionRefusedError:
				print('Connecting to %s (port %d)' % (self.server_ip, self.server_port))
				continue

		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print('[SERVER CONNECTED]')

		# 最初の接続メッセージを送る
		message = "%d,%s,%s,Ready\n" % (self.sensor_id, self.sensor_type, self.sensor_name)
		print("[SENT] %s" % message.strip())
		self.s.send(message.encode(self.socket_message_format))

		# 受信処理をメインスレッドとして続ける
		while True:
			message = self.s.recv(self.socket_buffer_size)
			message = message.decode(self.socket_message_format)

			print("[RECEIVE] %s" % message.strip())
			
			# センサスタート
			if message.startswith('RECSTART'):
				
				# ファイル保存に使用する名前
				dt_now = datetime.datetime.now()
				self.start_time_str = dt_now.strftime('%Y%m%d%H%M%S')
				self.last_minute = dt_now.minute
				self.data_saved = deque([])
				
				self.recording = True

				temp = dt_now.strftime('%Y-%m-%d %H:%M:%S')
				print('RECSTART : %s' % temp)

				# 収録開始の接続メッセージを送る
				message = "%d,%s,%s,Recording\n" % (self.sensor_id, self.sensor_type, self.sensor_name)
				print("[SENT] %s" % message.strip())
				self.s.send(message.encode(self.socket_message_format))
			
			# センサ停止
			elif message.startswith('RECSTOP'):
				
				dt_now = datetime.datetime.now()
				temp = dt_now.strftime('%Y-%m-%d %H:%M:%S')
				print('RECSTOP : %s' % temp)

				self.recording = False
				self.data_saved.append(None)

				self.filename_temp = self.save_dir + '/' + self.start_time_str + '.wav'
				self.write()
				self.data_saved = deque([])

				# 待機状態のメッセージを送る
				message = "%d,%s,%s,Ready\n" % (self.sensor_id, self.sensor_type, self.sensor_name)
				print("[SENT] %s" % message.strip())
				self.s.send(message.encode(self.socket_message_format))

	# マイク入力処理を行う
	def process_audio(self):
		
		stream = self.p.open(
			input_device_index= self.audio_device_number,
			format = self.audio_format,
			channels = self.audio_channel,
			rate = self.audio_rate,
			input = True,
			output = False,
			frames_per_buffer = self.audio_chunk
		)
		
		stream.start_stream()
		
		# # ファイル保存に使用する名前
		# dt_now = datetime.datetime.now()
		# self.start_time_str = dt_now.strftime('%Y%m%d%H%M%S')
		# last_minute = dt_now.minute
		# data_saved = []

		# 音量はセンサー収録時以外で5回/秒表示
		count_display = 0
		display_interval = (int(self.audio_rate / self.audio_chunk) / 5)
		display_max = 0.

		while stream.is_active():
			try:
				sec = math.floor(time.time())
				today = datetime.datetime.today()
				msec = ('{0:06d}'.format(today.microsecond))[:3]
				
				# データを取得
				dat_raw = stream.read(self.audio_chunk)
				dat = np.frombuffer(dat_raw, np.int16)
				
				if self.recording == False:
					
					# 最大値を計算して割合で表示
					dat_max = np.max(dat)
					rate = 100. * (float(dat_max) / float(self.ref_max))
					display_max = max(display_max, rate)

					if count_display % display_interval == 0:

						message = "Audio power monitor [%%] = %6.2f" % rate
						num_bar = int(rate/4)
						message += "  [" + ("#" * num_bar) + (" " * (25-num_bar)) + "]"
						sys.stdout.write('\r' + message)
						sys.stdout.flush()

						display_max = 0.
					
					count_display += 1

				# 音声データを保存する
				# 指定時間ごとに保存
				if self.recording:

					dt_now = datetime.datetime.now()
					minute = dt_now.minute

					if self.last_minute != minute:
						if minute % self.save_data_interval_minute == 0:
							
							# ファイルに保存
							self.data_saved.append(None)
							self.filename_temp = self.save_dir + '/' + self.start_time_str + '.wav'
							t = Thread(target=self.write)
							t.setDaemon(True)
							t.start()

							# filename = self.save_dir + '/' + self.start_time_str + '.wav'
							# self.write(filename, self.data_saved)
							# self.data_saved = []

							self.start_time_str = dt_now.strftime('%Y%m%d%H%M%S')

						self.last_minute = minute
					
					self.data_saved.append([dt_now, dat])
			
			except ConnectionResetError:
				stream.stop_stream()
				stream.close()
				self.p.terminate()
				print('Stream is terminated.')
				self.s.close()
				print('Socket is closed.')
				
		# 		# データが残っていればファイルに保存
		# 		if len(data_saved) > 0:
		# 			filename = self.save_dir + start_time_str + '.wav'
		# 			self.write(filename, data_saved)
		# 			data_saved = []
		
		# # データが残っていればファイルに保存
		# if len(data_saved) > 0:
		# 	filename = self.save_dir + start_time_str + '.wav'
		# 	self.write(filename, data_saved)
		# 	data_saved = []
		
	def write(self):
			
		num_frame = 0
		data = []
		while True:
			frame = self.data_saved.popleft()
			if frame is None:
				break
			data.append(frame)
			num_frame += 1
		
		if len(data) == 0:
			return
		
		# 先頭のフレームの時間
		dt_start = data[0][0]
		dt_end = data[-1][0]
		dt_len = dt_end - dt_start

		# フレーム数を合わせて保存する
		num_frame_recorded = 0
		num_frame_target = int((self.audio_rate * self.save_data_interval_minute * 60) / self.audio_chunk)
		data_saved_new = []
		for t in np.linspace(0, self.save_data_interval_minute * 60, num_frame_target):
			
			nearest_frame = None
			min_diff = 1E+6

			# 最初のファイル対策
			if t > dt_len.total_seconds() + 1.0:
				continue

			for d in data:
				time = d[0] - dt_start
				diff = abs(time.total_seconds() - t)
				
				if min_diff > diff:
					min_diff = diff
					nearest_frame = d[1]
			
			#if min_diff < MIN_DIFF and nearest_frame is not None:
			data_saved_new.append(nearest_frame)
			num_frame_recorded += 1
		
		# ファイルに保存
		if os.path.exists(self.save_dir) == False:
			os.makedirs(self.save_dir)
		
		ww = wave.open(self.filename_temp, 'wb')
		ww.setnchannels(self.audio_channel)
		ww.setsampwidth(self.p.get_sample_size(self.audio_format))
		ww.setframerate(self.audio_rate)
		ww.writeframes(b''.join(data_saved_new))
		ww.close()

		print('# captured frame = %d' % num_frame)
		print('# recorded frame = %d' % num_frame_recorded)
		print('Saved : ' + self.filename_temp)

if __name__ == "__main__":

	parser = argparse.ArgumentParser() 
	parser.add_argument('--config', default=FILENAME_CONFIG_DEFAULT)
	args = parser.parse_args()
	
	print('Config file : %s' % args.config)

	ac = AudioCapture(args.config)
	ac.start()

