from importlib.metadata import metadata
import pandas as pd
import kaggle, openml, xlsxwriter, os

from warnings import filterwarnings

filterwarnings("ignore")
kaggle.api.authenticate()

class DatasetRetrieval:
    def __init__(self):
        pass

    def authenticate_kaggle(self):
        """
        Authenticate Kaggle API using kaggle library.
        """
        kaggle.api.authenticate()

    def retrieve_kaggle_data(self, folder_path: str,
                             data_columns: list,
                             search_terms: list,
                             allowed_licenses: list, 
                             max_size: int, 
                             page_range: range) -> pd.DataFrame:
        """
        Retrieve datasets from Kaggle based on search terms, licenses, and size constraints, 
        and store their metadata in an Excel file to catch up quickly. The datasets are downloaded as zip files 
        and saved to a specified folder.

        Args:
            folder_path (str): The path to the folder where datasets and metadata will be stored.
            data_columns (list): A list of column names for the metadata DataFrame. 
                                 Example: ['title', 'file-name', 'description', 'link'].
            search_terms (list): A list of keywords to search for datasets on Kaggle.
                                 Example: ['health', 'finance'].
            allowed_licenses (list): A list of dataset licenses that are allowed for download.
                                     Example: ['CC0-1.0', 'CC0: Public Domain'].
            max_size (int): The maximum size (in MB) of datasets to be considered for download.
            page_range (range): The range of pages to search through in the Kaggle dataset list.

        Returns:
            pd.DataFrame: A DataFrame containing metadata of the downloaded datasets, including:
                          - title: The title of the dataset.
                          - file-name: The name of the dataset file.
                          - description: A brief description of the dataset.
                          - link: The URL link to the dataset on Kaggle.

        Raises:
            HTTPError: If there is an issue with the Kaggle API request (e.g., dataset not found).
            Exception: For any other issues during dataset download or file operations.

        Example:
            data_retrieval = DatasetRetrieval()
            data_retrieval.authenticate_kaggle()
            
            folder_path = '/path/to/output/folder'
            data_columns = ['title', 'file-name', 'description', 'link']
            search_terms = ['health']
            allowed_licenses = ['CC0-1.0', 'CC0: Public Domain']
            max_size = 10  # in MB
            page_range = range(1, 5)

            datasets_info = data_retrieval.retrieve_kaggle_data(folder_path,
                                                                data_columns,
                                                                search_terms,
                                                                allowed_licenses,
                                                                max_size,
                                                                page_range)
            print(datasets_info)
        """
        datasets_downloaded_folder_path = folder_path + '/datasets/'
        if not os.path.exists(datasets_downloaded_folder_path):
            os.makedirs(datasets_downloaded_folder_path)
        
        # Initialize the main records DataFrame
        main_records = pd.DataFrame(columns=data_columns)
        main_records.to_excel(folder_path + '/datasets_information.xlsx',
                            index=None,
                            engine='xlsxwriter')
        main_records = pd.read_excel(folder_path + '/datasets_information.xlsx',
                                    engine='openpyxl')
        
        # Retrieving dataset names to be dowloaded
        datasets_names = [
            dataset
            for word in search_terms
            for page in page_range
            for dataset in kaggle.api.dataset_list(page=page, search=word, max_size=max_size)
        ]

        print(f"Total datasets found for {search_terms}: {len(datasets_names)}")

        # Use sets for faster duplicate checks
        existing_titles = set(main_records['title'])
        existing_links = set(main_records['link'])

        # Downloading the actual datasets
        for data in datasets_names:
            if (vars(data)['_title'] not in existing_titles) \
                and (vars(data)['_url'] not in existing_links): # avoiding duplicates
            
                # Licences of the datasets that will be allowed to be downloaded
                # In this case: public domain licences
                if vars(data)['_license_name'] in allowed_licenses:
                    # Information that will be in the final dataframe
                    title = vars(data)['_title']
                    file_name = str(data).split('/')[1]
                    description = vars(data).get('_description', '')  # Handle missing description gracefully
                    link = vars(data)['_url']
                    # This can be extended with more information if needed,
                    # refer to Kaggle API documentation dataset section: https://github.com/Kaggle/kaggle-api/blob/main/docs/datasets_metadata.md
                    # you will also need to add the new columns to the data_columns list 
                    # and in the following concatenation.

                    main_records = pd.concat([main_records,
                                            pd.DataFrame({'title': [title],
                                                            'file-name': [file_name],
                                                            'description': [description],
                                                            'link':[link]})])

                    # Downloading the data
                    if not os.path.exists(datasets_downloaded_folder_path):
                        os.makedirs(datasets_downloaded_folder_path)
                    # Downloading the data
                    try:
                        print(f"Dataset URL: {vars(data)['_url']}")
                        kaggle.api.dataset_download_files(data._ref,
                                                        path=datasets_downloaded_folder_path,
                                                        unzip=False)
                    except Exception as e:
                        print(f"Failed to download dataset {data._ref}: {e}")
                    
                else: pass
            else: print(f"Dataset {data.title} already in records, skipping...")

        main_records.to_excel(folder_path + '/datasets_information.xlsx',
                            index=None,
                            engine='xlsxwriter')
        return main_records
    
    def retrieve_openml_data(self):
        pass

# Example of usage of the class
if __name__ == "__main__":
    data_retrieval = DatasetRetrieval()
    data_retrieval.authenticate_kaggle()
    
    folder_path = '/home/estiven/Proyectos/kaggle_openml_api_datasets/data_retrieval_output'
    data_columns = ['title', 'file-name', 'description', 'link']
    search_terms = ['health']
    allowed_licenses = ['CC0-1.0', 'CC0: Public Domain', ]
    max_size = 10 # in MB
    page_range = range(1, 5) # pages to search through

    datasets_info = data_retrieval.retrieve_kaggle_data(folder_path,
                                                        data_columns,
                                                        search_terms,
                                                        allowed_licenses,
                                                        max_size,
                                                        page_range)
    print(datasets_info)