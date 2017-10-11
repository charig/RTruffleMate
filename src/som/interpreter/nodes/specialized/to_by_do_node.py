from rpython.rlib import jit

from .to_do_node       import AbstractToDoNode

from ....vmobjects.block   import Block
from ....vmobjects.double  import Double
from ....vmobjects.integer import Integer
from ....vmobjects.method  import Method


class AbstractToByDoNode(AbstractToDoNode):

    _immutable_fields_ = ['_step_expr?']
    _child_nodes_      = ['_step_expr' ]

    def __init__(self, rcvr_expr, limit_expr, step_expr, body_expr, universe,
                 source_section = None):
        AbstractToDoNode.__init__(self, rcvr_expr, limit_expr, body_expr,
                                  universe, source_section)
        self._step_expr  = self.adopt_child(step_expr)

    def evaluate_rcvr_and_args(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        limit = self._limit_expr.execute(frame)
        step  = self._step_expr.execute(frame)
        body  = self._body_expr.execute(frame)

        return rcvr, [limit, step, body]

    def execute(self, frame):
        rcvr  = self._rcvr_expr.execute(frame)
        limit = self._limit_expr.execute(frame)
        step  = self._step_expr.execute(frame)
        body  = self._body_expr.execute(frame)
        self._to_by_loop(rcvr, limit, step, body, frame)
        return rcvr
    
    def execute_evaluated(self, frame, rcvr, args):
        self._to_by_loop(rcvr, args[0], args[1], args[2], frame)
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


class IntToIntByDoNode(AbstractToByDoNode):

    def get_selector(self):
        return self._universe.symbol_for("to:by:do:")

    def _to_by_loop(self, rcvr, limit, step, body_block, call_frame):
        block_method = body_block.get_method()

        i   = rcvr.get_embedded_integer()
        top = limit.get_embedded_integer()
        by  = step.get_embedded_integer()
        while i <= top:
            int_driver.jit_merge_point(block_method = block_method)
            block_method.invoke(body_block, [self._universe.new_integer(i)], call_frame)
            i += by

    @staticmethod
    def can_specialize(selector, rcvr, args, node):
        return (isinstance(args[0], Integer) and isinstance(rcvr, Integer) and
                len(args) == 3 and isinstance(args[1], Integer) and
                isinstance(args[2], Block) and
                selector.get_string() == "to:by:do:")

    @staticmethod
    def specialize_node(selector, rcvr, args, node):
        return node.replace(
            IntToIntByDoNode(node._rcvr_expr, node._arg_exprs[0],
                             node._arg_exprs[1], node._arg_exprs[2],
                             node._universe, node._source_section))

double_driver = jit.JitDriver(
    greens=['block_method'],
    reds='auto',
    is_recursive=True,
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)


class IntToDoubleByDoNode(AbstractToByDoNode):

    def get_selector(self):
        return self._universe.symbol_for("to:by:do:")

    def _to_by_loop(self, rcvr, limit, step, body_block, call_frame):
        block_method = body_block.get_method()

        i   = rcvr.get_embedded_integer()
        top = limit.get_embedded_double()
        by  = step.get_embedded_integer()
        while i <= top:
            double_driver.jit_merge_point(block_method = block_method)
            block_method.invoke(body_block, [self._universe.new_integer(i)], call_frame)
            i += by

    @staticmethod
    def can_specialize(selector, rcvr, args, node):
        return (isinstance(args[0], Double) and isinstance(rcvr, Integer) and
                len(args) == 3 and isinstance(args[1], Integer) and
                isinstance(args[2], Block) and
                selector.get_string() == "to:by:do:")

    @staticmethod
    def specialize_node(selector, rcvr, args, node):
        return node.replace(
            IntToDoubleByDoNode(node._rcvr_expr, node._arg_exprs[0],
                                node._arg_exprs[1], node._arg_exprs[2],
                                node._universe, node._source_section))
