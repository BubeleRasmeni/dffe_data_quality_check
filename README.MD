# Data Quality Reporting Dashboard

This is a Streamlit-based web application designed for data quality reporting, specifically for oceanographic datasets. The app allows users to upload CSV or Excel files, perform data quality checks, and view quality control (QC) reports. The interface includes clear instructions and provides a comprehensive analysis of data quality issues.

## Features

- **File Upload**: Supports uploading data files in CSV, XLSX, and XLX formats.
- **Data Quality Checks**: Automatically performs quality checks on uploaded data, including:
  - Column name and data type consistency
  - Range and threshold validation
  - Missing values and duplicates
  - Geospatial consistency
  - Outlier detection
  - Data validation against external sources
- **Quality Control Reporting**: Generates a QC report that flags data quality issues and maintains a log for tracking.
- **Instructions and Documentation**: Clear instructions for using the app and understanding the quality standards.

## Getting Started

### Prerequisites

- **Python 3.7 or higher**
- **Streamlit**: Install Streamlit using `pip install streamlit`.

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/data-quality-reporting-dashboard.git
   ```
