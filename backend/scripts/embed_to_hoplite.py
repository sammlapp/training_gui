import argparse
import logging
import sys
from file_selection import resolve_files_from_config
import numpy as np

# local imports
from load_model import load_model
from config_utils import load_config_file
from hoplite_utils import load_or_create_db
from train_utils import process_fully_annotated_files, process_single_class_annotations

# hard coding some parameters
batch_size = 128
num_workers = 0

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# for hoplite operations, should we start a background server that is persistent, so that user can quickly
# run queries/train classifiers/etc rather than just do big slow jobs?
# eg it would only need to load the model once, and keep the db connection open
