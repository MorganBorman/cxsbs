import struct

class DataBuffer(object):
    def __init__(self, data):
        self.data = data
        self.len = len(self.data)
        self.pos = 0
        
    def remaining(self):
        return self.data[self.pos:]
        
    def get(self, size=1):
        try:
            return self.data[self.pos:self.pos+size]
        finally:
            self.pos += size
        
    def current(self):
        return self.data[self.pos]
        
    def empty(self):
        return self.pos >= self.len
        
    def getbuf(self, length):
        try:
            return databuf(self.data[self.pos:self.pos+length])
        finally:
            self.pos += length
        
    def getint(self):
        "Get a cube compressed integer."
        c = self.current()

        if c == "\x80":
                self.get()
                t = self.get(2)
                return struct.unpack('h', t)[0]
        elif c == "\x81":
                self.get()
                t = self.get(4)
                return struct.unpack('i', t)[0]
        else:
                return struct.unpack('b', self.get())[0]
        
    def getuint(self):
        "Get a cube compressed unsigned integer."
        n = ord(self.get())
        if(n & 0x80):
            n += (ord(self.get()) << 7) - 0x80
            if(n & (1<<14)):
                n += (ord(self.get()) << 14) - (1<<14)
            if(n & (1<<21)):
                n += (ord(self.get()) << 21) - (1<<21)
            if(n & (1<<28)):
                n |= -1<<28
        return n;
        
    def getfloat(self):
        t = self.get(4)
        return struct.unpack('f', t)[0]
        
    def getstring(self):
        clist = []
        c = self.get()
        while True:
            if c == "\0":
                return "".join(clist)
            
            clist.append(c)
            
            if self.empty():
                return "".join(clist)
            
            c = self.get()
            
    def getchar(self):
        return ord(self.get())

def makeint(i):
    """Make a compressed integer according to the cube udp compressions scheme"""
    if -127 < i and i < 128:
        return struct.pack("b", i)
    elif -0x8000 < i and i < 0x8000 :
        return "\x80" + struct.pack("h", i)
    else:
        return "\x81" + struct.pack("i", i)

def pack(format, data):
    rdata = []
    
    i = 0
    for f in format:
        if f == "i":
            rdata.append(makeint(data[i]))
        elif f == "f":
            rdata.append(struct.pack('f', data[i]))
        elif f == "s":
            rdata.append(data[i]+'\x00')
        i += 1
        
    return "".join(rdata)