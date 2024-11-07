import pandas as pd
import re


import pandas as pd


def load_data(file, sep, enc):
    """
    Load data from a CSV or Excel file into a pandas DataFrame with error handling.
    """
    try:
        # Try to read CSV or Excel file with specified separator and encoding
        if file.name.endswith(".csv"):
            df = pd.read_csv(file, sep=sep, encoding=enc)
        else:
            df = pd.read_excel(file)
        return df, None

    # Handle encoding errors
    except UnicodeDecodeError as e:
        error_msg = f"Encoding error: {e}. Try using a different encoding."
        return None, error_msg

    # Handle separator or parsing errors in CSV files
    except pd.errors.ParserError as e:
        error_msg = f"Parsing error: {e}. Check if the selected separator [{sep}] matches the file structure."
        return None, error_msg

    # General exception catch for unexpected errors
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        return None, error_msg


def check_column_names(df):
    """
    Check for spaces, special characters, and adherence to naming conventions in column names.
    """
    issues = {}
    forbidden_chars = r"[ !@#\$%\^&\*\(\)\-\+=\{\}\[\]\|\\:;\"'<>,\?\/]"
    for col in df.columns:
        if re.search(forbidden_chars, col):
            issues[col] = "Contains spaces, hyphens, or special characters."
        elif not re.match("^[A-Za-z0-9_]+$", col):
            issues[col] = "Contains characters outside of alphanumeric and underscores."
    return issues


def check_missing_values(df):
    """
    Identify columns with missing values and their counts.
    """
    missing_values = df.isnull().sum()
    return missing_values[missing_values > 0]


def check_data_types(df):
    """
    Verify that each column has a consistent data type.
    """
    return df.dtypes


def check_date_format(df):
    """
    Validate that date columns follow the ISO 8601 format (YYYY-MM-DD).
    If no 'date' column is found, search for columns with values that resemble date format.
    """
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    date_columns = [col for col in df.columns if col.lower().startswith("date")]
    date_issues = {}
    valid_date_columns = []

    # If no explicit 'date' columns are found, search for potential date-formatted columns
    if not date_columns:
        # Look for columns where all values match the date pattern
        potential_date_columns = [
            col
            for col in df.columns
            if df[col].dtype == object and df[col].str.match(date_pattern).all()
        ]
        date_columns.extend(potential_date_columns)

    # Perform checks on identified date columns
    if date_columns:
        for col in date_columns:
            if df[col].dtype == object:
                if not df[col].str.match(date_pattern).all():
                    date_issues[col] = (
                        f"Column '{col}' does not follow ISO 8601 format (YYYY-MM-DD)😟. Please double check it and update it if necessary."
                    )
                else:
                    valid_date_columns.append(col)
            else:
                date_issues[col] = (
                    f"Column '{col}' is not in a text format (string type required for validation)."
                )
    else:
        date_issues["Info"] = (
            "No columns detected that appear to represent date in standard or inferred formats."
        )

    return date_issues, valid_date_columns


def check_time_format(df):
    """
    Validate that time columns follow the ISO 8601 format (HH:MM[:SS]).
    If no 'time' column is found, search for columns with values that resemble time.
    """
    time_pattern = r"^\d{2}:\d{2}(:\d{2})?$"
    time_columns = [col for col in df.columns if col.lower().startswith("time")]
    time_issues = {}
    valid_time_columns = []

    # If no explicit 'time' columns are found, search for potential time-formatted columns
    if not time_columns:
        # Look for columns where all values match the time pattern
        potential_time_columns = [
            col
            for col in df.columns
            if df[col].dtype == object and df[col].str.match(time_pattern).all()
        ]
        time_columns.extend(potential_time_columns)

    # Perform checks on identified time columns
    if time_columns:
        for col in time_columns:
            if df[col].dtype == object:
                if not df[col].str.match(time_pattern).all():
                    time_issues[col] = (
                        f"Column '{col}' does not follow ISO 8601 format (HH:MM[:SS])😟. Please double check it and update it if necessary."
                    )
                else:
                    valid_time_columns.append(col)
            else:
                time_issues[col] = (
                    f"Column '{col}' is not in a text format (string type required for validation).😟"
                )
    else:
        time_issues["Time"] = (
            "No columns detected that appear to represent time in standard or inferred formats."
        )

    return time_issues, valid_time_columns


def check_coordinates(df):
    """
    Validate that latitude and longitude columns are within valid decimal degree ranges,
    ensure they are in decimal degrees format, and make latitude values negative where needed.
    """
    # Locate columns with "lat" or "latitude" and "lon" or "longitude" in their names
    lat_col = next(
        (col for col in df.columns if re.search(r"^lat|latitude", col, re.IGNORECASE)),
        None,
    )
    lon_col = next(
        (col for col in df.columns if re.search(r"^lon|longitude", col, re.IGNORECASE)),
        None,
    )
    coord_issues = {}
    success_message = None

    if lat_col and lon_col:
        # Ensure latitude values are negative if needed
        df[lat_col] = df[lat_col].apply(lambda x: -abs(x) if x > 0 else x)

        # Check if latitude and longitude values are within decimal degrees ranges
        lat_in_degrees = df[lat_col].between(-90, 90).all()
        lon_in_degrees = df[lon_col].between(-180, 180).all()

        # Check if the latitude and longitude columns are numeric
        lat_is_numeric = pd.api.types.is_numeric_dtype(df[lat_col])
        lon_is_numeric = pd.api.types.is_numeric_dtype(df[lon_col])

        # Collect issues or provide success message
        if lat_in_degrees and lon_in_degrees and lat_is_numeric and lon_is_numeric:
            success_message = f"The '{lat_col}' and '{lon_col}' columns appear to be in decimal degrees and within valid ranges😀."
        else:
            if not lat_in_degrees:
                coord_issues[lat_col] = "Contains values outside the range -90 to 90😟."
            if not lon_in_degrees:
                coord_issues[lon_col] = (
                    "Contains values outside the range -180 to 180😟."
                )
            if not lat_is_numeric:
                coord_issues[lat_col] = (
                    "Latitude column is not in decimal degrees (numeric type required)😟."
                )
            if not lon_is_numeric:
                coord_issues[lon_col] = (
                    "Longitude column is not in decimal degrees (numeric type required)😟."
                )
    else:
        coord_issues["Coordinates"] = (
            "Latitude and/or Longitude columns could not be automatically detected. Ensure column names contain 'lat' or 'latitude' and 'lon' or 'longitude'."
        )

    return coord_issues, success_message, lat_col, lon_col
