import streamlit as st
import pandas as pd
import leafmap.foliumap as leafmap

# Import your functions and CSS
from functions import (
    load_data,
    check_column_names,
    check_missing_values,
    check_data_types,
    check_date_format,
    check_time_format,
    check_coordinates,
)
from css import app_css  # Import CSS as a string

# Set page configuration
st.set_page_config(page_title="Data Quality Reporting", layout="wide")
# Apply CSS styling
st.markdown(app_css, unsafe_allow_html=True)

# Initialize session state variables
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "separator" not in st.session_state:
    st.session_state.separator = ","
if "encoding" not in st.session_state:
    st.session_state.encoding = "utf-8"
if "df" not in st.session_state:
    st.session_state.df = None
if "lat_col" not in st.session_state:
    st.session_state.lat_col = None
if "lon_col" not in st.session_state:
    st.session_state.lon_col = None

# Sidebar for file upload and options
# Sidebar for file upload and settings
st.sidebar.image(r"images/upload_data_image.png", width=250)
st.sidebar.header("Upload Your Data File")
uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV or Excel file", type=["csv", "xls", "xlsx"]
)

# Update session state if a file is uploaded or removed
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file
else:
    st.session_state.uploaded_file = None
    st.session_state.df = None  # Clear the DataFrame when file is removed

# Separator and encoding options in the sidebar
st.session_state.separator = st.sidebar.selectbox(
    "Select CSV Separator", [";", ",", "|", "\t"], index=0
)
st.session_state.encoding = st.sidebar.selectbox(
    "Select File Encoding", ["utf-8", "ISO-8859-1", "latin1", "cp1252"], index=0
)

st.markdown(
    '<h1 class="main-title">Data Quality Reporting</h1>', unsafe_allow_html=True
)

if st.session_state.uploaded_file:
    # Load data with error handling
    df, load_error = load_data(
        st.session_state.uploaded_file,
        st.session_state.separator,
        st.session_state.encoding,
    )
    st.session_state.df = df if df is not None else st.session_state.df

    if load_error:
        st.error(load_error)
    else:
        # Display data in expanders with error handling
        try:
            with st.expander("Uploaded Data", expanded=True):
                st.dataframe(st.session_state.df.head(6))
        except Exception as e:
            st.error(f"An error occurred while displaying the data: {e}")

        # Column Naming Issues in an expander
        try:
            st.markdown(
                '<div class="subheader">Column Naming Issues</div>',
                unsafe_allow_html=True,
            )
            with st.expander("Column Naming Issues", expanded=True):
                col_issues = check_column_names(st.session_state.df)
                for col, issue in col_issues.items():
                    st.warning(f"Column '{col}': {issue}")
                if not col_issues:
                    st.success("All column names follow best practices😀.")
        except Exception as e:
            st.error(f"An error occurred while checking column names: {e}")

        # Missing Values in an expander
        try:
            st.markdown(
                '<div class="subheader">Missing Values</div>', unsafe_allow_html=True
            )
            with st.expander("Missing Values", expanded=True):
                missing_values = check_missing_values(st.session_state.df)
                if not missing_values.empty:
                    st.write(missing_values)
                else:
                    st.success("No missing values found😀.")
        except Exception as e:
            st.error(f"An error occurred while checking for missing values: {e}")

        # Data Types in an expander
        try:
            st.markdown(
                '<div class="subheader">Data Types</div>', unsafe_allow_html=True
            )
            with st.expander("Data Types", expanded=True):
                st.write(check_data_types(st.session_state.df))
        except Exception as e:
            st.error(f"An error occurred while displaying data types: {e}")

        # Date Format Issues in an expander
        try:
            st.markdown(
                '<div class="subheader">Date Column Format Issues</div>',
                unsafe_allow_html=True,
            )
            with st.expander("Date Column Format Issues", expanded=True):
                date_issues, valid_date_columns = check_date_format(st.session_state.df)
                for col, issue in date_issues.items():
                    st.warning(f"{issue}")
                for col in valid_date_columns:
                    st.success(f"Column '{col}' is ISO 8601 (YYYY-MM-DD)😀.")
        except Exception as e:
            st.error(f"An error occurred while checking date formats: {e}")

        # Time Format Issues in an expander
        try:
            st.markdown(
                '<div class="subheader">Time Column Format Issues</div>',
                unsafe_allow_html=True,
            )
            with st.expander("Time Column Format Issues", expanded=True):
                time_issues, valid_time_columns = check_time_format(st.session_state.df)
                for col, issue in time_issues.items():
                    st.warning(f"Column '{col}': {issue}")
                for col in valid_time_columns:
                    st.success(f"Column '{col}' is ISO 8601 (HH:MM[:SS])😀.")
        except Exception as e:
            st.error(f"An error occurred while checking time formats: {e}")

        # Coordinate Checks in an expander
        try:
            st.markdown(
                '<div class="subheader">Coordinate Issues (Latitude and Longitude)</div>',
                unsafe_allow_html=True,
            )
            with st.expander(
                "Coordinate Issues (Latitude and Longitude)", expanded=True
            ):
                (
                    coord_issues,
                    success_message,
                    st.session_state.lat_col,
                    st.session_state.lon_col,
                ) = check_coordinates(st.session_state.df)
                if success_message:
                    st.success(success_message)
                else:
                    for col, issue in coord_issues.items():
                        st.warning(f"{col}: {issue}")
        except Exception as e:
            st.error(f"An error occurred while checking coordinates: {e}")

        # Map visualization in an expander if lat and lon columns are present
        st.markdown(
            '<div class="subheader">Map of Coordinates</div>',
            unsafe_allow_html=True,
        )
        if st.session_state.lat_col and st.session_state.lon_col:
            try:
                with st.expander("Map of Coordinates", expanded=True):

                    unique_map_data = (
                        st.session_state.df[
                            [st.session_state.lat_col, st.session_state.lon_col]
                        ]
                        .dropna()
                        .drop_duplicates()
                    )
                    m = leafmap.Map(
                        center=[
                            unique_map_data[st.session_state.lat_col].mean(),
                            unique_map_data[st.session_state.lon_col].mean(),
                        ],
                        zoom=6,
                    )
                    m.add_basemap("Esri.WorldTopoMap")
                    for _, row in unique_map_data.iterrows():
                        m.add_marker(
                            location=[
                                row[st.session_state.lat_col],
                                row[st.session_state.lon_col],
                            ],
                            shape="circle",
                            popup=f"Coordinates: {row[st.session_state.lat_col]}, {row[st.session_state.lon_col]}",
                            radius=5,
                        )
                    m.to_streamlit(height=600)
            except Exception as e:
                st.error(f"An error occurred while creating the map: {e}")
