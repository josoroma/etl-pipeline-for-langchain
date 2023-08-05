LOG_LEVEL = "INFO"

DATA = {
    "URL": "https://github.com/hwchase17/langchain.git",
    "LAKE": "DATA_LAKE",
    "LOGS": "LOGS",
    "BACKUPS": "BACKUPS",
    "DATETIME": "%Y-%m-%d_%H:%M:%S",
}

ACTION = {
    "OK": "_OK_",
    "ERROR": "_ERROR_",
    "EXCEPTION": "_EXCEPTION_",
    "START": "_START_",
    "END": "_END_"
}

STAT = {
    "TOTAL_PROCESSED": "Total files processed: ",
    "TOTAL_OK": "Total files processed successfully: ",
    "TOTAL_ERROR": "Total files processed with errors: ",
    "TOTAL_EXCEPTION": "Total files processed with exceptions: ",
}
