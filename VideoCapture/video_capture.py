"""
This client application captures and saves video data

Requierment:
	python >3.6
	opencv-python
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
import cv2

# 設定ファイルのデフォルトの名前
FILENAME_CONFIG_DEFAULT = './config/config-sample.txt'

# カメラ画像を表示するウィンドウの名前
CV_WINDOW_NAME = 'video monitor (half size)'

class VideoCapture:
	
	socket_buffer_size = 1024
	socket_message_format = 'utf-8'

	# データを保存するフラグ
	recording = False

	def __init__(self, config_filename):
		
		# 設定ファイルを読み込み
		self.load_config(config_filename)

		# カメラを初期化
		print('Initializing camera...', end='')
		sys.stdout.flush()
		self.cap = cv2.VideoCapture(self.video_device_number)
		print('done!')

		print('Setting video parameter', end='')
		sys.stdout.flush()
		self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
		#self.fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
		print('.', end='')
		sys.stdout.flush()
		self.cap.set(cv2.CAP_PROP_FOURCC, self.fourcc)
		print('.', end='')
		sys.stdout.flush()
		self.cap.set(cv2.CAP_PROP_FPS, self.video_fps)
		print('.', end='')
		sys.stdout.flush()
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
		print('.', end='')
		sys.stdout.flush()
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
		print('done!')

	# 処理開始
	def start(self):

		# 別スレッドでビデオの処理を開始
		thread_video = Thread(target=self.process_video)
		thread_video.setDaemon(True)
		thread_video.start()

		# メインスレッドでサーバへの接続処理と受信処理を開始
		self.process_connection()

	def load_config(self, config_filename):

		# 設定ファイルを読み込む
		config = configparser.ConfigParser()
		config.read(config_filename, 'UTF-8')

		self.server_ip = config.get('Connection', 'server_ip')
		self.server_port = config.getint('Connection', 'server_port')

		self.sensor_id = config.getint('Sensor', 'sensor_id')
		self.sensor_type = config.get('Sensor', 'sensor_type')
		self.sensor_name = config.get('Sensor', 'sensor_name')

		self.video_device_number = config.getint('Sensor', 'device_number')
		self.video_width = config.getint('Sensor', 'device_width')
		self.video_height = config.getint('Sensor', 'device_height')
		self.video_fps = config.getint('Sensor', 'device_fps')

		self.save_dir = config.get('Save', 'save_dir')
		self.save_dir_original = self.save_dir
		self.save_split_by_day = config.getboolean('Save', 'save_split_by_day')
		self.save_data_interval_minute = config.getint('Save', 'save_data_interval_minute')
	
		print('----------config-----------')
		print('server_ip : %s' % self.server_ip)
		print('server_port : %d' % self.server_port)
		print('sensor_id : %d' % self.sensor_id)
		print('sensor_type : %s' % self.sensor_type)
		print('sensor_name : %s' % self.sensor_name)
		print('video_device_number : %d' % self.video_device_number)
		print('video_height : %d' % self.video_height)
		print('video_width : %d' % self.video_width)
		print('video_fps : %d' % self.video_fps)
		print('save_dir : %s' % self.save_dir)
		print('save_split_by_day : %s' % self.save_split_by_day)
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

			try:
				message = self.s.recv(self.socket_buffer_size)
			except ConnectionResetError:
				self.process_connection()
				return
			
			message = message.decode(self.socket_message_format)

			print("[RECEIVE] %s" % message.strip())
			
			# センサスタート
			if message.startswith('RECSTART'):
				
				# ファイルを日付毎のファイルに保存	
				if self.save_split_by_day:
					self.save_dir = self.save_dir_original + '/' + datetime.datetime.now().strftime('%Y%m%d') + '/'
				
				# 保存場所のフォルダがない場合は作成
				if os.path.exists(self.save_dir) == False:
					os.makedirs(self.save_dir)

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
				
				self.filename_temp = self.save_dir + '/' + self.start_time_str + '.mp4'
				self.write()
				self.data_saved = deque([])

				# 待機状態のメッセージを送る
				message = "%d,%s,%s,Ready\n" % (self.sensor_id, self.sensor_type, self.sensor_name)
				print("[SENT] %s" % message.strip())
				self.s.send(message.encode(self.socket_message_format))

	# マイク入力処理を行う
	def process_video(self):
		
		count = 0
		while (self.cap.isOpened()):
			
			try:
				sec = math.floor(time.time())
				today = datetime.datetime.today()
				msec = ('{0:06d}'.format(today.microsecond))[:3]
				
				# データを取得
				ret, frame = self.cap.read()

				if ret == False:
					print('Frame lost!')
					continue
				
				if self.recording == False:
					# 表示の際は縮小する
					frame2 = cv2.resize(frame , (int(self.video_width*0.5), int(self.video_height*0.5)))
					cv2.imshow(CV_WINDOW_NAME, frame2)

				# 音声データを保存する
				# 指定時間ごとに保存
				if self.recording:

					dt_now = datetime.datetime.now()
					minute = dt_now.minute

					if self.last_minute != minute:
						if minute % self.save_data_interval_minute == 0:

							# ファイルに保存
							self.data_saved.append(None)
							self.filename_temp = self.save_dir + '/' + self.start_time_str + '.mp4'
							t = Thread(target=self.write)
							t.setDaemon(True)
							t.start()

							self.start_time_str = dt_now.strftime('%Y%m%d%H%M%S')

						self.last_minute = minute

					self.data_saved.append([dt_now, frame])
				
				cv2.waitKey(1)
				
			except ConnectionResetError:
				self.cap.release()
				self.video_buffer.release()
				cv2.destroyAllWindows()
				print('Stream is terminated.')
				self.s.close()
				print('Socket is closed.')
		
	def write(self):
		
		# ファイルに保存
		if os.path.exists(self.save_dir) == False:
			os.makedirs(self.save_dir)
		
		#MIN_DIFF = 1.0

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

		# if dt_len.total_seconds() < (self.save_data_interval_minute * 60.) - 5.:
		# 	flg_head = True
		# else:
		# 	flg_head = False

		video_buffer = cv2.VideoWriter(
			self.filename_temp,
			self.fourcc,
			self.video_fps,
			(self.video_width, self.video_height)
		)

		# フレーム数を合わせて保存する
		num_frame_recorded = 0
		num_frame_target = self.video_fps * self.save_data_interval_minute * 60
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
			video_buffer.write(nearest_frame)
			num_frame_recorded += 1
		
		video_buffer.release()

		print('# captured frame = %d' % num_frame)
		print('# recorded frame = %d' % num_frame_recorded)
		print('Saved : ' + self.filename_temp)

if __name__ == "__main__":

	parser = argparse.ArgumentParser() 
	parser.add_argument('--config', default=FILENAME_CONFIG_DEFAULT)
	args = parser.parse_args()
	
	print('Config file : %s' % args.config)

	vc = VideoCapture(args.config)
	vc.start()

