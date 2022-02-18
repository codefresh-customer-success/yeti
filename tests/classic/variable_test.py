'''
    Variable class Testing
'''
from ..classic.variable import Variable
import pytest


def test_name_is_a_string():
    with pytest.raises(TypeError):
        x=Variable(23,0,"pipeline",1,"")