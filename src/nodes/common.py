
import time
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def timer(description):
    start = time.time()
    yield
    elapsed = time.time() - start
    logger.info(f"{description} took {elapsed:.2f} seconds")


def read_file(filename, default=""):
    try:
        with open(filename) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        return default


def extract_content_after_pattern(text):
    pattern = "\n</think>\n\n"
    position = text.find(pattern)
    if position == -1:
        return text
    return text[position + len(pattern):]


def with_live_callback(fn, live_callback=None):
    def wrapped(state):
        new_state = fn(state)
        if live_callback:
            live_callback(new_state.get("messages", []))
        return new_state
    return wrapped
