class StaticBufferException( Exception ):
  pass

# 0 <= next <= lngt <= size
class StaticBuffer():

  def __init__( self, size ):
    self._bfr= bytearray( size )
    self.size= size			# Allocated size
    self.lngt= 0			# Current length
    self.next= 0			# Ordinal to start next write

  def clear( self ):
    self.lngt= 0
    self.next= 0

  def flush( self ):
    pass

  def getvalue( self ):
    return bytes(self._bfr[:self.lngt])

  def seek( self, ordinal ):
    if ordinal < 0  or  ordinal > self.next:
      raise StaticBufferException( b'Seek ordinal out of range' )
    self.next= ordinal

  def tell( self ):
    return self.next

  def write( self, astring ):
    if not isinstance( astring, bytes):
      raise StaticBufferException( b'Wrong parameter type' )
    eos= self.next + len(astring)	# End of slice ordinal
    if eos > self.size:
      raise StaticBufferException( b'String too long' )
    self._bfr[self.next:eos]= astring
    self.next= eos
    self.lngt= max( self.lngt, eos )
    return len(astring)

  @property
  def bfr(self):
      return self._bfr
