from rpython.rlib import jit

from ..expression_node import ExpressionNode

from ....vmobjects.block   import Block
from ....vmobjects.double  import Double
from ....vmobjects.integer import Integer
from ....vmobjects.method  import Method


class AbstractToDoNode(ExpressionNode):

    _immutable_fields_ = ['_rcvr_expr?', '_limit_expr?', '_body_expr?',
                          '_universe']
    _child_nodes_      = ['_rcvr_expr', '_limit_expr', '_body_expr']

    def __init__(self, rcvr_expr, limit_expr, body_expr, universe,
                 source_section = None):
        ExpressionNode.__init__(self, source_section)
        self._rcvr_expr  = self.adopt_child(rcvr_expr)
        self._limit_expr = self.adopt_child(limit_expr)
        self._body_expr  = self.adopt_child(body_expr)
        self._universe   = universe

    def evaluate_rcvr_and_args(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        limit = self._limit_expr.execute(frame)
        body  = self._body_expr.execute(frame)

        return rcvr, [limit, body]

    def get_universe(self):
        return self._universe

    def execute(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        limit = self._limit_expr.execute(frame)
        body  = self._body_expr.execute(frame)
        self._do_loop(rcvr, limit, body, frame)
        return rcvr

    def execute_evaluated(self, frame, rcvr, args):
        self._do_loop(rcvr, args[0], args[1], frame)
        return rcvr


def get_printable_location(block_method):
    assert isinstance(block_method, Method)
    return "#to:do: %s" % block_method.merge_point_string()


int_driver = jit.JitDriver(
    greens=['block_method'],
    reds='auto',
    is_recursive=True,
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)


class IntToIntDoNode(AbstractToDoNode):

    def _do_loop(self, rcvr, limit, body_block, call_frame):
        block_method = body_block.get_method()

        i   = rcvr.get_embedded_integer()
        top = limit.get_embedded_integer()
        while i <= top:
            int_driver.jit_merge_point(block_method = block_method)
            block_method.invoke(body_block, [self._universe.new_integer(i)], call_frame)
            i += 1

    def get_selector(self):
        return self._universe.symbol_for("to:do:")

    @staticmethod
    def can_specialize(selector, rcvr, args, node):
        return (isinstance(args[0], Integer) and isinstance(rcvr, Integer) and
                len(args) > 1 and isinstance(args[1], Block) and
                selector.get_string() == "to:do:")

    @staticmethod
    def specialize_node(selector, rcvr, args, node):
        return node.replace(
            IntToIntDoNode(node._rcvr_expr, node._arg_exprs[0],
                           node._arg_exprs[1], node._universe,
                           node._source_section))


double_driver = jit.JitDriver(
    greens=['block_method'],
    reds='auto',
    is_recursive=True,
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)


class IntToDoubleDoNode(AbstractToDoNode):

    def _do_loop(self, rcvr, limit, body_block, call_frame):
        block_method = body_block.get_method()

        i   = rcvr.get_embedded_integer()
        top = limit.get_embedded_double()
        while i <= top:
            double_driver.jit_merge_point(block_method = block_method)
            block_method.invoke(body_block, [self._universe.new_integer(i)], call_frame)
            i += 1

    def get_selector(self):
        return self._universe.symbol_for("to:do")

    @staticmethod
    def can_specialize(selector, rcvr, args, node):
        return (isinstance(args[0], Double) and isinstance(rcvr, Integer) and
                len(args) > 1 and isinstance(args[1], Block) and
                selector.get_string() == "to:do:")

    @staticmethod
    def specialize_node(selector, rcvr, args, node):
        return node.replace(
            IntToDoubleDoNode(node._rcvr_expr, node._arg_exprs[0],
                              node._arg_exprs[1], node._universe,
                              node._source_section))
