from __future__ import absolute_import

from rpython.rlib import jit

from som.vmobjects.array import Array

class Method(Array):
    
    # Static field indices and number of method fields
    SIGNATURE_INDEX                 = Array.NUMBER_OF_OBJECT_FIELDS
    HOLDER_INDEX                    = 1 + SIGNATURE_INDEX
    NUMBER_OF_METHOD_FIELDS         = 1 + HOLDER_INDEX

    _immutable_fields_ = ["_bytecodes[*]",
                          "_inline_cache_class",
                          "_receiver_class_table",
                          "_number_of_locals",
                          "_maximum_number_of_stack_elements"]

    
    def __init__(self, nilObject, num_literals, num_locals, max_stack_elements,
                 num_bytecodes, signature):
        Array.__init__(self, nilObject, num_literals)

        # Set the number of bytecodes in this method
        self._bytecodes              = ["\x00"] * num_bytecodes
        self._inline_cache_class     = [None]   * num_bytecodes
        self._inline_cache_invokable = [None]   * num_bytecodes
        
        self._number_of_locals       = num_locals
        self._maximum_number_of_stack_elements = max_stack_elements
        self._set_signature(signature)
        
    
    def is_primitive(self):
        return False
    
    def is_invokable(self):
        """In the RPython version, we use this method to identify methods 
           and primitives
        """
        return True
  
    def get_number_of_locals(self):
        # Get the number of locals
        return self._number_of_locals

    def get_maximum_number_of_stack_elements(self):
        # Get the maximum number of stack elements
        return self._maximum_number_of_stack_elements

    def get_signature(self):
        # Get the signature of this method by reading the field with signature
        # index
        return self.get_field(self.SIGNATURE_INDEX)

    def _set_signature(self, value):
        # Set the signature of this method by writing to the field with
        # signature index
        self.set_field(self.SIGNATURE_INDEX, value)

    def get_holder(self):
        # Get the holder of this method by reading the field with holder index
        return self.get_field(self.HOLDER_INDEX)

    def set_holder(self, value):
        # Set the holder of this method by writing to the field with holder index
        self.set_field(self.HOLDER_INDEX, value)

        # Make sure all nested invokables have the same holder
        for i in range(0, self.get_number_of_indexable_fields()):
            if self.get_indexable_field(i).is_invokable():
                self.get_indexable_field(i).set_holder(value)

    def get_constant(self, bytecode_index):
        # Get the constant associated to a given bytecode index
        return self.get_indexable_field(self.get_bytecode(bytecode_index + 1))

    def get_number_of_arguments(self):
        # Get the number of arguments of this method
        return self.get_signature().get_number_of_signature_arguments()
  
    def _get_default_number_of_fields(self):
        # Return the default number of fields in a method
        return self.NUMBER_OF_METHOD_FIELDS
  
    def get_number_of_bytecodes(self):
        # Get the number of bytecodes in this method
        return len(self._bytecodes)

    @jit.elidable
    def get_bytecode(self, index):
        # Get the bytecode at the given index
        assert 0 <= index and index < len(self._bytecodes)
        return ord(self._bytecodes[index])

    def set_bytecode(self, index, value):
        # Set the bytecode at the given index to the given value
        assert 0 <= value and value <= 255
        self._bytecodes[index] = chr(value)

    def invoke(self, frame, interpreter):
        # Allocate and push a new frame on the interpreter stack
        new_frame = interpreter.push_new_frame(self,
                                    interpreter.get_universe().nilObject)
        new_frame.copy_arguments_from(frame)

    def __str__(self):
        return "Method(" + self.get_holder().get_name().get_string() + ">>" + str(self.get_signature()) + ")"

    @jit.elidable
    def get_inline_cache_class(self, bytecode_index):
        assert 0 <= bytecode_index and bytecode_index < len(self._inline_cache_class)
        return self._inline_cache_class[bytecode_index]

    @jit.elidable
    def get_inline_cache_invokable(self, bytecode_index):
        assert 0 <= bytecode_index and bytecode_index < len(self._inline_cache_invokable)
        return self._inline_cache_invokable[bytecode_index]

    def set_inline_cache(self, bytecode_index, receiver_class, invokable):
        self._inline_cache_class[bytecode_index]    = receiver_class
        self._inline_cache_invokable[bytecode_index] = invokable

    def merge_point_string(self):
        """ debug info for the jit """
        return "%s>>%s" % (self.get_holder().get_name().get_string(),
                           self.get_signature().get_string())
