"""
Data ingestion layer: reads Excel/CSV/PDF files and normalizes them into
a small, predictable shape (`summarize_dataframe`) the rest of the pipeline
can rely on without knowing anything about the original file format.
"""
import logging

import pandas as pd
from pypdf import PdfReader

from app.core.exceptions import FileParsingError

logger = logging.getLogger(__name__)


def read_excel_file(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        logger.warning("Failed to read Excel file %s: %s", file_path, e)
        raise FileParsingError(f"Could not read this Excel file: {e}") from e


def read_csv_file(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        logger.warning("Failed to read CSV file %s: %s", file_path, e)
        raise FileParsingError(f"Could not read this CSV file: {e}") from e


def read_pdf_file(file_path: str) -> str:
    """Extract text from a PDF, page by page, with page markers. Returns '' if no text layer exists."""
    try:
        reader = PdfReader(file_path)
    except Exception as e:
        logger.warning("Failed to open PDF %s: %s", file_path, e)
        raise FileParsingError(f"Could not open this PDF: {e}") from e

    chunks = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            chunks.append(f"\n--- PAGE {page_num + 1} ---\n{text}")

    return "".join(chunks)


def summarize_dataframe(df: pd.DataFrame) -> dict:
    """
    Pull the numbers the rest of the app needs out of an uploaded ledger.
    The last numeric column is treated as the target metric (revenue, expense, etc.)
    -- this is a simplifying assumption, documented here rather than left implicit.
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not numeric_cols:
        return {
            "target_column": None,
            "total": 0.0,
            "row_count": len(df),
            "series": [],
            "preview_text": df.head(10).to_string(),
        }

    target_col = numeric_cols[-1]
    series = df[target_col].fillna(0).astype(float).tolist()

    return {
        "target_column": str(target_col),
        "total": float(df[target_col].sum()),
        "row_count": int(len(df)),
        "series": series,
        "preview_text": df.head(10).to_string(),
    }
