"""
Dataset validation service.

This module validates the curated sports knowledge base before ingestion
into ChromaDB. It performs:

- JSON parsing
- Schema validation (Pydantic)
- Business rule validation
- Duplicate detection
- Dataset integrity checks

The validator aggregates all errors and reports them together instead of
failing on the first invalid record.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from src.constants import (
    REQUIRED_RECORD_FIELDS,
    SUPPORTED_DIFFICULTIES,
    SUPPORTED_QUESTION_TYPES,
    SUPPORTED_SPORTS,
    MIN_CONTENT_LENGTH,
    MAX_CONTENT_LENGTH,
    MIN_KEYWORDS,
    MAX_KEYWORDS,
)

from src.exceptions import DatasetValidationError
from src.logger import logger, log_execution_time
from src.models import SportsKnowledge


class DatasetValidator:
    """
    Validates the sports knowledge dataset before ingestion.
    """

    def __init__(self) -> None:
        self.errors: list[str] = []

        self.records: list[SportsKnowledge] = []

        self._id_index: dict[str, str] = {}

        self._title_index: dict[str, str] = {}

        self.files_scanned: int = 0

    # ======================================================
    # Public API
    # ======================================================

    @log_execution_time("Dataset Validation")
    def load_and_validate(
        self,
        dataset_directory: str | Path,
    ) -> list[SportsKnowledge]:
        """
        Load every JSON file from a directory and validate them.

        Parameters
        ----------
        dataset_directory:
            Directory containing sports JSON files.

        Returns
        -------
        list[SportsKnowledge]

        Raises
        ------
        DatasetValidationError
            If one or more validation errors are found.
        """

        dataset_directory = Path(dataset_directory)

        if not dataset_directory.exists():
            raise DatasetValidationError(
                f"Dataset directory does not exist: {dataset_directory}"
            )

        if not dataset_directory.is_dir():
            raise DatasetValidationError(
                f"Expected directory: {dataset_directory}"
            )

        logger.info(
            f"Scanning dataset directory: {dataset_directory}"
        )

        json_files = sorted(dataset_directory.glob("*.json"))

        if not json_files:
            raise DatasetValidationError(
                "No JSON files found."
            )

        for file_path in json_files:
            self._load_file(file_path)

        self._validate_duplicates()

        if self.errors:

            self.summary()

            raise DatasetValidationError(
                "\n".join(self.errors)
            )

        logger.success(
            f"Validation successful "
            f"({len(self.records)} records)"
        )

        return self.records

    # ======================================================
    # Loading
    # ======================================================

    def _load_file(
        self,
        file_path: Path,
    ) -> None:
        """
        Load a single JSON file.
        """

        logger.info(f"Loading {file_path.name}")

        self.files_scanned += 1

        try:

            with file_path.open(
                "r",
                encoding="utf-8",
            ) as fp:

                data = json.load(fp)

        except json.JSONDecodeError as exc:

            self.errors.append(
                f"{file_path.name}: invalid JSON ({exc})"
            )

            return

        if not isinstance(data, list):

            self.errors.append(
                f"{file_path.name}: root must be a JSON array."
            )

            return

        if not data:

            self.errors.append(
                f"{file_path.name}: file is empty."
            )

            return

        logger.info(
            f"{file_path.name}: {len(data)} record(s)"
        )

        for record in data:

            self._validate_record(
                record=record,
                filename=file_path.name,
            )


    # ======================================================
    # Record Validation
    # ======================================================

    def _validate_record(
        self,
        record: dict[str, Any],
        filename: str,
    ) -> None:
        """
        Validate a single knowledge record.
        """

        if not isinstance(record, dict):
            self.errors.append(
                f"{filename}: record must be a JSON object."
            )
            return

        self._validate_required_fields(record, filename)

        try:
            knowledge = SportsKnowledge.model_validate(record)

        except PydanticValidationError as exc:

            self.errors.append(
                f"{filename}: schema validation failed\n{exc}"
            )

            return

        self._validate_sport(knowledge, filename)

        self._validate_difficulty(knowledge, filename)

        self._validate_question_types(knowledge, filename)

        self._validate_keywords(knowledge, filename)

        self._validate_content(knowledge, filename)

        self._validate_source(knowledge, filename)

        self.records.append(knowledge)

        self._track_duplicates(
            knowledge=knowledge,
            filename=filename,
        )

    # ======================================================
    # Required Fields
    # ======================================================

    def _validate_required_fields(
        self,
        record: dict[str, Any],
        filename: str,
    ) -> None:

        missing = REQUIRED_RECORD_FIELDS - set(record.keys())

        if missing:

            self.errors.append(
                f"{filename}: missing fields -> "
                f"{', '.join(sorted(missing))}"
            )

    # ======================================================
    # Sport
    # ======================================================

    def _validate_sport(
        self,
        record: SportsKnowledge,
        filename: str,
    ) -> None:

        if record.sport not in SUPPORTED_SPORTS:

            self.errors.append(
                f"{filename}: "
                f"{record.id} "
                f"invalid sport "
                f"'{record.sport}'"
            )

    # ======================================================
    # Difficulty
    # ======================================================

    def _validate_difficulty(
        self,
        record: SportsKnowledge,
        filename: str,
    ) -> None:

        for difficulty in record.difficulty:

            if difficulty not in SUPPORTED_DIFFICULTIES:

                self.errors.append(
                    f"{filename}: "
                    f"{record.id} "
                    f"invalid difficulty "
                    f"'{difficulty}'"
                )

    # ======================================================
    # Question Types
    # ======================================================

    def _validate_question_types(
        self,
        record: SportsKnowledge,
        filename: str,
    ) -> None:

        for question_type in record.question_types:

            if question_type not in SUPPORTED_QUESTION_TYPES:

                self.errors.append(
                    f"{filename}: "
                    f"{record.id} "
                    f"invalid question type "
                    f"'{question_type}'"
                )

    # ======================================================
    # Keywords
    # ======================================================

    def _validate_keywords(
        self,
        record: SportsKnowledge,
        filename: str,
    ) -> None:

        keywords = record.keywords

        if len(keywords) < MIN_KEYWORDS:

            self.errors.append(
                f"{filename}: "
                f"{record.id} "
                f"requires at least "
                f"{MIN_KEYWORDS} keywords."
            )

        if len(keywords) > MAX_KEYWORDS:

            self.errors.append(
                f"{filename}: "
                f"{record.id} "
                f"contains more than "
                f"{MAX_KEYWORDS} keywords."
            )

        normalized = [k.strip().lower() for k in keywords]

        if len(normalized) != len(set(normalized)):

            self.errors.append(
                f"{filename}: "
                f"{record.id} "
                f"contains duplicate keywords."
            )

    # ======================================================
    # Content
    # ======================================================

    def _validate_content(
        self,
        record: SportsKnowledge,
        filename: str,
    ) -> None:

        content = record.content.strip()

        if not content:

            self.errors.append(
                f"{filename}: "
                f"{record.id} "
                f"empty content."
            )

            return

        if len(content) < MIN_CONTENT_LENGTH:

            self.errors.append(
                f"{filename}: "
                f"{record.id} "
                f"content too short."
            )

        if len(content) > MAX_CONTENT_LENGTH:

            self.errors.append(
                f"{filename}: "
                f"{record.id} "
                f"content too long."
            )

    # ======================================================
    # Source
    # ======================================================

    def _validate_source(
        self,
        record: SportsKnowledge,
        filename: str,
    ) -> None:

        source = record.source

        if not source.type.strip():

            self.errors.append(
                f"{filename}: "
                f"{record.id} "
                f"invalid source.type"
            )

        if not source.name.strip():

            self.errors.append(
                f"{filename}: "
                f"{record.id} "
                f"invalid source.name"
            )

        if not source.license.strip():

            self.errors.append(
                f"{filename}: "
                f"{record.id} "
                f"invalid source.license"
            )



    # ======================================================
    # Duplicate Tracking
    # ======================================================

    def _track_duplicates(
        self,
        knowledge: SportsKnowledge,
        filename: str,
    ) -> None:
        """
        Track duplicate IDs and titles across the dataset.
        """

        # -----------------------------
        # Duplicate IDs
        # -----------------------------

        if knowledge.id in self._id_index:

            previous = self._id_index[knowledge.id]

            self.errors.append(
                f"Duplicate record ID '{knowledge.id}'. "
                f"First found in '{previous}', "
                f"again in '{filename}'."
            )

        else:

            self._id_index[knowledge.id] = filename

        # -----------------------------
        # Duplicate Titles
        # -----------------------------

        normalized_title = knowledge.title.strip().lower()

        if normalized_title in self._title_index:

            previous = self._title_index[normalized_title]

            self.errors.append(
                f"Duplicate title '{knowledge.title}'. "
                f"First found in '{previous}', "
                f"again in '{filename}'."
            )

        else:

            self._title_index[
                normalized_title
            ] = filename

    # ======================================================
    # Final Validation
    # ======================================================

    def _validate_duplicates(self) -> None:
        """
        Reserved for future cross-record validation.

        Duplicate IDs and titles are tracked while records
        are processed. This hook is intentionally kept for
        future validations such as:

        - conflicting facts
        - duplicate keywords
        - version conflicts
        - inconsistent metadata
        """

        return

    # ======================================================
    # Summary
    # ======================================================

    def summary(self) -> None:
        """
        Log validation summary.
        """

        logger.info("=" * 60)
        logger.info("Dataset Validation Summary")
        logger.info("=" * 60)

        logger.info(
            f"Files scanned : {self.files_scanned}"
        )

        logger.info(
            f"Records loaded: {len(self.records)}"
        )

        logger.info(
            f"Errors found  : {len(self.errors)}"
        )

        if self.errors:

            logger.error("Validation FAILED")

            for error in self.errors:

                logger.error(error)

        else:

            logger.success(
                "Dataset validation successful."
            )

        logger.info("=" * 60)