from som.vmobjects.abstract_object import AbstractObject


class ObjectWithoutFields(AbstractObject):

    _immutable_fields_ = ["_class"]

    def __init__(self, obj_class):
        AbstractObject.__init__(self)
        self._class = obj_class

    def get_class(self, universe):
        return self._class

    def set_class(self, value):
        self._class = value

    def get_number_of_fields(self):
        return 0
