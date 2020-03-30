from rpython.rlib.jit import we_are_jitted
from .expression_node import ExpressionNode
from som.interpreter.objectstorage.field_accessor_node import create_read, \
    create_write

from som.vmobjects.abstract_object import AbstractObject
from som.vmobjects.object          import Object


class _AbstractFieldNode(ExpressionNode):

    _immutable_fields_ = ["_self_exp?", "_field_idx"]
    _child_nodes_      = ["_self_exp"]

    def __init__(self, self_exp, field_idx, source_section):
        ExpressionNode.__init__(self, source_section)
        self._self_exp  = self.adopt_child(self_exp)
        self._field_idx = field_idx

    def field_idx(self):
        return self._field_idx

    def get_receiver(self, frame):
        return self._self_exp.execute(frame)

    def _children_accept(self, visitor):
        ExpressionNode._children_accept(self, visitor)
        self._self_exp.accept(visitor)

    def _accept(self, visitor):
        raise NotImplementedError("You cant visit this node")

class FieldReadNode(_AbstractFieldNode):

    _immutable_fields_ = ['_read?']
    _child_nodes_      = ['_read']

    def __init__(self, self_exp, field_idx, source_section):
        _AbstractFieldNode.__init__(self, self_exp, field_idx, source_section)
        self._read = self.adopt_child(create_read(field_idx))

    def execute_with_receiver(self, frame, self_obj):
        assert isinstance(self_obj, Object)

        return self._read.read(frame, self_obj)

    def execute(self, frame):
        self_obj = self._self_exp.execute(frame)
        assert isinstance(self_obj, Object)
        if we_are_jitted():
            return self_obj.get_field(self._field_idx)
        else:
            return self._read.read(frame, self_obj)

    def _accept(self, visitor):
        visitor.visit_FieldReadNode(self)

    def _children_accept(self, visitor):
        _AbstractFieldNode._children_accept(self, visitor)
        self._read.accept(visitor)


class FieldWriteNode(_AbstractFieldNode):

    _immutable_fields_ = ["_value_exp?", "_write?"]
    _child_nodes_      = ["_value_exp",  "_write"]

    def __init__(self, self_exp, value_exp, field_idx, source_section):
        _AbstractFieldNode.__init__(self, self_exp, field_idx, source_section)
        self._value_exp = self.adopt_child(value_exp)
        self._write     = self.adopt_child(create_write(field_idx))

    def execute_with_receiver(self, frame, self_obj):
        value = self._value_exp.execute(frame)

        assert isinstance(self_obj, Object)
        assert isinstance(value, AbstractObject)

        self._write.write(frame, self_obj, value)

        return value

    def value(self, frame):
        return self._value_exp.execute(frame)

    def execute(self, frame):
        self_obj = self._self_exp.execute(frame)
        value = self._value_exp.execute(frame)

        assert isinstance(self_obj, Object)
        assert isinstance(value, AbstractObject)

        if we_are_jitted():
            self_obj.set_field(self._field_idx, value)
        else:
            self._write.write(frame, self_obj, value)

        return value

    def _accept(self, visitor):
        visitor.visit_FieldWriteNode(self)

    def _children_accept(self, visitor):
        _AbstractFieldNode._children_accept(self, visitor)
        self._write.accept(visitor)
        self._value_exp.accept(visitor)

def create_read_node(self_exp, index, source_section = None):
    return FieldReadNode(self_exp, index, source_section)


def create_write_node(self_exp, value_exp, index, source_section = None):
    return FieldWriteNode(self_exp, value_exp, index, source_section)
