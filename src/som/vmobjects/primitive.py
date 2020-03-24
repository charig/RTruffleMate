from som.vmobjects.abstract_object    import AbstractObject
from mate.interpreter.invokable import MateInvokablePrimitive
from som.vmobjects.object import Object
from som.vmobjects.array         import Array
from som.vmobjects.context       import Context
from som.vm.globals import trueObject

class Primitive(AbstractObject):
    _immutable_fields_ = ["_prim_fun", "_is_empty", "_signature", "_holder",
                          "_universe"]
        
    def __init__(self, signature_string, universe, prim_fun, is_empty = False):
        AbstractObject.__init__(self)
        
        self._signature = universe.symbol_for(signature_string)
        self._prim_fun  = prim_fun
        self._is_empty  = is_empty
        self._holder    = None
        self._universe  = universe

    def get_universe(self):
        return self._universe

    def invoke(self, rcvr, args, call_frame):
        inv = self._prim_fun
        return inv(self, rcvr, args, call_frame)

    @staticmethod
    def is_primitive():
        return True

    @staticmethod
    def is_invokable():
        """ We use this method to identify methods and primitives """
        return True

    def get_signature(self):
        return self._signature

    def get_holder(self):
        return self._holder

    def set_holder(self, value):
        self._holder = value

    def is_empty(self):
        # By default a primitive is not empty
        return self._is_empty
    
    def get_class(self, universe):
        return universe.primitiveClass

    def __str__(self):
        return ("Primitive(" + self.get_holder().get_name().get_string() + ">>"
                + str(self.get_signature()) + ")")

    def mateify(self):
        return MatePrimitive(self._signature, self._universe, self._prim_fun, self._holder, self._is_empty)

class MatePrimitive(Primitive):
    _immutable_fields_ = ["_invokable"]

    def __init__(self, signature, universe, prim_fun, holder, is_empty):
        AbstractObject.__init__(self)

        self._signature = signature
        self._prim_fun  = prim_fun
        self._is_empty  = is_empty
        self._holder    = holder
        self._universe  = universe

        self._invokable = MateInvokablePrimitive()

    def invoke(self, receiver, arguments, call_frame):

        inv = self._prim_fun

        if call_frame is None or call_frame.meta_level():
            return inv(self, receiver, arguments, call_frame)

        environment = call_frame.get_meta_object_environment() or receiver.get_meta_object_environment()

        # No esta definido o es Nil
        if environment is None or not isinstance(environment, Object):
            return inv(self, receiver, arguments, call_frame)

        method = self._invokable.lookup_meta_invokable(environment)
        if method is None:
            # El mate enviroment no define el methodo correspondiente a este nodo
            return inv(self, receiver, arguments, call_frame)

        sm_args = method.invoke_to_mate(receiver, [self.get_signature(), Array.from_objects([environment, trueObject, receiver] + arguments)], call_frame)
        assert(isinstance(sm_args, Array))
        new_args = sm_args.as_argument_array()

        return inv(self, new_args[2], new_args[3:], call_frame)

def empty_primitive(signature_string, universe):
    """ Return an empty primitive with the given signature """
    return Primitive(signature_string, universe, _invoke, True)

def _invoke(ivkbl, rcvr, args, call_frame):
    """ Write a warning to the screen """
    print "Warning: undefined primitive %s called" % str(ivkbl.get_signature())
