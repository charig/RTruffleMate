from mate.interpreter.nodes.mate_node import MateNode
from mate.vm.constants import ReflectiveOp
from som.interpreter.nodes.expression_node import ExpressionNode
from som.vmobjects.object import Object
from som.vmobjects.array         import Array
import som.vm.universe
from mate.interpreter.nodes.lookup import UninitializedMateLookUpNode
from rpython.rlib.jit import we_are_jitted
from som.vmobjects.context       import Context
from som.vm.globals import trueObject, falseObject

class MateInvokablePrimitive(ExpressionNode):
    _immutable_fields_ = ["_lookup_node?"]
    _child_nodes_ = ["_lookup_node"]

    def __init__(self, source_section = None):
        self._lookup_node = self.adopt_child(UninitializedMateLookUpNode(self.reflective_op(), som.vm.universe.get_current()))

    def reflective_op(self):
        return ReflectiveOp.MessageActivation

    def replace_lookup_list_head(self, node):
        self._lookup_node.replace(node)

    def lookup_meta_invokable(self, environment):
        return self._lookup_node.lookup_meta_invokable(environment)

class MateInvokable(MateNode):

    def __init__(self, som_node, source_section = None):
        ExpressionNode.__init__(self, source_section)
        som_node.get_method().set_invokable(self)
        self._som_node = self.adopt_child(som_node)
        self._lookup_node = self.adopt_child(UninitializedMateLookUpNode(self.reflective_op(), som.vm.universe.get_current()))

    def get_som_node(self):
        return self._som_node

    def invoke_to_mate(self, receiver, arguments, call_frame):
        return self._som_node.invoke_to_mate(receiver, arguments, call_frame)

    def invoke_from_mate(self, receiver, arguments, call_frame, meta_object):
        return self._som_node.invoke_from_mate(receiver, arguments, call_frame, meta_object)

    def invoke(self, receiver, arguments, call_frame):

        if call_frame is None or call_frame.meta_level():
            return self._som_node.invoke(receiver, arguments, call_frame)

        environment = call_frame.get_meta_object_environment() or receiver.get_meta_object_environment()

        # No esta definido o es Nil
        if environment is None or not isinstance(environment, Object):
            return self._som_node.invoke(receiver, arguments, call_frame)

        method = self._lookup_node.lookup_meta_invokable(environment)
        if method is None:
            # El mate enviroment no define el methodo correspondiente a este nodo
            return self._som_node.invoke(receiver, arguments, call_frame)

        sm_args = method.invoke_to_mate(receiver, [self._som_node.get_method().get_signature(), Array.from_objects([environment, trueObject, receiver] + arguments)], call_frame)
        assert(isinstance(sm_args, Array))
        new_args = sm_args.as_argument_array()

        if new_args[1] == falseObject:
            # Paso a base level
            if isinstance(new_args[0], Object):
                environment = new_args[0]
            else:
                environment = None

            return self._som_node.invoke_from_mate(new_args[2], new_args[3:], call_frame, environment)
        else:
            # Sigo en meta level
            return self._som_node.invoke_to_mate(new_args[2], new_args[3:], call_frame)

    def reflective_op(self):
        return ReflectiveOp.MessageActivation