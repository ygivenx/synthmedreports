import csv
import os
import random
import datetime
import json
import argparse
from typing import List, Union, Dict, Literal
import numpy as np
import pandas as pd
from pydantic import BaseModel

# ---------------- Pydantic Models for Column Configurations ----------------


class SequenceColumn(BaseModel):
    name: str
    type: Literal["sequence"] = "sequence"
    prefix: str = ""
    pad: int = 0
    start: int = 1
    increment: int = 1


class EnumColumn(BaseModel):
    name: str
    type: Literal["enum"] = "enum"
    values: List[str]


class IntColumn(BaseModel):
    name: str
    type: Literal["int"] = "int"
    min: int
    max: int


class DateColumn(BaseModel):
    name: str
    type: Literal["date"] = "date"
    start: str  # ISO date string, e.g. "2020-01-01"
    end: str  # ISO date string, e.g. "2022-12-31"


# For generating synthetic text reports, we allow per‐section configuration.
class TextReportConfig(BaseModel):
    min_phrases: int
    max_phrases: int


class TextColumn(BaseModel):
    name: str
    type: Literal["text"] = "text"
    injection_rate: float = 0.1
    event_keywords: List[str] = [
        "DVT",
        "thrombosis",
        "venous thromboembolism",
        "embolism",
        "clot",
    ]
    # Report-type–specific configuration: for each report type, define the sections and their phrase count ranges.
    radiology: Dict[str, TextReportConfig]
    pathology: Dict[str, TextReportConfig]
    clindoc: Dict[str, TextReportConfig]
    # A date range used if needed in the text generation (for example, if you wish to embed a date)
    date_range: Dict[str, str] = {"start": "2020-01-01", "end": "2022-12-31"}
    allowed_report_types: List[str] = ["radiology", "pathology", "clindoc"]
    report_percentages: Dict[str, float] = {
        "radiology": 40,
        "pathology": 30,
        "clindoc": 30,
    }


# A union of all possible column types.
ColumnConfig = Union[SequenceColumn, EnumColumn, IntColumn, DateColumn, TextColumn]


# New model for Vocabulary
class VocabModel(BaseModel):
    radiology: List[str]
    pathology: List[str]
    clindoc: List[str]


# ---------------- Updated Top-level Configuration ----------------
class ConfigModel(BaseModel):
    num_patients: int = 100
    avg_notes_per_patient: int = 5
    output_csv: str = "output.csv"
    columns: List[ColumnConfig]
    vocab: VocabModel


# ---------------- Helper Functions for Text Generation ----------------


def generate_section_text(
    section_title: str,
    min_phrases: int,
    max_phrases: int,
    vocab_list: List[str],
    injection_rate: float,
    keywords: List[str],
) -> str:
    """
    Generate a section with a header and a sentence composed of randomly chosen phrases.
    With probability injection_rate, one or more keywords are inserted.
    """
    num_phrases = random.randint(min_phrases, max_phrases)
    phrases = [random.choice(vocab_list) for _ in range(num_phrases)]
    section_text = " ".join(phrases)

    if random.random() < injection_rate:
        num_injections = random.randint(1, len(keywords))
        keywords_to_inject = random.sample(keywords, num_injections)
        words = section_text.split()
        for kw in keywords_to_inject:
            insert_index = random.randint(0, len(words))
            words.insert(insert_index, kw)
        section_text = " ".join(words)

    return f"{section_title}: {section_text}."


def generate_radiology_text(text_config: TextColumn, phrases: List[str]) -> str:
    cfg = text_config.radiology
    technique = generate_section_text(
        "Technique",
        cfg["technique"].min_phrases,
        cfg["technique"].max_phrases,
        phrases,
        text_config.injection_rate,
        text_config.event_keywords,
    )
    findings = generate_section_text(
        "Findings",
        cfg["findings"].min_phrases,
        cfg["findings"].max_phrases,
        phrases,
        text_config.injection_rate,
        text_config.event_keywords,
    )
    conclusion = generate_section_text(
        "Conclusion",
        cfg["conclusion"].min_phrases,
        cfg["conclusion"].max_phrases,
        phrases,
        text_config.injection_rate,
        text_config.event_keywords,
    )
    return "\n".join([technique, findings, conclusion])


def generate_pathology_text(text_config: TextColumn, phrases: List[str]) -> str:
    cfg = text_config.pathology
    gross_desc = generate_section_text(
        "Gross Description",
        cfg["gross_desc"].min_phrases,
        cfg["gross_desc"].max_phrases,
        phrases,
        text_config.injection_rate,
        text_config.event_keywords,
    )
    micro_desc = generate_section_text(
        "Microscopic Description",
        cfg["micro_desc"].min_phrases,
        cfg["micro_desc"].max_phrases,
        phrases,
        text_config.injection_rate,
        text_config.event_keywords,
    )
    diagnosis = generate_section_text(
        "Diagnosis",
        cfg["diagnosis"].min_phrases,
        cfg["diagnosis"].max_phrases,
        phrases,
        text_config.injection_rate,
        text_config.event_keywords,
    )
    return "\n".join([gross_desc, micro_desc, diagnosis])


