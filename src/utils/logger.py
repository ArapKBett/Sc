import logging

def setup_logger():
    """Configure and return a logger."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cybersecurity-bot.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger()
