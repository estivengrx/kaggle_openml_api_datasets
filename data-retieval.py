import pandas as pd
import kaggle, openml, os

from warnings import filterwarnings

filterwarnings("ignore")
kaggle.api.authenticate()

class DatasetRetrieval:
    def __init__(self, folder_path: str, data_columns: list):
        """
        Initialize the DatasetRetrieval class.

        This constructor sets up the folder paths for storing datasets and metadata,
        initializes the metadata file if it does not exist, and creates the necessary
        directories for storing downloaded datasets.

        Attributes:
            folder_path (str): Path to the folder where datasets and metadata will be stored.
            data_columns (list): List of column names for the metadata DataFrame.
            datasets_folder (str): Path to the folder where downloaded datasets will be stored.
            metadata_file (str): Path to the Excel file where metadata about the datasets is stored.
        """
        self.folder_path = folder_path  # Path to the folder where datasets and metadata will be stored
        self.data_columns = data_columns  # List of column names for the metadata DataFrame
        self.datasets_folder = os.path.join(folder_path, "datasets")  # Folder to store downloaded datasets

        # Creating folder to download datasets if it doesn't exist
        os.makedirs(self.datasets_folder, exist_ok=True)

        # Initialize metadata file or create it if it doesn't exist
        self.metadata_file = os.path.join(folder_path, "datasets_information.xlsx")

        if not os.path.exists(self.metadata_file):
            df = pd.DataFrame(columns=self.data_columns)
            df.to_excel(self.metadata_file, index=False, engine="xlsxwriter")

    def authenticate_kaggle(self):
        """
        Authenticate the Kaggle API using the `kaggle` library.

        This method ensures that the Kaggle API is authenticated using the credentials
        stored in the `~/.kaggle/kaggle.json` file. The credentials must be set up prior
        to using this method. Authentication is required to access Kaggle datasets and
        other API functionalities.
        """
        kaggle.api.authenticate()
        
    def _load_metadata_file(self):
        """
        Load the metadata Excel file into a DataFrame.

        This method reads the `datasets_information.xlsx` file located in the `folder_path`
        directory and loads its contents into a pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the metadata of the datasets.
        """
        return pd.read_excel(self.metadata_file, engine='openpyxl')
    
    def _save_metadata_file(self, df: pd.DataFrame, sheet_name: str = 'Sheet1'):
        """
        Save the metadata DataFrame to an Excel file.

        Args:
            df (pd.DataFrame): The DataFrame containing metadata to be saved.

        This method saves the provided DataFrame to the `datasets_information.xlsx` file
        located in the `folder_path` directory. The file is saved using the `xlsxwriter` engine.
        """
        df.to_excel(self.metadata_file, index=False, engine='xlsxwriter', sheet_name=sheet_name)
        
    def _is_dataset_allowed(self, dataset, allowed_licenses: list, max_size: int) -> bool:
        """
        Check if a dataset meets the allowed license and size constraints.

        Args:
            dataset (object): The dataset object retrieved from the Kaggle API.
            allowed_licenses (list): A list of allowed license names for the dataset.
                                    Example: ['CC0-1.0', 'CC0: Public Domain'].
            max_size (int): The maximum allowed size of the dataset in megabytes (MB).

        Returns:
            bool: True if the dataset's license is in the allowed licenses and its size
                is less than or equal to the maximum size, False otherwise.
        """
        if len(allowed_licenses) == 0:
            return True
        else:
            return (dataset.license_name in allowed_licenses 
                    and dataset.total_bytes / (1024**2) <= max_size)

    def retrieve_kaggle_data(self, search_terms: list,
                            allowed_licenses: list,
                            max_size: int,
                            page_range: range) -> pd.DataFrame:
        """
        Retrieve datasets from Kaggle based on search terms, licenses, and size constraints, 
        and store their metadata in an Excel file. The datasets are downloaded as zip files 
        and saved to a specified folder.

        This method ensures that only datasets meeting the specified license and size constraints 
        are downloaded. Metadata for successfully downloaded datasets is saved to an Excel file 
        for future reference.

        Args:
            search_terms (list): A list of keywords to search for datasets on Kaggle.
                                Example: ['health', 'finance'].
            allowed_licenses (list): A list of dataset licenses that are allowed for download.
                                    Example: ['CC0-1.0', 'CC0: Public Domain'].
            max_size (int): The maximum size (in MB) of datasets to be considered for download.
            page_range (range): The range of pages to search through in the Kaggle dataset list.

        Returns:
            pd.DataFrame: A DataFrame containing metadata of the successfully downloaded datasets, including:
                        - title: The title of the dataset.
                        - file-name: The name of the dataset file.
                        - description: A brief description of the dataset.
                        - link: The URL link to the dataset on Kaggle.

        Raises:
            Exception: If there is an issue with the Kaggle API request or dataset download.

        Example:
            data_retrieval = DatasetRetrieval(folder_path, data_columns)
            data_retrieval.authenticate_kaggle()

            search_terms = ['health']
            allowed_licenses = ['CC0-1.0', 'CC0: Public Domain']
            max_size = 10  # in MB
            page_range = range(1, 5)

            datasets_info = data_retrieval.retrieve_kaggle_data(
                search_terms=search_terms,
                allowed_licenses=allowed_licenses,
                max_size=max_size,
                page_range=page_range
            )
            print(datasets_info)
        """
        df = self._load_metadata_file()

        # Sets of titles and links for faster duplicate checks
        existing_titles = set(df['title'])
        existing_links = set(df['link'])

        datasets_names = []
        for word in search_terms:
            for page in page_range:
                try:
                    datasets = kaggle.api.dataset_list(page=page, search=word, max_size=max_size)
                    if datasets:  # Ensure datasets is not None
                        datasets_names.extend(datasets)
                except Exception as e:
                    print(f"Error retrieving datasets for search term '{word}' on page {page}: {e}")

        print(f"Total datasets found for {search_terms}: {len(datasets_names)}")

        # Process each dataset
        for dataset in datasets_names:

            title = dataset.title
            link = dataset.url

            # Skip duplicates
            if title in existing_titles or link in existing_links:
                print(f"Skipping {title}: already downloaded")
                continue

            # Check license + size
            if not self._is_dataset_allowed(dataset, allowed_licenses, max_size):
                continue

            # Prepare metadata entry
            new_entry = {
                "title": title,
                "file-name": dataset.ref,
                "description": dataset.subtitle or "",
                "link": link
            }   

            # Download dataset
            try:
                kaggle.api.dataset_download_files(
                    dataset.ref,
                    path=os.path.join(self.datasets_folder, "kaggledata"),
                    unzip=False
                )
                print(f"Downloaded: {dataset.ref}")

                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True) # Add metadata to df
                self._save_metadata_file(df, sheet_name='kaggle-data') # Save updated metadata
            except Exception as e:
                print(f"Failed to download {dataset.ref}: {e}")

        print('Total datasets downloaded:', len(df))
        return df
    
    def retrieve_openml_data(self, index_range: range):
        """
        Retrieve datasets from OpenML using a range of dataset IDs and store both 
        their metadata and the dataset files locally.

        This method loads an existing metadata file, iterates over a range of 
        OpenML dataset IDs, retrieves dataset information, avoids duplicates based 
        on title and URL, appends new metadata to the metadata file, downloads the 
        dataset content, and saves it as a CSV. Updated metadata is written back 
        to disk after each dataset is processed.

        Args:
            index_range (range): 
                A range of OpenML dataset IDs to retrieve. 
                Example: `range(100, 200)`.

        Returns:
            pd.DataFrame:
                A DataFrame containing the updated metadata for all processed 
                OpenML datasets, with columns such as:
                - title
                - file-name
                - description
                - link

        Workflow:
            1. Load the existing metadata file.
            2. Create sets of existing titles and URLs to detect duplicates.
            3. For each dataset ID:
                - Retrieve dataset metadata using OpenML API.
                - Skip datasets that already appear in metadata.
                - Append new dataset metadata to the metadata DataFrame.
                - Download dataset content and convert it to a DataFrame.
                - Save the dataset as a CSV file in `datasets/openml/`.
            4. Save the updated metadata file to disk.
            5. Return the metadata DataFrame.

        Notes:
            - Only public datasets are downloaded. Private datasets are skipped.
            - Each dataset is saved as `<title>.csv` inside the OpenML output folder.
            - Metadata is saved incrementally after processing each dataset.

        Raises:
            openml.exceptions.OpenMLPrivateDatasetError:
                If the dataset is private and cannot be accessed.
            Exception:
                For any other errors that occur during dataset retrieval,
                conversion, or file saving operations.

        Example:
            >>> retriever = DatasetRetrieval(folder_path="/path/to/data")
            >>> meta = retriever.retrieve_openml_data(range(100, 110))
            >>> print(meta.head())
        """
        # Load metadata file
        metadata_df = self._load_metadata_file()

        # Sets to avoid duplicates
        existing_titles = set(metadata_df['title'])
        existing_links = set(metadata_df['link'])

        # Folder where CSVs will be stored
        output_dir = os.path.join(self.folder_path, "datasets", "openml")
        os.makedirs(output_dir, exist_ok=True)

        for dataset_id in index_range:
            try:
                dataset_info = openml.datasets.get_dataset(dataset_id, download_data=False)

                title = dataset_info.name
                link = dataset_info.original_data_url
                description = dataset_info.description

                if title in existing_titles or link in existing_links: # Avoid duplicates
                    print(f"Skipping {title} — already exists.")
                    continue

                metadata_df = pd.concat([ 
                    metadata_df,
                    pd.DataFrame({
                        "title": [title],
                        "file-name": [title],
                        "description": [description],
                        "link": [link]
                    })
                ], ignore_index=True) # Append new metadata

                # Update sets for faster lookup
                existing_titles.add(title)
                existing_links.add(link)

                X, y, _, attribute_names = dataset_info.get_data(
                    dataset_format="dataframe",
                    target=dataset_info.default_target_attribute
                ) # Retrieve datasets

                dataset_df = X.copy()
                if y is not None:
                    dataset_df["class"] = y

                dataset_df.to_csv(os.path.join(output_dir, f"{title}.csv"), index=False) # Save as CSV
                print(f"Downloaded: {title}")

            except openml.exceptions.OpenMLPrivateDatasetError:
                print(f"Dataset {dataset_id} is private — skipping.")
                continue

            except Exception as e:
                print(f"Error retrieving dataset {dataset_id}: {e}")
                continue

            self._save_metadata_file(metadata_df, sheet_name="openml-data") # Saving rows for each dataset

        return metadata_df


