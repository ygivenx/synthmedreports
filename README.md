# SynthMedReports

SynthMedReports is a highly customizable Python package for generating synthetic medical report CSV files. With a flexible JSON configuration file validated by Pydantic, you can define arbitrary columns (e.g., sequence IDs, enums, integers, dates, and synthetic text) and control every aspect of the generated data—from the text report structure to vocabulary phrases and event injection. Optionally, the package can be extended to run as a web service using FastAPI and Uvicorn.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
  - [Column Types](#column-types)
  - [Vocabulary Configuration](#vocabulary-configuration)
- [Usage](#usage)
  - [Command-Line Interface](#command-line-interface)
  - [Example Configuration File](#example-configuration-file)
- [Troubleshooting and Support](#troubleshooting-and-support)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Customizable Columns:**  
  Define arbitrary CSV columns with types such as:
  - **Sequence:** Auto-incrementing IDs with optional prefix and zero-padding.
  - **Enum:** Randomly selected values from a predefined list.
  - **Int:** Random integers within a range.
  - **Date:** Random dates generated within a given period.
  - **Text:** Synthetic text reports with structured sections.
  
- **Report Types:**  
  Generate synthetic text reports mimicking:
  - **Radiology** (e.g., Technique, Findings, Conclusion)
  - **Pathology** (e.g., Gross Description, Microscopic Description, Diagnosis)
  - **Clindoc** (e.g., History, Examination, Plan)

- **Custom Vocabulary:**  
  Move the vocabulary phrases (for radiology, pathology, and clindoc) into the configuration file for full control over the language used in the generated reports.

- **Event Keyword Injection:**  
  Inject event-specific keywords (e.g., related to deep vein thromboembolism) into text reports at a configurable rate.

- **CLI & API:**  
  Use a command-line interface for generating CSV files, or extend the package to expose a web API with FastAPI and Uvicorn.

- **Pydantic Configuration:**  
  Validate configuration files using Pydantic to ensure that user inputs are correct and complete.

## Installation

Clone or download the repository, then navigate to the root folder (where `setup.py` is located) and install using pip:

```bash
pip install .
```

This installs the package and registers the command-line entry point generate_reports.

### Quick Start
Create a JSON Configuration File
Create a configuration file (for example, config_default.json) that defines the number of records, columns, vocabulary, and report settings.

Run the CLI Command

Generate the CSV file with the command:

```generate_reports --config config_default.json```

Configuration
The package is configured using a JSON file that is validated by Pydantic. The configuration file includes sections for:

```
General Settings: Number of records and output CSV filename.
Columns: An array of column definitions. Each column is defined by its type and properties.
Vocabulary: Lists of phrases for each report type used to generate synthetic text.
Column Types
SequenceColumn
name: Column name.
type: Must be "sequence".
prefix: (Optional) A string prefix (e.g., "P" for patient IDs).
pad: (Optional) Minimum width for the numeric part, zero-padded.
start: Starting number (default is 1).
increment: Step size between values.
EnumColumn
name: Column name.
type: Must be "enum".
values: List of possible values; one is chosen randomly for each record.
IntColumn
name: Column name.
type: Must be "int".
min: Minimum integer value.
max: Maximum integer value.
DateColumn
name: Column name.
type: Must be "date".
start: Start date (ISO format, e.g., "2020-01-01").
end: End date (ISO format, e.g., "2022-12-31").
TextColumn
name: Column name.
type: Must be "text".
injection_rate: Probability (0.0–1.0) of injecting an event keyword.
event_keywords: List of keywords (e.g., related to DVT) to inject.
radiology, pathology, clindoc:
Define structured report sections (each section is configured with a minimum and maximum number of phrases).
date_range: A date range used within text reports if needed.
allowed_report_types: List of report types (e.g., ["radiology", "pathology", "clindoc"]).
Vocabulary Configuration
The vocabulary (phrases used to generate text reports) is defined under a top-level vocab key:

radiology: List of phrases for radiology reports.
pathology: List of phrases for pathology reports.
clindoc: List of phrases for clinical documents.
```

### Usage
Command-Line Interface
After installation, you can generate a CSV file by running:

```bash
generate_reports --config config_default.json
```

CLI Options
--config: (Required) Path to your JSON configuration file.
--num_records: Override the number of records defined in the configuration.
--output_csv: Override the output CSV file name defined in the configuration.
For example, to generate 50 records in a file named my_output.csv:

```bash
generate_reports --config config_default.json --num_records 50 --output_csv my_output.csv
```

Example Configuration File
Below is an example configuration file (config_default.json):

```json
{
  "num_records": 100,
  "output_csv": "output.csv",
  "columns": [
    {
      "name": "patient_id",
      "type": "sequence",
      "prefix": "P",
      "pad": 3,
      "start": 1,
      "increment": 1
    },
    {
      "name": "text_id",
      "type": "sequence",
      "prefix": "T",
      "pad": 5,
      "start": 1,
      "increment": 1
    },
    {
      "name": "text_date",
      "type": "date",
      "start": "2020-01-01",
      "end": "2022-12-31"
    },
    {
      "name": "text",
      "type": "text",
      "injection_rate": 0.1,
      "event_keywords": ["DVT", "thrombosis", "venous thromboembolism", "embolism", "clot"],
      "radiology": {
        "technique": {"min_phrases": 3, "max_phrases": 6},
        "findings": {"min_phrases": 6, "max_phrases": 12},
        "conclusion": {"min_phrases": 3, "max_phrases": 6}
      },
      "pathology": {
        "gross_desc": {"min_phrases": 3, "max_phrases": 6},
        "micro_desc": {"min_phrases": 6, "max_phrases": 12},
        "diagnosis": {"min_phrases": 3, "max_phrases": 6}
      },
      "clindoc": {
        "history": {"min_phrases": 4, "max_phrases": 8},
        "examination": {"min_phrases": 4, "max_phrases": 8},
        "plan": {"min_phrases": 4, "max_phrases": 8}
      },
      "date_range": {"start": "2020-01-01", "end": "2022-12-31"},
      "allowed_report_types": ["radiology", "pathology", "clindoc"]
    },
    {
      "name": "text_tag_1",
      "type": "enum",
      "values": ["radiology", "pathology", "clindoc"]
    }
  ],
  "vocab": {
    "radiology": [
      "CT scan", "MRI", "ultrasound", "contrast enhancement", "lesion", "nodule", "mass",
      "calcification", "spiculated margins", "infiltrative pattern", "peripheral", "central",
      "no evidence of metastasis", "pulmonary", "liver", "bone", "soft tissue", "impression",
      "staging", "axial images"
    ],
    "pathology": [
      "malignant", "benign", "carcinoma", "adenocarcinoma", "invasive", "neoplastic", "biopsy",
      "histology", "cytology", "cellular atypia", "mitotic figures", "grade III", "necrosis",
      "frozen section", "immunohistochemistry", "specimen", "resection", "tumor", "infiltration",
      "margins"
    ],
    "clindoc": [
      "chemotherapy", "radiation therapy", "surgery", "palliative care", "diagnosis", "follow-up",
      "patient history", "progress note", "physical examination", "symptom management", "pain",
      "nausea", "fatigue", "oncology", "stage IV", "adjuvant", "treatment plan", "clinical findings",
      "laboratory results", "vitals"
    ]
  }
}
```

### Troubleshooting and Support
- Installation Issues:
  Ensure you have installed all dependencies: numpy, pydantic  

- Configuration Errors:
  Verify that your JSON configuration file is valid and follows the schema outlined above. Pydantic will report validation errors if any required field is missing or invalid.

- Pydantic Validation:
  If you encounter errors related to configuration, refer to the Pydantic documentation for guidance on schema definitions.

### General Support:
For further assistance, consider opening an issue in the project's repository.

### Contributing
Contributions, improvements, and bug reports are welcome! Please fork the repository, submit your changes, and create a pull request with detailed information about your changes.

### License
This project is licensed under the MIT License. See the LICENSE file for details.
