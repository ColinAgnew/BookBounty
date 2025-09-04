#!/usr/bin/env python3
"""
Utility functions for book searching to reduce code duplication
"""

from thefuzz import fuzz
import re


class SearchUtils:
    """Helper class containing common search functionality"""
    
    @staticmethod
    def compare_author_names(author1, author2):
        """
        Compare two author names using fuzzy matching after preprocessing
        
        Args:
            author1 (str): First author name
            author2 (str): Second author name
            
        Returns:
            int: Match ratio (0-100)
        """
        try:
            processed_author1 = SearchUtils.preprocess_name(author1)
            processed_author2 = SearchUtils.preprocess_name(author2)
            return fuzz.ratio(processed_author1, processed_author2)
        except Exception:
            return 0
    
    @staticmethod
    def preprocess_name(name):
        """
        Preprocess a name for comparison by normalizing it
        
        Args:
            name (str): Name to preprocess
            
        Returns:
            str: Normalized name
        """
        if not name:
            return ""
        
        # Replace punctuation with spaces and normalize
        name_string = name.replace(".", " ").replace(":", " ").replace(",", " ")
        new_string = "".join(e for e in name_string if e.isalnum() or e.isspace()).lower()
        words = new_string.split()
        words.sort()
        return " ".join(words)
    
    @staticmethod
    def clean_filename(filename):
        """
        Clean a filename for filesystem safety
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Cleaned filename
        """
        if not filename:
            return "Unknown"
        
        # Remove/replace problematic characters
        cleaned = re.sub(r'[\\*?:"<>|]', " - ", filename.replace("/", "+").strip())
        # Normalize multiple spaces
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        
        return cleaned if cleaned else "Unknown"
    
    @staticmethod
    def extract_cell_text(cells, index, default=""):
        """
        Safely extract text from HTML table cells
        
        Args:
            cells: List of table cells
            index (int): Index of cell to extract
            default (str): Default value if extraction fails
            
        Returns:
            str: Extracted text or default value
        """
        try:
            return cells[index].get_text().strip()
        except (AttributeError, IndexError):
            return default
    
    @staticmethod
    def get_search_text(title, use_shortened=False):
        """
        Get search text for a book title
        
        Args:
            title (str): Original title
            use_shortened (bool): Whether to use shortened title (text before ':')
            
        Returns:
            str: Search text
        """
        if not title:
            return ""
        
        return title.split(":")[0] if use_shortened and ":" in title else title
    
    @staticmethod
    def get_author_search_text(author, use_last_name_only=False):
        """
        Get search text for an author name
        
        Args:
            author (str): Full author name
            use_last_name_only (bool): Whether to use only the last name
            
        Returns:
            str: Author search text
        """
        if not author:
            return ""
        
        if use_last_name_only:
            parts = author.split()
            return parts[-1] if parts else author
        
        return author
    
    @staticmethod
    def check_file_type_match(file_type, preferred_extensions):
        """
        Check if a file type matches preferred extensions
        
        Args:
            file_type (str): File type to check
            preferred_extensions (list): List of preferred extensions
            
        Returns:
            bool: True if file type matches preferences
        """
        if not file_type or not preferred_extensions:
            return False
        
        file_type_lower = file_type.lower()
        return any(ext.replace(".", "").lower() in file_type_lower for ext in preferred_extensions)
    
    @staticmethod
    def check_language_match(language, allowed_languages, default_language="all"):
        """
        Check if a language matches allowed languages
        
        Args:
            language (str): Language to check
            allowed_languages (list): List of allowed languages
            default_language (str): Default language setting
            
        Returns:
            bool: True if language is allowed
        """
        if not language or not allowed_languages:
            return default_language.lower() == "all"
        
        language_lower = language.lower()
        return (language_lower in [lang.lower() for lang in allowed_languages] or 
                default_language.lower() == "all")