# # Example of usage of the class
# if __name__ == "__main__":
    
#     # # Define settings before instantiating the class
#     # folder_path = os.path.join(
#     #     os.path.dirname(os.path.abspath(__file__)),
#     #     "data_retrieval_output"
#     # )

#     # data_columns = ['title', 'file-name', 'description', 'link']
#     # search_terms = ['health']
#     # allowed_licenses = []
#     # max_size = 10  # in MB
#     # page_range = range(1, 2)

#     # # Instantiate the class (folder_path + columns are stored internally)
#     # data_retrieval = DatasetRetrieval(folder_path, data_columns)

#     # # Authenticate Kaggle API
#     # data_retrieval.authenticate_kaggle()

#     # # Retrieve datasets
#     # datasets_info = data_retrieval.retrieve_kaggle_data(
#     #     search_terms=search_terms,
#     #     allowed_licenses=allowed_licenses,
#     #     max_size=max_size,
#     #     page_range=page_range
#     # )

#     # Define the main folder where metadata and datasets will be stored
#     folder_path = os.path.join(
#         os.path.dirname(os.path.abspath(__file__)),
#         "data_retrieval_output"
#     )

#     # Metadata file columns for OpenML
#     data_columns = ['title', 'file-name', 'description', 'link']

#     # Instantiate your retrieval class
#     data_retrieval = DatasetRetrieval(folder_path, data_columns)

#     # Choose a range of OpenML dataset IDs to download
#     # (small range just for demo — OpenML has thousands)
#     dataset_range = range(50, 60)

#     # Retrieve datasets
#     metadata_df = data_retrieval.retrieve_openml_data(dataset_range)

#     # Show updated metadata
#     print("\nDownloaded datasets metadata:\n")
#     print(metadata_df)
