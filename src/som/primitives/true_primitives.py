from som.primitives.primitives import Primitives
from som.vm.globals import falseObject, trueObject
from som.vmobjects.primitive import Primitive


def _not(ivkbl, rcvr, args, meta_level):
    return falseObject


def _or(ivkbl, rcvr, args, meta_level):
    return trueObject


def _and(ivkbl, rcvr, args, meta_level):
    block = args[0]
    block_method = block.get_method()
    return block_method.invoke(block, [], meta_level)


class TruePrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("not", self._universe, _not))
        self._install_instance_primitive(Primitive("or:", self._universe, _or))
        self._install_instance_primitive(Primitive("and:", self._universe, _and))
        self._install_instance_primitive(Primitive("||", self._universe, _or))
        self._install_instance_primitive(Primitive("&&", self._universe, _and))
