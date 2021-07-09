from datetime import datetime
import pandas as pd

from .cohortextractor import DummyDataValidationError, SUPPORTED_FILE_FORMATS


def validate_dummy_data(study_definition, dummy_data_file):
    """Validate that dummy data provided by user matches expected structure and format.

    Raises DummyDataValidationError if dummy data is not valid.
    """

    df = read_into_dataframe(dummy_data_file)

    validate_expected_columns(df, study_definition)

    for (col_name, (_, query_args)) in study_definition.covariate_definitions.items():
        if col_name == "population":
            # Ignore the population definition, since it is not used as a column in the
            # output
            continue

        if query_args["hidden"]:
            # Ignore hidden covariates
            continue

        validator = get_validator(col_name, query_args)

        for ix, value in enumerate(df[col_name]):
            if pd.isna(value) or value == "":
                # Ignore null or missing values
                continue

            try:
                validator(value)
            except ValueError:
                raise DummyDataValidationError(
                    f"Invalid value `{value}` for {col_name} in row {ix + 2}"
                )


def read_into_dataframe(path):
    """Read data from path into a Pandas DataFrame."""

    try:
        if path.suffixes in [[".csv"], [".csv", ".gz"]]:
            return pd.read_csv(path)
        elif path.suffixes in [[".dta"], [".dta", ".gz"]]:
            return pd.read_stata(path)
        elif path.suffix == ".feather":
            return pd.read_feather(path)
        else:
            msg = f"Dummy data must be in one of the following formats: {', '.join(SUPPORTED_FILE_FORMATS)}"
            raise DummyDataValidationError(msg)
    except FileNotFoundError:
        raise DummyDataValidationError(f"Dummy data file not found: {path}")


def validate_expected_columns(df, study_definition):
    """Raise DummyDataValidationError if dataframe does not have expected columns."""

    expected_columns = {
        col_name
        for col_name, (_, query_args) in study_definition.covariate_definitions.items()
        if not (col_name == "population" or query_args["hidden"])
    }
    expected_columns.add("patient_id")

    extra_columns = set(df.columns) - expected_columns
    if extra_columns:
        if len(extra_columns) == 1:
            msg = f"Unexpected column in dummy data: {list(extra_columns)[0]}"
        else:
            msg = f"Unexpected columns in dummy data: {', '.join(extra_columns)}"
        raise DummyDataValidationError(msg)

    missing_columns = expected_columns - set(df.columns)
    if missing_columns:
        if len(missing_columns) == 1:
            msg = f"Missing column in dummy data: {list(missing_columns)[0]}"
        else:
            msg = f"Missing columns in dummy data: {', '.join(missing_columns)}"
        raise DummyDataValidationError(msg)


def get_validator(col_name, query_args):
    """Return function that validates that value is valid to appear in column.

    A validator is a single-argument function that raises a ValueError on invalid input.
    """

    column_type = query_args["column_type"]
    if column_type == "date":
        if query_args["date_format"] == "YYYY":
            return date_validator_year
        elif query_args["date_format"] == "YYYY-MM":
            return date_validator_month
        elif query_args["date_format"] == "YYYY-MM-DD":
            return date_validator_day
        else:
            assert False, query_args["date_format"]
    elif column_type == "bool":
        return bool_validator
    elif column_type == "int":
        return int
    elif column_type == "str":
        return str
    elif column_type == "float":
        return float
    else:
        assert False, f"Unknown column type {column_type} for column {col_name}"


def bool_validator(value):
    if value not in [True, False]:
        raise ValueError


def date_validator_year(value):
    datetime.strptime(str(int(value)), "%Y")


def date_validator_month(value):
    datetime.strptime(value, "%Y-%m")


def date_validator_day(value):
    datetime.strptime(value, "%Y-%m-%d")
