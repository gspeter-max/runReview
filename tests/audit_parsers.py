import sys
import os
import time

# Ensure we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag.ingestion.parsers.python_parser import PythonParser
from app.rag.ingestion.parsers.javascript_parser import JavaScriptParser
from app.rag.ingestion.parsers.factory import ParserFactory
from app.rag.ingestion.parsers.base import ParsedStructure

def test_python_parser_robustness():
    print("Testing Python Parser Robustness...")
    parser = PythonParser()
    invalid_code = "def incomplete_func(\n    print('hello')"
    structures = parser.parse(invalid_code, "test.py")
    
    assert len(structures) == 1
    assert structures[0].kind == "module"
    print("  ✓ Gracefully fell back on syntax error.")

def test_python_parser_accuracy():
    print("Testing Python Parser Accuracy...")
    parser = PythonParser()
    code = '''
"""Module docstring."""
import os

@decorator1
@decorator2(arg=1)
class MyClass:
    """Class docstring."""
    def method1(self, x: int) -> str:
        """Method docstring."""
        return str(x)
    
    async def async_method(self):
        pass

def top_level_func():
    def nested_func():
        pass
    pass
'''
    structures = parser.parse(code, "test.py")
    
    # Check imports
    imports = [s for s in structures if s.kind == "import_block"]
    assert len(imports) == 1
    assert "import os" in imports[0].content

    # Check class
    classes = [s for s in structures if s.kind == "class"]
    assert len(classes) == 1
    assert classes[0].name == "MyClass"
    assert classes[0].docstring == "Class docstring."
    assert "decorator1" in classes[0].decorators
    assert "decorator2(arg=1)" in classes[0].decorators

    # Check methods
    methods = [s for s in structures if s.kind == "method"]
    assert len(methods) == 2
    assert any(m.name == "method1" and m.parent == "MyClass" for m in methods)
    assert any(m.name == "async_method" and m.parent == "MyClass" for m in methods)
    
    # Check top-level function
    funcs = [s for s in structures if s.kind == "function"]
    assert len(funcs) == 1
    assert funcs[0].name == "top_level_func"
    
    # Check nested function (Current implementation only iterates child nodes of module/class)
    # So nested_func should NOT be found as a separate structure by design (maybe?)
    # Let's see if it's found.
    assert not any(f.name == "nested_func" for f in funcs)
    print("  ✓ Accuracy looks good (nested functions are NOT extracted separately).")

def test_js_parser_robustness():
    print("Testing JS Parser Robustness...")
    parser = JavaScriptParser()
    # Mismatched braces
    code = "function test() { \n  if (true) { \n    return 1;" 
    structures = parser.parse(code, "test.js")
    # It should still find the function because it's regex-based
    assert any(s.name == "test" for s in structures)
    print("  ✓ Regex-based parsing is robust against syntax errors (but may have wrong boundaries).")

def test_js_parser_accuracy():
    print("Testing JS Parser Accuracy...")
    parser = JavaScriptParser()
    code = '''
export class MyClass {
  method1() {
    return 1;
  }
}

/** Function doc */
export async function myFunc(a, b) {
  return a + b;
}

const arrowFunc = (x) => {
  return x * 2;
};

interface MyInterface {
  id: string;
}

type MyType = string | number;

// Braces in comments { }
// Braces in strings " { "
function withBraces() {
  const s = "{";
  return s;
}
'''
    structures = parser.parse(code, "test.js")
    
    names = [s.name for s in structures]
    print(f"  Found: {names}")
    
    assert "MyClass" in names
    assert "myFunc" in names
    assert "arrowFunc" in names
    assert "MyInterface" in names
    assert "MyType" in names
    assert "withBraces" in names
    
    # Check if method1 was found
    assert "method1" in names
    
    # Check brace matching with strings
    with_braces = next(s for s in structures if s.name == "withBraces")
    # If brace matching failed, it might have cut off early or late
    assert "const s = \"{\";" in with_braces.content
    assert "return s;" in with_braces.content
    print("  ✓ Found major structures, but missed methods (due to lack of indentation support).")

def test_js_parser_performance():
    print("Testing JS Parser Performance...")
    parser = JavaScriptParser()
    # Large file with many functions
    num_funcs = 1000
    lines = []
    for i in range(num_funcs):
        lines.append(f"function func{i}() {{")
        lines.append(f"  console.log({i});")
        lines.append("}")
    
    content = "\n".join(lines)
    
    start_time = time.time()
    structures = parser.parse(content, "large.js")
    duration = time.time() - start_time
    
    print(f"  Parsed {len(structures)} structures in {duration:.4f}s")
    assert len(structures) == num_funcs
    
    # Test with very deep nesting (might be slow if brace matching is inefficient)
    nesting_level = 500
    nested_lines = []
    for i in range(nesting_level):
        nested_lines.append(" " * i + "if (true) {")
    nested_lines.append(" " * nesting_level + "console.log('deep');")
    for i in range(nesting_level - 1, -1, -1):
        nested_lines.append(" " * i + "}")
    
    nested_content = "function deep() {\n" + "\n".join(nested_lines) + "\n}"
    
    start_time = time.time()
    structures = parser.parse(nested_content, "deep.js")
    duration = time.time() - start_time
    print(f"  Parsed deep nesting in {duration:.4f}s")

def test_parser_factory():
    print("Testing Parser Factory...")
    py_parser = ParserFactory.get_parser("python")
    assert isinstance(py_parser, PythonParser)
    
    js_parser = ParserFactory.get_parser("javascript")
    assert isinstance(js_parser, JavaScriptParser)
    
    ts_parser = ParserFactory.get_parser("typescript")
    assert isinstance(ts_parser, JavaScriptParser)
    
    unknown_parser = ParserFactory.get_parser("cobol")
    from app.rag.ingestion.parsers.generic_parser import GenericParser
    assert isinstance(unknown_parser, GenericParser)
    print("  ✓ Factory correctly identifies and fallbacks.")

if __name__ == "__main__":
    test_python_parser_robustness()
    test_python_parser_accuracy()
    test_js_parser_robustness()
    test_js_parser_accuracy()
    test_js_parser_performance()
    test_parser_factory()
