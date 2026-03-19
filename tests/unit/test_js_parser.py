from __future__ import annotations

import pytest
from app.rag.ingestion.parsers.javascript_parser import JavaScriptParser

class TestJavaScriptParser:
    def test_extracts_indented_methods(self):
        parser = JavaScriptParser()
        code = """
class MyClass {
  constructor() {
    this.value = 1;
  }

  method1() {
    return 1;
  }

  async method2() {
    return 2;
  }
}

function topLevel() {
  return 3;
}
"""
        structures = parser.parse(code, "test.js")
        names = [s.name for s in structures]
        
        assert "MyClass" in names
        assert "topLevel" in names
        # These are currently expected to FAIL before the fix
        assert "constructor" in names
        assert "method1" in names
        assert "method2" in names

    def test_extracts_indented_classes_and_functions(self):
        parser = JavaScriptParser()
        code = """
  class IndentedClass {
    method() {}
  }

  function indentedFunction() {
  }
"""
        structures = parser.parse(code, "test.js")
        names = [s.name for s in structures]
        
        assert "IndentedClass" in names
        assert "indentedFunction" in names
        assert "method" in names
