from docutils import nodes
from sphinx import addnodes
from sphinx.domains.python import PyFunction, PyMethod


class PyCoroutineMixin:
    def get_signature_prefix(self, sig):
        return [nodes.Text('coroutine'), addnodes.desc_sig_space()]


class PyCoroutineFunction(PyCoroutineMixin, PyFunction):
    pass


class PyCoroutineMethod(PyCoroutineMixin, PyMethod):
    pass


def setup(app):
    app.add_directive_to_domain('py', 'coroutinefunction', PyCoroutineFunction)
    app.add_directive_to_domain('py', 'coroutinemethod', PyCoroutineMethod)
    return {'version': '1.0', 'parallel_read_safe': True}
