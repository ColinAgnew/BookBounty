#!/usr/bin/env python3


from thefuzz import fuzz
import re


class SearchUtils:
    
    @staticmethod
    def compare_author_names(author1, author2):
        try:
            processed_author1 = SearchUtils.preprocess_name(author1)
            processed_author2 = SearchUtils.preprocess_name(author2)
            return fuzz.ratio(processed_author1, processed_author2)
        except Exception:
            return 0
    
    @staticmethod
    def preprocess_name(name):
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
        if not filename:
            return "Unknown"
        
        # Remove/replace problematic characters
        cleaned = re.sub(r'[\\*?:"<>|]', " - ", filename.replace("/", "+").strip())
        # Normalize multiple spaces
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        
        return cleaned if cleaned else "Unknown"
    
    @staticmethod
    def extract_cell_text(cells, index, default=""):
        try:
            return cells[index].get_text().strip()
        except (AttributeError, IndexError):
            return default
    
    @staticmethod
    def get_search_text(title, use_shortened=False):
        if not title:
           return ""
        
        return title.split(":")[0] if use_shortened and ":" in title else title
    
    @staticmethod
    def get_author_search_text(author, use_last_name_only=False):
        if not author:
            return ""
        
        if use_last_name_only:
            parts = author.split()
            return parts[-1] if parts else author
        
        return author
    
    @staticmethod
    def check_file_type_match(file_type, preferred_extensions):
        if not file_type or not preferred_extensions:
            return False
        
        file_type_lower = file_type.lower()
        return any(ext.replace(".", "").lower() in file_type_lower for ext in preferred_extensions)
    
    @staticmethod
    def check_language_match(language, allowed_languages, default_language="all"):
        if not language or not allowed_languages:
            return default_language.lower() == "all"
        
        language_lower = language.lower()
        return (language_lower in [lang.lower() for lang in allowed_languages] or 
                default_language.lower() == "all")
