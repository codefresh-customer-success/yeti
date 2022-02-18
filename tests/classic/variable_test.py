'''
    Variable class Testing
'''
from classic.variable import Variable
import pytest
from classic.exceptions import VariableSourceNotSupported

def test_variable_name_is_a_string():
    with pytest.raises(TypeError):
        Variable(23,0,"pipeline",1,"")

def test_variable_source_is_valid():
    with pytest.raises(VariableSourceNotSupported):
        Variable("var1",0,"unknown",1,"")

def test_normal_variable_creation():
    x=Variable("var1",0,"pipeline",1,'{{.Input.body.repository.owner.name}}')
    assert x.name == "var1"
    assert x.value == 0
    assert x.source == "pipeline"
    assert x.path == '{{.Input.body.repository.owner.name}}'