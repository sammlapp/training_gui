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


def query_hoplite(files, model, db, audio_root, num_results):
    # TODO: should be able to specify file/start time pairs
    results = {}
    for file in files:
        results[file] = model.similarity_search_hoplite_db(
            files[0], db=db, audio_root=audio_root, num_results=num_results
        )
    return results


def main():
    parser = argparse.ArgumentParser(description="Query hoplite database")
    parser.add_argument(
        "--config", required=True, help="Path to inference configuration file"
    )
    args = parser.parse_args()

    # Load configuration from file
    config_data = load_config_file(args.config, logger=logger)

    try:

        query_hoplite(files, model, db, audio_root, num_results)
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    main()
