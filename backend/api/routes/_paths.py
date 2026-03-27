import os


def dataset_csv_path() -> str:
    # Resolve from this file so route handlers work from any launch directory.
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "dataset.csv"))
