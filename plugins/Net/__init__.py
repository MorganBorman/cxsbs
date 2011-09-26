import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def reload(self):
		pass
		
	def unload(self):
		pass
		
from socket import inet_ntop, inet_pton, ntohl, htonl, AF_INET
from struct import pack, unpack

# Based heavily on code from here:
# http://code.activestate.com/recipes/66517-ip-address-conversion-functions-with-the-builtin-s/
# But with a few fixes:
# 1) does network byte ordering conversions
# 2) makeMask works for case of 0


def ipLongToString(num):
	return numToDottedQuad(num)

def ipStringToLong(ip):
	return dottedQuadToNum(ip)

def dottedQuadToNum(ip):
	"convert decimal dotted quad string to long integer"
	return ntohl(unpack('!L',inet_pton(AF_INET,ip))[0])

def numToDottedQuad(n):
	"convert long int to dotted quad string"
	return inet_ntop(AF_INET, pack('!L',htonl(n)))

def makeMask(n):
	"return a mask of n bits as a long integer"
	return (1L<<n)-1

def ipToNetAndHost(ip, maskbits):
	"returns tuple (network, host) dotted-quad addresses given IP and mask size"
	# (by Greg Jorgensen)

	n = dottedQuadToNum(ip)
	m = makeMask(maskbits)

	host = n & m
	net = n - host

	return numToDottedQuad(net), numToDottedQuad(host)

import unittest
	
class NetTestCase(unittest.TestCase):
	def testBidirectional(self):  ## test method names begin 'test*'
		self.assertEquals("127.0.0.1", ipLongToString(ipStringToLong("127.0.0.1")))
		self.assertEquals(16777343, ipStringToLong(ipLongToString(16777343)))
		
		
		self.assertEquals("255.231.201.198", ipLongToString(ipStringToLong("255.231.201.198")))
		self.assertEquals(3335120895, ipStringToLong(ipLongToString(3335120895)))
		
	def testValues(self):
		self.assertEquals(3335120895, ipStringToLong("255.231.201.198"))
		self.assertEquals(16777343, ipStringToLong("127.0.0.1"))

####################################################################################
"""Old Sauerbraten ones"""
####################################################################################
"""
def ipLongToString(num):
	return '%d.%d.%d.%d' % ((num & 0xff),
		(num >> 8) & 0xff,
		(num >> 16) & 0xff,
		(num >> 24) & 0xff)

def ipStringToLong(st):
	st = st.split('.')
	if len(st) != 4:
		raise ValueError('Not a valid ipv4 address')
	i = int(st[3])
	i = i << 8
	i = i | int(st[2])
	i = i << 8
	i = i | int(st[1])
	i = i << 8
	i = i | int(st[0])
	n = i
	if n > 0x7FFFFFFF:
		n = int(0x100000000 - n)
		if n < 2147483648:
			return -n
		else:
			return -2147483648
	return n
"""