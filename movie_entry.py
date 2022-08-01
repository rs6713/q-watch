import logging
from qwatch.gui import MovieWindow

import warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger("qwatch")
loglvl = logging.INFO

logger.setLevel(loglvl)
ch = logging.StreamHandler()
ch.setLevel(loglvl)
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s'
)
ch.setFormatter(formatter)
logger.addHandler(ch)

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s | %(levelname)s | %(funcName)s | %(message)s',
#     handlers=[logging.StreamHandler()],
#     datefmt="%Y-%m-%d %H:%M:%S",
# )
# logger = logging.getLogger(__name__)


MovieWindow()
