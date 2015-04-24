
# -*- encoding: UTF-8 -*-
import sublime
import sublime_plugin
import os
import sys


MAC_CHECK_FILES   = ['.bash_profile', '.bash_login', '.profile']
LINUX_CHECK_FILES = ['.bashrc']
ZSH_CHECK_FILES   = ['.zshrc']
RE_FORMAT         = r'^export[ \t]+%s=(.+)'


def _isWindows():
	return sys.platform == 'win32'

def _isLinux():
	return sys.platform.startswith('linux')

def _is_mac():
	return sys.platform == 'darwin'

def _is_zsh():
	shellItem = os.environ.get('SHELL')
	if shellItem is not None:
		if len(shellItem) >= 3:
			return shellItem[-3:] == "zsh"
	return False

def _get_unix_file_list():
	file_list = None
	if _is_zsh():
		file_list = ZSH_CHECK_FILES
	elif _isLinux():
		file_list = LINUX_CHECK_FILES
	elif _is_mac():
		file_list = MAC_CHECK_FILES
	return file_list

def _search_unix_variable(var_name, file_name):
	if not os.path.isfile(file_name):
		return None

	import re
	str_re = RE_FORMAT % var_name
	patten = re.compile(str_re)
	ret = None

	for line in open(file_name , encoding='utf-8'):
		str1  = line.lstrip(' \t')
		match = patten.match(str1)
		if match is not None:
			ret = match.group(1)

	return ret

def _find_environment_variable(var):
	ret = os.getenv(var)
	if ret == None:
		if not _isWindows():
			file_list = _get_unix_file_list()

			if file_list is not None:
				home = os.path.expanduser('~')
				for name in file_list:
					path = os.path.join(home, name)
					ret  = _search_unix_variable(var, path)
					if ret is not None:
						break

	return ret


def get_workdir(file_name):
	path, postfix = os.path.splitext(file_name)
	if postfix != ".lua" : return None
	src_dir = path.find("src")
	if src_dir < 0 : return None
	return path[:src_dir]


def launch_simulator(file_name):
	QUICK_V3_ROOT = _find_environment_variable("QUICK_V3_ROOT")
	if QUICK_V3_ROOT == None:
		sublime.message_dialog("please set environment variable 'QUICK_V3_ROOT'")
		return

	WORKDIR = get_workdir(file_name)
	if WORKDIR == None: return

	BIN = ""
	ARG = " -workdir %s -search-path %s/quick" % (WORKDIR, QUICK_V3_ROOT)

	def _windows():
		os.system("taskkill /F /IM simulator.exe")
		return QUICK_V3_ROOT + "/tools/simulator/runtime/win32/simulator.exe"

	def _mac():
		os.system("ps -x|grep simulator|xargs kill -9")
		return QUICK_V3_ROOT + "/tools/simulator/runtime/mac/Simulator.app/Contents/MacOS/Simulator"

	if _isWindows(): 
		BIN = _windows()
	if _is_mac(): 
		BIN = _mac()
	# if _isLinux(): _linux()

	sublime.set_timeout_async(lambda:os.system(BIN + ARG), 0)



class RunQuickSimulatorCommand(sublime_plugin.WindowCommand):

	def run(self):
		view = self.window.active_view()
		file_name = view.file_name()
		launch_simulator(file_name)

