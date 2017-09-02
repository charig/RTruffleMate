from .expression_node import ExpressionNode


class LiteralNode(ExpressionNode):

    _immutable_fields_ = ["_value"]

    def __init__(self, value, source_section = None):
        ExpressionNode.__init__(self, source_section)
        self._value = value

    def get_value(self):
    	return self._value

    def execute(self, frame):
        return self._value

    def _accept(self, visitor):
    	visitor.visit_LiteralNode(self)
