from npdoc_to_md import render_md_from_obj_docstring


# # Test a function with an empty docstring

def test_empty_func():
    assert render_md_from_obj_docstring(obj=lambda x: x, obj_namespace='test') == '**<span style="color:purple">test</span>_(x)_**'
