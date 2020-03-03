from som.primitives.primitives import Primitives
from som.vm.globals import falseObject, trueObject, nilObject
from som.vmobjects.primitive import Primitive
from som.vmobjects.file import File
from som.vmobjects.string import String
from som.vmobjects.integer import Integer
from som.vmobjects.array import Array
import os
from rpython.rlib.debug import attach_gdb

def _prim_open_writable(ivkbl, rcvr, args, call_frame):
    filename = args[0]
    writable = args[1]

    s = filename.get_embedded_string()
    print s

    if not s or len(s) < 1:
        return nilObject

    try:
        if (writable == trueObject):
            return File(s, True)
        else:
            return File(s, False)
    except:
        return nilObject

def _prim_get_position(ivkbl, rcvr, args, call_frame):
    file = args[0]
    return ivkbl.get_universe().new_integer(int(file.get_position()))

def _prim_close(ivkbl, rcvr, args, call_frame):
    file = args[0]
    file.close()
    return nilObject

def _prim_set_position_to(ivkbl, rcvr, args, call_frame):
    file = args[0]
    position = args[1]
    file.set_position(position.get_embedded_integer())
    return rcvr

def _prim_size(ivkbl, rcvr, args, call_frame):
    file = args[0]
    return ivkbl.get_universe().new_integer(int(file.get_size()))

def _prim_read_into_starting_at_count(ivkbl, rcvr, args, call_frame):
    file       = args[0]
    collection = args[1]
    start      = args[2]
    count      = args[3]

    assert isinstance(file, File)
    assert isinstance(collection, Array)
    assert isinstance(start, Integer)
    assert isinstance(count, Integer)

    stream = file.get_embedded_stream()
    stream.seek(start.get_embedded_integer() - 1, os.SEEK_SET)

    content = stream.read(count.get_embedded_integer());
    collection.set_all(ivkbl.get_universe().new_character(' '))

    i = 0
    for c in content:
        collection.set_indexable_field(i, ivkbl.get_universe().new_character(c))
        i = i + 1

    return ivkbl.get_universe().new_integer(i)

def _prim_at_end(ivkbl, rcvr, args, call_frame):
    file = args[0]
    if file.at_end():
        return trueObject
    else:
        return falseObject

def _prim_size_no_error(ivkbl, rcvr, args, call_frame):
    file = args[0]
    try:
        return ivkbl.get_universe().new_integer(int(file.get_size()))
    except:
        return nilObject

class StandardFileStreamPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("primOpen:writable:",              self._universe, _prim_open_writable))
        self._install_instance_primitive(Primitive("primGetPosition:",                self._universe, _prim_get_position))
        self._install_instance_primitive(Primitive("primSetPosition:to:",             self._universe, _prim_set_position_to))
        self._install_instance_primitive(Primitive("primSize:",                       self._universe, _prim_size))
        self._install_instance_primitive(Primitive("primClose:",                       self._universe, _prim_close))
        self._install_instance_primitive(Primitive("primSizeNoError:",                       self._universe, _prim_size_no_error))
        self._install_instance_primitive(Primitive("primRead:into:startingAt:count:", self._universe, _prim_read_into_starting_at_count))
        self._install_instance_primitive(Primitive("primAtEnd:",                      self._universe, _prim_at_end))
