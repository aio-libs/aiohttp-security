from sphinx import addnodes
from sphinx.domains.python import PyClassmember, PyModulelevel


class PyCoroutineMixin:
    def handle_signature(self, sig, signode):
        ret = super().handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_annotation("coroutine ", "coroutine "))
        return ret


class PyCoroutineFunction(PyCoroutineMixin, PyModulelevel):
    def run(self):
        self.name = "py:function"
        return PyModulelevel.run(self)


class PyCoroutineMethod(PyCoroutineMixin, PyClassmember):
    def run(self):
        self.name = "py:method"
        return PyClassmember.run(self)


def setup(app):
    app.add_directive_to_domain("py", "coroutinefunction", PyCoroutineFunction)
    app.add_directive_to_domain("py", "coroutinemethod", PyCoroutineMethod)
    return {"version": "1.0", "parallel_read_safe": True}
