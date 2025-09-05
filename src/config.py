#!/usr/bin/env python3

# Default configuration values
DEFAULT_SETTINGS = {
    "readarr_address": "http://192.168.1.2:8787",
    "readarr_api_key": "",
    "request_timeout": 120.0,
    "libgen_address_v1_list": ["http://libgen.is", "http://libgen.rs"],
    "libgen_address_v2_list": ["http://libgen.li", "http://libgen.la"],
    "thread_limit": 1,
    "sleep_interval": 0,
    "library_scan_on_completion": True,
    "sync_schedule": [],
    "minimum_match_ratio": 90,
    "selected_language": "English",
    "selected_path_type": "file",
    "preferred_extensions_fiction": [".epub", ".mobi", ".azw3", ".djvu"],
    "preferred_extensions_non_fiction": [".pdf", ".epub", ".mobi", ".azw3", ".djvu"],
    "search_last_name_only": False,
    "search_shortened_title": False,
}

# File paths
DEFAULT_CONFIG_FOLDER = "config"
DEFAULT_DOWNLOAD_FOLDER = "downloads"
SETTINGS_CONFIG_FILE = "settings_config.json"

# Validation ranges
MIN_THREAD_LIMIT = 1
MAX_THREAD_LIMIT = 10
MIN_TIMEOUT = 1
MAX_TIMEOUT = 600
MIN_MATCH_RATIO = 0
MAX_MATCH_RATIO = 100
MIN_SLEEP_INTERVAL = 0

# Scheduler settings
SCHEDULER_CHECK_INTERVAL = 600  # 10 minutes
SCHEDULER_SLEEP_AFTER_SYNC = 3600  # 1 hour

# HTTP settings
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'BookBounty/1.0'
}

# File type validation
VALID_BOOK_EXTENSIONS = ['.epub', '.mobi', '.azw3', '.djvu', '.pdf', '.fb2', '.txt']

# Error messages
ERROR_MESSAGES = {
    'invalid_numeric': "Invalid numeric value for setting '{setting}': {value}",
    'out_of_range': "Value for setting '{setting}' is out of range ({min}-{max}): {value}",
    'missing_setting': "Missing required setting: {setting}",
    'invalid_boolean': "Invalid boolean value for setting '{setting}': {value}",
}

# Success messages
SUCCESS_MESSAGES = {
    'config_loaded': "Configuration loaded successfully",
    'config_saved': "Configuration saved successfully",
    'app_started': "BookBounty application started successfully",
}

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
