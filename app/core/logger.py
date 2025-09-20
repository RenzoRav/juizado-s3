import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)


formatter = logging.Formatter(
    "%(levelname)s - %(name)s - %(message)s"
)
handler.setFormatter(formatter)


logger.addHandler(handler)

logger.propagate = False
