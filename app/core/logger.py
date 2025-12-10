import logging

# Configure basic logging

logging.basicConfig(
  level=logging.INFO,
  format="[%(levelname)s] %(asctime)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
  datefmt="%Y-%m-%d %H:%M:%S",
)

# Create a logger instance

logger = logging.getLogger(__name__)