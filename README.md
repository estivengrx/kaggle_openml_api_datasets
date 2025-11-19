# Kaggle and OpenML Dataset Retrieval

This project provides a Python-based solution for retrieving datasets from Kaggle and OpenML APIs. It allows users to download datasets based on specific search terms, licenses, and size constraints, while also storing metadata for the retrieved datasets.
Note: search by search terms is only available for Kaggle datasets.

## Features

- **Kaggle Dataset Retrieval**: Search and download datasets from Kaggle based on keywords, licenses, and size limits.
- **OpenML Dataset Retrieval**: Retrieve datasets from OpenML using a range of dataset IDs.
- **Metadata Management**: Automatically maintains metadata for all downloaded datasets in an Excel file.
- **Duplicate Avoidance**: Skips datasets that have already been downloaded.
- **Customizable Storage**: Allows users to specify the folder where datasets and metadata will be stored.

## Project Structure

- `data_retieval.py`: Contains the `DatasetRetrieval` class, which implements the functionality for interacting with Kaggle and OpenML APIs.
- `data_retrieval_output/`: Default folder where datasets and metadata are stored.
  - `datasets/`: Subfolder containing downloaded datasets.
  - `datasets_information.xlsx`: Excel file storing metadata for all retrieved datasets.
- `example_of_usage.py`: Example script demonstrating how to use the `DatasetRetrieval` class.

## Requirements

- Python 3.7+
- Libraries:
  - kaggle
  - openml
  - pandas
  - openpyxl
  - xlsxwriter

Install the required libraries using the following command:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Setup

Before using the project, ensure you have the necessary API credentials:

- **Kaggle**: Place your `kaggle.json` file in the `~/.kaggle/` directory (Linux/Mac) or `C:\Users\<YourUsername>\.kaggle\` (Windows). Refer to [Kaggle API documentation](https://www.kaggle.com/docs/api) for more details.
- **OpenML**: No additional setup is required for OpenML, only the library.

### 2. Example Usage
Refer to the `example_of_usage.py` file for a complete example. Below is a brief overview:

```python
from data_retieval import DatasetRetrieval
retriever = DatasetRetrieval(output_folder='data_retrieval_output/')
# Retrieve Kaggle datasets
retriever.retrieve_kaggle_datasets(
    search_terms=['health', 'finance'],
    allowed_licenses=['CC0-1.0', 'CC0: Public Domain'],
    max_size=100
)
# Retrieve OpenML datasets
retriever.retrieve_openml_datasets(
    id_range=(1, 100),
    allowed_licenses=['CC0', 'Public Domain'],
    max_size=100
)
```

### 3. Output

- **Downloaded Datasets**: Stored in the `data_retrieval_output/datasets/` folder.
- **Metadata**: Stored in `data_retrieval_output/datasets_information.xlsx`.

## Notes

- Only public datasets are downloaded. Private datasets are skipped.
- Ensure you have sufficient disk space for storing the datasets.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the [Unlicense](https://unlicense.org), making it free and open-source software.