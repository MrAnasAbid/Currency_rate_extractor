import logging

def get_classic_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set to DEBUG for more detailed output

    # Create handlers
    file_handler = logging.FileHandler("currency_rate_extractor.log")
    stream_handler = logging.StreamHandler()

    # Create a formatter and set it for the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
