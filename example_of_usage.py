import os
from data_retieval import DatasetRetrieval

def main():
    """
    Main function to demonstrate the usage of the DatasetRetrieval class
    for retrieving datasets from Kaggle and OpenML.
    """
    # Define the main folder where metadata and datasets will be stored
    folder_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data_retrieval_output"
    )

    # Instantiate the DatasetRetrieval class
    data_retrieval = DatasetRetrieval(folder_path)

    # Authenticate Kaggle API
    data_retrieval.authenticate_kaggle()

    # Retrieve Kaggle datasets
    search_terms = ['health']
    allowed_licenses = []  # Empty list means no license filtering
    max_size = 10  # Maximum dataset size in MB
    page_range = range(1, 2)  # Pages to search through

    print("\nRetrieving Kaggle datasets...")
    kaggle_metadata = data_retrieval.retrieve_kaggle_data(
        search_terms=search_terms,
        allowed_licenses=allowed_licenses,
        max_size=max_size,
        page_range=page_range
    )
    print("\nKaggle datasets metadata:\n")
    print(kaggle_metadata)

    # Retrieve OpenML datasets
    dataset_range = range(50, 60)  # Range of OpenML dataset IDs to download (only as an example)

    print("\nRetrieving OpenML datasets...")
    openml_metadata = data_retrieval.retrieve_openml_data(dataset_range)
    print("\nOpenML datasets metadata:\n")
    print(openml_metadata)

if __name__ == "__main__":
    main()