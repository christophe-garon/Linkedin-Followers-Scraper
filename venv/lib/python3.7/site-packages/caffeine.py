#!/usr/bin/python

# This below is far more complicated than necessary.  We leave it commented for posterity. 
#
# based on original by Michael Lynn.
# https://github.com/pudquick/pypmset/blob/master/pypmset.py
# from ctypes import c_uint32, cdll, c_int, c_void_p, POINTER, byref
# from CoreFoundation import CFStringCreateWithCString, CFRelease, kCFStringEncodingASCII
# from objc import pyobjc_id
# import atexit
# 
# libIOKit = cdll.LoadLibrary('/System/Library/Frameworks/IOKit.framework/IOKit')
# libIOKit.IOPMAssertionCreateWithName.argtypes = [ c_void_p, c_uint32, c_void_p, POINTER(c_uint32) ]
# libIOKit.IOPMAssertionRelease.argtypes = [ c_uint32 ]
# 
# def _CFSTR(py_string):
#     return CFStringCreateWithCString(None, py_string, kCFStringEncodingASCII)
# 
# def raw_ptr(pyobjc_string):
#     return pyobjc_id(pyobjc_string.nsstring())
# 
# def _IOPMAssertionCreateWithName(assert_name, assert_level, assert_msg):
#     assertID = c_uint32(0)
#     p_assert_name = raw_ptr(_CFSTR(assert_name))
#     p_assert_msg = raw_ptr(_CFSTR(assert_msg))
#     errcode = libIOKit.IOPMAssertionCreateWithName(p_assert_name,
#         assert_level, p_assert_msg, byref(assertID))
#     return (errcode, assertID)
# 
# _IOPMAssertionRelease = libIOKit.IOPMAssertionRelease
# 
# def _assertion_type(display):
# 	if display:
# 		return 'NoDisplaySleepAssertion'
# 	else:
# 		return "NoIdleSleepAssertion"
# 
# _kIOPMAssertionLevelOn = 255
# _assertion = None 
# reason = "python caffeine"
# 
# _assertID = c_uint32(0) 
# 
# 
# def on(display=False):
# 	# Stop idle sleep
# 	global _errcode, _assertID
# 	a = _assertion_type(display)
# 	if a != _assertion:
# 		off()
# 	if _assertID.value ==0:
# 		_errcode, _assertID = _IOPMAssertionCreateWithName(a,
#     _kIOPMAssertionLevelOn, reason)
# 
# 
# 
# def off():
# 	global _errcode
# 	_errcode = _IOPMAssertionRelease(_assertID)
# 	_assertID.value = 0
# 
# def verify():
# 	import subprocess
# 	subprocess.call(['pmset', '-g', 'assertions'])
# 
# on()
# atexit.register(off)


import os
import subprocess
import platform
import atexit

if platform.system()!='Darwin':
	import warnings
	warnings.warn('This package is designed for use on Mac OS X; use on other systems may cause errors and will probably fail.')
	

_pid = os.getpid()
_caf = None

def on(display=False):
	off()
	if display:
		_caf = subprocess.Popen(['caffeinate', '-dis', '-w', str(_pid)])
	else:
		_caf = subprocess.Popen(['caffeinate', '-is', '-w', str(_pid)])

def off():
	global _caf
	if _caf is not None:
		_caf.kill()
		_caf = None

def verify():
	subprocess.call(['pmset', '-g', 'assertions'])

on()
atexit.register(off)


