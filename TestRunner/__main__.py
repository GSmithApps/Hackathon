import itertools
import json
import hashlib
import argparse
import os
from .factory import create_test_runner
from factories.corpus_factory import create_corpus
from factories.embedding_generator_factory import create_embedding_generator
import spacy
from pathlib import Path
from .config import (
    NON_MUTUALLY_EXCLUSIVE_CONFIGS,
    DATASETS_PATH,
    HASH_RECORD_PATH,
    EMBEDDINGS_PATH
)


def load_configs(config_path="grid_search_config.json"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, config_path)
    with open(full_path, "r") as f:
        return json.load(f)


def powerset(iterable):
    """
    Generate all subsets of an iterable, including the empty set and full set.
    """
    s = list(iterable)
    return [
        list(subset)
        for subset in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(1, len(s) + 1)
        )
    ]


def generate_combinations(config_space):
    """
    Generate all combinations of configuration options,
    including multi-value attributes like splitting_method.
    """
    updated_config_space = {}

    for key, values in config_space.items():
        if (
            isinstance(values, list) and key in NON_MUTUALLY_EXCLUSIVE_CONFIGS
        ):  # Handle non-mutually exclusive case
            updated_config_space[key] = powerset(values)
        else:
            updated_config_space[key] = values

    keys, values = zip(*updated_config_space.items())
    return [dict(zip(keys, v)) for v in itertools.product(*values)]


def run_test(config, dataset_name):

    data_path = DATASETS_PATH / Path(dataset_name)
    corpus = create_corpus(data_path)
    embedding_identifier = generate_embedding_identifier(
        dataset_name,
        config
    )
    embedding_path = EMBEDDINGS_PATH / Path(embedding_identifier + ".ann")
    embedding_exists = check_if_embedding_exists(
        embedding_path
    )
    if embedding_exists:
        # TODO: gather id_mapping and metadata from previous run
        pass
    else:
        nlp = spacy.load("en_core_web_sm")
        eg = create_embedding_generator(
            corpus, dataset_name, nlp, config, embedding_path
        )
        id_mapping, embedding_time = eg.generate_embeddings()

    tr = create_test_runner(
        dataset_name,
        corpus,
        id_mapping,
        embedding_path,
        embedding_time,
        config,
    )
    tr.run_test()




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=["grid", "single"], default="grid", help="Run mode"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to specific config file for single run",
    )
    parser.add_argument(
        "--dataset-name",
        help="Name of dataset used for testing"
    )
    args = parser.parse_args()
# __init__(self, dataset_name, config_path="grid_search_config.json")
    dataset_name = args.dataset_name
    if args.mode == "grid":
        config_space = load_configs()
        configs = generate_combinations(config_space)
        for config in configs:
            run_test(config, dataset_name)
    elif args.mode == "single" and args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
        run_test(config, dataset_name)
    else:
        print("Invalid arguments. Use --help for details.")


if __name__ == "__main__":
    main()
