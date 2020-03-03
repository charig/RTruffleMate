from som.vmobjects.abstract_object import AbstractObject
import os

class File(AbstractObject):
    _immutable_fields_ = ["_size"]
    
    def __init__(self, filename, writable):
        AbstractObject.__init__(self)

        if writable:
            self._stream = open(filename, 'ab')
        else:
            self._stream = open(filename, 'rb')

        self._stream.seek(0, os.SEEK_END)
        self._size = self._stream.tell()
        self._stream.seek(0, os.SEEK_SET)
    
    def get_embedded_stream(self):
        return self._stream

    def get_size(self):
        return self._size

    def close(self):
        return self._stream.close()

    def get_position(self):
        return self._stream.tell()

    def set_position(self, position):
        self._stream.seek(position, os.SEEK_SET)

    def at_end(self):
        return self._stream.tell() == self._size

    def __str__(self):
        return "\"" + self._string + "\""

    def get_class(self, universe):
        return universe.fileClass
