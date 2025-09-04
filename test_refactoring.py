#!/usr/bin/env python3
"""
Basic tests for search utilities to ensure refactoring is working correctly
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from search_utils import SearchUtils


def run_all_tests():
    """Run all tests"""
    print("Running basic tests for search utilities...")
    try:
        # Test author name comparison
        result = SearchUtils.compare_author_names("John Smith", "John Smith")
        assert result == 100
        
        # Test name preprocessing
        result = SearchUtils.preprocess_name("J.K. Rowling")
        assert isinstance(result, str)
        assert "j" in result.lower()
        
        # Test filename cleaning
        result = SearchUtils.clean_filename("Test: Book")
        assert "Test" in result
        
        # Test search text functions
        result = SearchUtils.get_search_text("Book: Subtitle", True)
        assert result == "Book"
        
        result = SearchUtils.get_author_search_text("John Smith", True)
        assert result == "Smith"
        
        # Test check functions
        result = SearchUtils.check_file_type_match("epub", [".epub", ".pdf"])
        assert result == True
        
        result = SearchUtils.check_language_match("english", ["english", "french"])
        assert result == True
        
        print("✅ All tests passed! Refactoring is working correctly.")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)