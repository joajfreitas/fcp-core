import copy

from PySide2.QtCore import Signal
from PySide2.QtWidgets import *

class UndoState():
    def __init__(self):
        pass

    def undo(self):
        print("UndoState should not be used directly")
        exit()


class UndoUpdate(UndoState):
    def __init__(self, obj, var, old, new):
        self.obj = obj
        self.var = var
        self.old = old
        self.new = new

        if old == new:
            return None

    def undo(self):
        setattr(self.obj, self.var, self.old)

    def redo(self):
        setattr(self.obj, self.var, self.new)

    def __repr__(self):
        return f"{self.var} {self.old} {self.new}"

class UndoAdd(UndoState):
    #delete_sig = Signal()
    def __init__(self, obj, holder, remove, add):
        self.obj = obj
        self.holder = holder
        self.remove = remove
        self.add = add

    def undo(self):
        print("undo")
        self.obj = copy.copy(self.obj)
        #print("remove from spec", self.obj.spec.rm_node(self.obj))
        self.remove()

    def redo(self):
        self.holder.node = self.obj
        self.holder.show()

    def __repr__(self):
        return f"{self.obj}"

class UndoRedo():
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []
        return

    def push(self, state):
        print("push", state)
        if state is None:
            return
        self.undo_stack.append(state)
        self.redo_stack = []

    def undo(self):
        if len(self.undo_stack) == 0:
            print("Undo not possible")
            return

        state = self.undo_stack.pop()
        state.undo()
        self.redo_stack.append(state)

    def redo(self):
        if len(self.redo_stack) == 0:
            print("Redo not possible")
            return

        state = self.redo_stack.pop()
        state.redo()
        self.undo_stack.append(state)
