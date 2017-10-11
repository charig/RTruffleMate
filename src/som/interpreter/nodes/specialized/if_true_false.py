from ..expression_node   import ExpressionNode
from som.vm.globals import nilObject, trueObject, falseObject
from ....vmobjects.block import Block


class IfTrueIfFalseNode(ExpressionNode):

    _immutable_fields_ = ['_rcvr_expr?', '_true_expr?', '_false_expr?',
                          '_universe']
    _child_nodes_      = ['_rcvr_expr',  '_true_expr',  '_false_expr']

    def __init__(self, rcvr_expr, true_expr, false_expr, universe,
                 source_section):
        ExpressionNode.__init__(self, source_section)
        self._rcvr_expr  = self.adopt_child(rcvr_expr)
        self._true_expr  = self.adopt_child(true_expr)
        self._false_expr = self.adopt_child(false_expr)
        self._universe   = universe

    def get_universe(self):
        return self._universe

    def get_selector(self):
        return self._universe.symbol_for("ifTrue:ifFalse:")

    def evaluate_rcvr_and_args(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        true  = self._true_expr.execute(frame)
        false = self._false_expr.execute(frame)

        return rcvr, [true, false]

    def execute(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        true  = self._true_expr.execute(frame)
        false = self._false_expr.execute(frame)

        return self._do_iftrue_iffalse(rcvr, true, false, frame)

    def execute_evaluated(self, frame, rcvr, args):
        return self._do_iftrue_iffalse(rcvr, args[0], args[1], frame)

    def _value_of(self, obj, call_frame):
        if isinstance(obj, Block):
            return obj.get_method().invoke(obj, [], call_frame)
        else:
            return obj

    def _do_iftrue_iffalse(self, rcvr, true, false, call_frame):
        if rcvr is trueObject:
            return self._value_of(true, call_frame)
        else:
            assert rcvr is falseObject
            return self._value_of(false, call_frame)

    @staticmethod
    def can_specialize(selector, rcvr, args, node):
        return (len(args) == 2 and (rcvr is trueObject or rcvr is falseObject)
                and selector.get_string() == "ifTrue:ifFalse:")

    @staticmethod
    def specialize_node(selector, rcvr, args, node):
        return node.replace(
            IfTrueIfFalseNode(node._rcvr_expr, node._arg_exprs[0],
                              node._arg_exprs[1], node._universe,
                              node._source_section))


class IfNode(ExpressionNode):

    _immutable_fields_ = ['_rcvr_expr?', '_branch_expr?', '_condition',
                          '_universe']
    _child_nodes_      = ['_rcvr_expr',  '_branch_expr']

    def __init__(self, rcvr_expr, branch_expr, condition_obj, universe,
                 source_section):
        ExpressionNode.__init__(self, source_section)
        self._rcvr_expr   = self.adopt_child(rcvr_expr)
        self._branch_expr = self.adopt_child(branch_expr)
        self._condition   = condition_obj
        self._universe    = universe

    def get_universe(self):
        return self._universe

    def get_selector(self):
        if self._condition is trueObject:
            return self._universe.symbol_for("ifTrue:")
        else:
            return self._universe.symbol_for("ifFalse")

    def evaluate_rcvr_and_args(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        branch = self._branch_expr.execute(frame)

        return rcvr, [branch]

    def execute(self, frame):
        rcvr   = self._rcvr_expr.execute(frame)
        branch = self._branch_expr.execute(frame)
        return self._do_if(rcvr, branch, frame)

    def execute_evaluated(self, frame, rcvr, args):
        return self._do_if(rcvr, args[0], frame)

    def _value_of(self, obj, call_frame):
        if isinstance(obj, Block):
            return obj.get_method().invoke(obj, [], call_frame)
        else:
            return obj

    def _do_if(self, rcvr, branch, call_frame):
        if rcvr is self._condition:
            return self._value_of(branch, call_frame)
        else:
            assert (rcvr is falseObject or rcvr is trueObject)
            return nilObject

    @staticmethod
    def can_specialize(selector, rcvr, args, node):
        sel = selector.get_string()
        return (len(args) == 1 and (rcvr is trueObject or rcvr is falseObject)
                and (sel == "ifTrue:" or sel == "ifFalse:"))

    @staticmethod
    def specialize_node(selector, rcvr, args, node):
        if selector.get_string() == "ifTrue:":
            return node.replace(
                IfNode(node._rcvr_expr, node._arg_exprs[0],
                       trueObject, node._universe, node._source_section))
        else:
            assert selector.get_string() == "ifFalse:"
            return node.replace(
                IfNode(node._rcvr_expr, node._arg_exprs[0],
                       falseObject, node._universe, node._source_section))
