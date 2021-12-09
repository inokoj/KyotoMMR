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

import subprocess
import signal

# 設定ファイルのデフォルトの名前
FILENAME_CONFIG_DEFAULT = './config/config-sample.txt'

class ExeLauncher:
	
	audio_chunk = 1000 # 1000 / 16000 = 62.5 msec
	socket_buffer_size = 1024
	socket_message_format = 'utf-8'

	# データを保存するフラグ
	recording = False

	def __init__(self, config_filename):
		
		# 設定ファイルを読み込み
		self.load_config(config_filename)

	# 処理開始
	def start(self):

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
		self.cmd = config.get('Sensor', 'command')
	
		print('----------config-----------')
		print('server_ip : %s' % self.server_ip)
		print('server_port : %d' % self.server_port)
		print('sensor_id : %d' % self.sensor_id)
		print('sensor_type : %s' % self.sensor_type)
		print('sensor_name : %s' % self.sensor_name)
		print('sensor_command : %s' % self.cmd)
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

		try:
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
				if message.startswith('RECSTART') and self.recording == False:
					
					dt_now = datetime.datetime.now()
					
					self.process = subprocess.Popen(self.cmd, shell=True)
					self.recording = True
					print("Started process : %d" % self.process.pid)

					temp = dt_now.strftime('%Y-%m-%d %H:%M:%S')
					print('RECSTART : %s' % temp)

					# 収録開始の接続メッセージを送る
					message = "%d,%s,%s,Recording\n" % (self.sensor_id, self.sensor_type, self.sensor_name)
					print("[SENT] %s" % message.strip())
					self.s.send(message.encode(self.socket_message_format))
				
				# センサ停止
				elif message.startswith('RECSTOP') and self.recording:
					
					dt_now = datetime.datetime.now()
					temp = dt_now.strftime('%Y-%m-%d %H:%M:%S')
					print('RECSTOP : %s' % temp)

					#self.process.terminate()
					
					# For Windows
					killcmd = "taskkill /F /PID {pid} /T".format(pid=self.process.pid)
					subprocess.run(killcmd,shell=True)
					self.recording = False

					# 待機状態のメッセージを送る
					message = "%d,%s,%s,Ready\n" % (self.sensor_id, self.sensor_type, self.sensor_name)
					print("[SENT] %s" % message.strip())
					self.s.send(message.encode(self.socket_message_format))
		
		except ConnectionResetError:
			self.s.close()
			self.process_connection()

if __name__ == "__main__":

	parser = argparse.ArgumentParser() 
	parser.add_argument('--config', default=FILENAME_CONFIG_DEFAULT)
	args = parser.parse_args()
	
	print('Config file : %s' % args.config)

	el = ExeLauncher(args.config)
	el.start()

