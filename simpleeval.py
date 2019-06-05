"""
``simple_eval()`` is like ``eval()``, but only allows simple
expressions.  Given relatively safe input, this can be thought of as a
safe eval (but of course unsafe input can cause any number of
problems).

Expressions given to simple_eval are limited to:

* Variables
* Non-private attribute access (no leading ``_``)
  - Attributes can be used to traverse dictionaries
  - Autocall may be turned on (i.e., x.meth means x.meth())
* var[], i.e., __getitem__.
* All the math operators, +, -, /, *, %
* Comparisons, ==, >, <, >=, <=, !=
* ``in`` and ``not in``
* not, and, or
* TRUE if COND else FALSE
* top-level functions passed in (no methods, no builtins)
* Literal numbers, strings, dictionaries, lists, tuples
"""

class SimpleEval(object):
    """
    Evaluator; subclass or instantiate to customize
    """

    autocall = False
    dict_attr = False

    def __init__(self, **kw):
        for name, value in kw.items():
            if not hasattr(self, name):
                raise TypeError(
                    "Unexpected keyword argument %s=%r" % (name, value))
            setattr(self, name, value)

    def __call__(self, source, globals=None, locals=None):
        pass
    
