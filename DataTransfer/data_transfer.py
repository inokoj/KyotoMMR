"""
This class is for data transfer from client to server

Requierment:
	python >3.6
	pyaudio (https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
"""

import sys, os


import argparse
import configparser

import time
import datetime

import shutil

# 設定ファイルのデフォルトの名前
FILENAME_CONFIG_DEFAULT = './config/config-sample.txt'

class DataTransfer:
	"""
	データを転送するクラス
	"""

	def __init__(self):
		
		self.load_config()
	
	def load_config(self, config_filename):
		"""
		設定ファイルを読み込む
		"""

		config = configparser.ConfigParser()
		config.read(config_filename, 'UTF-8')

		self.copy_to = config.get('Copy', 'to')
		self.copy_from = config.get('Copy', 'from')
		self.copy_coverwrite = config.getboolean('Copy', 'overwrite')
		
		self.target_extention_raw = config.get('Copy', 'copy_target_extention')
		if self.target_extention_raw.strip() == 'all':
			self.target_extention = None
		else:
			self.target_extention = [s.strip() in for s in self.target_extention.split(',')]
		
		self.copy_daytype = config.get('Copy', 'copy_daytype')
		if self.copy_daytype.strip() == 'all':
			self.copy_allday_flg = True
			self.target_date = None
		elif self.copy_daytype.strip() == 'today':
			self.copy_allday_flg = False
			self.target_date = datetime.datetime.now().strftime('%Y%m%d')
		else:
			self.copy_allday_flg = False
			self.target_date = self.copy_daytype
	
		print('----------config-----------')
		print('copy_to : %s' % self.copy_to)
		print('copy_from : %s' % self.copy_from)
		print('copy_overwrite : %s' % self.copy_coverwrite)
		print('copy_target_extention : %s' % self.target_extention_raw)
		print('copy_daytype : %s' % self.copy_daytype)
		print('---------------------------')

		TARGET_EXT = ["txt", "avi", "wav"]
	
	def create_directory(self, dirName):
		"""
		指定されたディレクトリがなければ作成する
		"""
		if not os.path.exists(dirName):
			os.makedirs(dirName)

	def check_and_copy(self, src, dst):
		"""
		指定されたディレクトリのデータを再帰的に探索してコピーする
		"""

		# ファイルの場合
		if os.path.isfile(src):

			# 拡張子の確認
			for ext in self.target_extention:
				if src.lower().endswith(ext.lower()):
					check_ext = True

			if check_ext == False:
				return

			# 日付の確認
			if self.target_date is not None:
				if self.target_date not in src:
					return

			# ファイルの存在確認
			if self.overwrite == False and os.path.exists(dst) == True:
				return
			
			print("copying  %s -> %s" % (src, dst))
			shutil.copy2(src, dst)

		# フォルダの場合
		elif os.path.isdir(src):

			create_directory(dst)
			
			for child in os.listdir(src):

				if child.startswith('$') or child.startswith('.'):
					continue
				
				if child.strip() == 'System Volume Information':
					continue

				new_src = src + "/" + child
				new_dst = dst + "/" + child
				self.check_and_copy(new_src, new_dst)

	def start(self):
		"""
		コピーを実行
		"""

		self.create_directory(self.copy_to)
		self.check_and_copy(self.copy_from, self.copy_to)

if __name__ == "__main__":

	parser = argparse.ArgumentParser() 
	parser.add_argument('--config', default=FILENAME_CONFIG_DEFAULT)
	args = parser.parse_args()
	
	print('Config file : %s' % args.config)

	dt = DataTransfer(args.config)
	dt.start()

