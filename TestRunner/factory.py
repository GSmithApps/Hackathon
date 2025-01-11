# TestRunner/factory.py

from pathlib import Path
from .models import QuestionAnswer
from Models.models import CorpusData
from TestRunner.test_runner import TestRunner

def create_test_runner(
    dataset_name: str,
    corpus: CorpusData,
    id_mapping: dict,
    embedding_path: str,
    embedding_time,
    config
) -> TestRunner:
    """
    Factory function to create a TestRunner instance.

    Args:
        dataset_name (str): The name of root folder of the data
        id_mapping (dict): Mapping of document IDs to embeddings.
        embedding_path (str): Path to embeddings.

    Returns:
        TestRunner: An initialized TestRunner instance.
    """
    splitting_method = config["splitting_method"]
    model_name = config["embedding_model"]
    question_answer = QuestionAnswer(dataset_name)
    return TestRunner(
        question_answer,
        corpus,
        id_mapping,
        embedding_path,
        splitting_method,
        embedding_time,
        model_name
    )
