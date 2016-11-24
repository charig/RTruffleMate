from rpython.rlib.objectmodel import compute_hash

from som.primitives.primitives import Primitives
from som.vm.globals import falseObject, trueObject
from som.vmobjects.primitive import Primitive
from som.vmobjects.string import String
from som.vmobjects.character import Character
from som.vmobjects.symbol import Symbol


def _concat(ivkbl, rcvr, args):
    argument = args[0]
    return ivkbl.get_universe().new_string(rcvr.get_embedded_string()
                                           + argument.get_embedded_string())


def _asSymbol(ivkbl, rcvr, args):
    return ivkbl.get_universe().symbol_for(rcvr.get_embedded_string())


def _length(ivkbl, rcvr, args):
    return ivkbl.get_universe().new_integer(len(rcvr.get_embedded_string()))


def _equals(ivkbl, rcvr, args):
    op1 = args[0]
    op2 = rcvr
    universe = ivkbl.get_universe()

    if isinstance(op1, String):
        if isinstance(op1, Symbol) and isinstance(op2, Symbol):
            if op1 is op2:
                return trueObject
            else:
                return falseObject
        if isinstance(op2, String):
            if op1.get_embedded_string() == op2.get_embedded_string():
                return trueObject

    if isinstance(op1, Character):
        string = op2.get_embedded_string() 
        if len(string) == 1 and string[0] == op1.get_embedded_character():
            return trueObject

    return falseObject


def _substring(ivkbl, rcvr, args):
    end   = args[1]
    start = args[0]

    s      = start.get_embedded_integer() - 1
    e      = end.get_embedded_integer()
    string = rcvr.get_embedded_string()
    
    if s < 0 or s >= len(string) or e > len(string) or e < s: 
        return ivkbl.get_universe().new_string("Error - index out of bounds")
    else:
        return ivkbl.get_universe().new_string(string[s:e])


def _hashcode(ivkbl, rcvr, args):
    return ivkbl.get_universe().new_integer(
        compute_hash(rcvr.get_embedded_string()))

def _at(ivkbl, rcvr, args):
    index = args[0]
    string = rcvr.get_embedded_string()

    i      = index.get_embedded_integer() - 1
    string = rcvr.get_embedded_string()
    
    if i < 0 or i >= len(string): 
        return ivkbl.get_universe().new_string("Error - index out of bounds")
    else:
        return ivkbl.get_universe().new_string(string[i])

def _charAt(ivkbl, rcvr, args):
    index = args[0]
    string = rcvr.get_embedded_string()

    i      = index.get_embedded_integer() - 1
    string = rcvr.get_embedded_string()
    
    if i < 0 or i >= len(string): 
        return ivkbl.get_universe().new_string("Error - index out of bounds")
    else:
        return ivkbl.get_universe().new_character(string[i])


class StringPrimitives(Primitives):
    
    def install_primitives(self):        
        self._install_instance_primitive(Primitive("concatenate:",          self._universe, _concat))
        self._install_instance_primitive(Primitive("asSymbol",              self._universe, _asSymbol))
        self._install_instance_primitive(Primitive("length",                self._universe, _length))
        self._install_instance_primitive(Primitive("=",                     self._universe, _equals))
        self._install_instance_primitive(Primitive("primSubstringFrom:to:", self._universe, _substring))
        self._install_instance_primitive(Primitive("hashcode",              self._universe, _hashcode))
        self._install_instance_primitive(Primitive("at:",                   self._universe, _at))
        self._install_instance_primitive(Primitive("charAt:",               self._universe, _charAt))
