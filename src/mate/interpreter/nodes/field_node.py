from mate.interpreter.nodes.mate_node import MateNode
from mate.vm.constants import ReflectiveOp
from som.vmobjects.integer import Integer

class MateFieldNode(MateNode):

    def execute(self, frame):

        value = None
        receiver = self._som_node.get_receiver(frame)

        if not frame.meta_level():
            value = self.do_mate_semantics(frame, receiver)

        if value is None:
            return self._som_node.execute_with_receiver(frame, receiver)
        else:
            return value

class MateFieldReadNode(MateFieldNode):

    def get_meta_args(self, frame):
        return [Integer(self._som_node.field_idx() + 1)]

    def reflective_op(self):
        return ReflectiveOp.ExecutorReadField


class MateFieldWriteNode(MateNode):

    def get_meta_args(self, frame):
        return [Integer(self._som_node.field_idx() + 1), self._som_node.value(frame)]

    def reflective_op(self):
        return ReflectiveOp.ExecutorWriteField