else:
    st.info("Please upload a CSV or Excel file to begin the quality checks.")
    # Enhanced placeholder message with instructions and icon
    st.markdown(
        '<h3 class="instructions-title">Instructions</h3>', unsafe_allow_html=True
    )
    st.markdown(
        """
        1. **Review Standards**: Check out the **General Data formating Recomendations** and **Column Naming** recommendations below.
        """
    )

    # Display standards in expander
    with st.expander("**_📊 General Data formating Recomendations_**"):
        st.write(
            """
        Best Practices for Column Naming and data formats  
        - **Use Consistent Naming Conventions**: Use snake_case (e.g., `file_name`, `latitude_degS`) or CamelCase (e.g., `FileName`, `LatitudeDegS`).
        - **Include Units**: Specify units, preferable next to the column name separated by an underscore, e.g., `Temperature_C` for Celsius, `Salinity_psu` for practical salinity units.
        - **Date and Time Format**: Use ISO 8601 format for dates (`yyyy-mm-dd`) and specify time format (`HH:MM:SS`).
        - **Avoid Special Characters**: Keep column names simple and avoid characters like spaces and special symbols. Common special characters to avoid include:
            - `!`, `@`, `#`, `$`, `%`, `^`, `&`, `*`, `(`, `)`, `-`, `+`, `=`, `{`, `}`, `[`, `]`, `|`, `\\`, `:`, `;`, `"`, `'`, `<`, `>`, `,`, `?`, `/`, and whitespace.
        - **Consistent Data Types**: Ensure each column has a single data type (e.g., all numeric or all text).
        - **Null Values**: Use a consistent marker for missing data, such as empty cells or "NA".
        - **Quality Flags**: Add a quality flag column to indicate data quality levels (e.g., `0` for good, `1` for suspect).
        - **File Encoding**: Save CSV files with UTF-8 encoding to support a wide range of characters.

        Tidy Data Principles
        - **Each Variable in One Column**: Ensure each column represents a single variable (e.g., `temperature`, `salinity`).
        - **Each Observation in One Row**: Each row should represent a single observation or measurement.
        - **Each Type of Observation in a Separate Table**: Separate different types of data (e.g., measurements vs. metadata) into different tables.
        """
        )

    st.markdown(
        """ 
        2. **Load Your Data**: Once you have checked the recommendations Upload a CSV file with the correct separator and encoding options in the sidebar.
        3. **Data Quality Checks**: Use the quality check expanders to verify data consistency, including missing values and column naming practices.
        4. **Map Your Data**: Verify the latitude and longitude columns to confirm that location coordinates are accurate.
        """
    )
    
    st.markdown(
        """
    <style>
    /* Center and adjust the width of the expander */
    .stExpander {
        width: 95% !important; /* Adjust width as desired */
        margin: 0 auto; /* Center the expander */
    }
    /* Adjust the font size of the expander label */
    .stExpander label {
        font-size: 14px !important; /* Adjust font size as needed */
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
