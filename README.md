This project contains Python code to download large amounts of datasets from Kaggle and OpenML's APIs. The main script is contained in the Jupyter notebook `kaggle_api_and_openml_library.ipynb`

## Inside `kaggle_api_and_openml_library.ipynb`
The notebook is divided into several sections:

1. **Importing Libraries**: The necessary Python libraries are imported. This includes `pandas`, `kaggle`, `openml`, `xlsxwriter`, and `os`.

2. **Creating the DataFrame**: A DataFrame `main_records` is created to hold the name of the dataset, file name, description, and link.

3. **Kaggle Datasets**: The Kaggle API is used to search for datasets based on specific keywords. The names of the datasets are stored in a list `datasets_names`. The datasets are then downloaded if they meet certain conditions (e.g., they have a public domain license).

4. **OpenML Datasets**: The OpenML API is used to retrieve dataset information for a range of dataset indices. The information is stored in a DataFrame `openml_records`. The datasets are then downloaded if they meet certain conditions.

5. **Requirements**: The notebook also includes a cell to generate a `requirements.txt` file that lists all the Python packages needed to run the notebook.

## Running the Notebook

To run the notebook, you will need to install the necessary Python packages. You can do this by running `pip install -r requirements.txt` in your terminal.
Please note that you will need to have a Kaggle API key (`kaggle.json`) to download datasets from Kaggle. You can obtain this key from your Kaggle account settings.