def generate_clindoc_text(text_config: TextColumn, phrases: List[str]) -> str:
    cfg = text_config.clindoc
    history = generate_section_text(
        "History",
        cfg["history"].min_phrases,
        cfg["history"].max_phrases,
        phrases,
        text_config.injection_rate,
        text_config.event_keywords,
    )
    examination = generate_section_text(
        "Examination",
        cfg["examination"].min_phrases,
        cfg["examination"].max_phrases,
        phrases,
        text_config.injection_rate,
        text_config.event_keywords,
    )
    plan = generate_section_text(
        "Plan",
        cfg["plan"].min_phrases,
        cfg["plan"].max_phrases,
        phrases,
        text_config.injection_rate,
        text_config.event_keywords,
    )
    return "\n".join([history, examination, plan])


def generate_text_value(text_config: TextColumn, vocab: VocabModel) -> str:
    if text_config.report_percentages:
        report_type = random.choices(
            list(text_config.report_percentages.keys()),
            weights=list(text_config.report_percentages.values()),
            k=1,
        )[0]
    else:
        report_type = random.choice(text_config.allowed_report_types)
    if report_type == "radiology":
        return generate_radiology_text(text_config, vocab.radiology)
    elif report_type == "pathology":
        return generate_pathology_text(text_config, vocab.pathology)
    elif report_type == "clindoc":
        return generate_clindoc_text(text_config, vocab.clindoc)
    else:
        return generate_clindoc_text(text_config, vocab.clindoc)


def generate_random_date(start_date_str: str, end_date_str: str) -> str:
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + datetime.timedelta(days=random_days)).isoformat()


# ---------------- Column Value Generator ----------------
def generate_value(
    col: ColumnConfig, state: Dict[str, int], vocab: VocabModel
) -> Union[str, int]:
    if isinstance(col, SequenceColumn):
        current = state.get(col.name, col.start)
        formatted = (
            f"{col.prefix}{str(current).zfill(col.pad)}"
            if col.pad > 0
            else f"{col.prefix}{current}"
        )
        state[col.name] = current + col.increment
        return formatted

    elif isinstance(col, EnumColumn):
        return random.choice(col.values)

    elif isinstance(col, IntColumn):
        return random.randint(col.min, col.max)

    elif isinstance(col, DateColumn):
        return generate_random_date(col.start, col.end)

    elif isinstance(col, TextColumn):
        return generate_text_value(col, vocab)

    else:
        return ""


# ---------------- Configuration Loading ----------------
def load_config(config_path: str) -> ConfigModel:
    with open(config_path, "r") as f:
        raw = json.load(f)
    return ConfigModel.model_validate(raw)


# ---------------- MAIN FUNCTION ----------------
def main():
    parser = argparse.ArgumentParser(
        description="Generate a CSV file with synthetic medical report data."
    )
    parser.add_argument(
        "--config", type=str, help="Path to JSON config file.", required=True
    )
    parser.add_argument(
        "--num_patients", type=int, help="Override number of patients.", default=None
    )
    parser.add_argument(
        "--avg_notes_per_patient",
        type=int,
        help="Override average notes per patient.",
        default=None,
    )
    parser.add_argument(
        "--output_csv", type=str, help="Override output CSV file name.", default=None
    )
    args = parser.parse_args()

    config = load_config(args.config)
    if args.num_patients is not None:
        config.num_patients = args.num_patients
    if args.avg_notes_per_patient is not None:
        config.avg_notes_per_patient = args.avg_notes_per_patient
    if args.output_csv is not None:
        config.output_csv = args.output_csv

    seq_state = {}
    records = []

    # Loop over patients and generate notes per patient based on a Poisson distribution
    for _ in range(config.num_patients):
        # Generate patient-level values (e.g., patient_id)
        patient_record = {}
        for col in config.columns:
            if col.name == "patient_id":
                patient_record["patient_id"] = generate_value(
                    col, seq_state, config.vocab
                )
        # Determine number of notes for this patient (at least one note)
        num_notes = max(1, np.random.poisson(config.avg_notes_per_patient))
        for _ in range(num_notes):
            record = {}
            for col in config.columns:
                if col.name == "patient_id":
                    record["patient_id"] = patient_record["patient_id"]
                else:
                    record[col.name] = generate_value(col, seq_state, config.vocab)
            records.append(record)

    # Determine output format based on file extension.
    output_file = config.output_csv
    ext = os.path.splitext(output_file)[1].lower()
    if ext == ".parquet":
        df = pd.DataFrame(records)
        df.to_parquet(output_file, index=False)
        print(
            f"Parquet file '{output_file}' generated with data for {config.num_patients} patients."
        )
    else:
        header = [col.name for col in config.columns]
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            for rec in records:
                writer.writerow(rec)
        print(
            f"CSV file '{output_file}' generated with data for {config.num_patients} patients."
        )


if __name__ == "__main__":
    main()
