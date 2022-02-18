'''
    Variable class Testing
'''
import pytest
from classic.variable   import Variable
from classic.exceptions import VariableSourceNotSupported

def test_variable_name_is_a_string():
    '''Testing variable name is a string'''
    with pytest.raises(TypeError):
        Variable(23,0,"pipeline",1,"")

def test_variable_source_is_valid():
    '''Testing variable source is supported'''
    with pytest.raises(VariableSourceNotSupported):
        Variable("var1",0,"unknown",1,"")

def test_normal_variable_creation():
    '''Testing basic creation of a Variable'''
    x=Variable("var1",0,"pipeline",1,'{{.Input.body.repository.owner.name}}')
    assert x.name == "var1"
    assert x.value == 0
    assert x.source == "pipeline"
    assert x.path == '{{.Input.body.repository.owner.name}}'