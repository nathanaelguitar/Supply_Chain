import pandas as pd
import os
from pathlib import Path
from typing import Union, Optional


def load_excel_file(file_path: str, sheet_name: Union[str, int] = 0, verbose: bool = False) -> Optional[pd.DataFrame]:
    """
    Load an Excel file into a pandas DataFrame.
    
    Args:
        file_path (str): Path to the Excel file
        sheet_name (str or int): Sheet name or index to read. Defaults to 0 (first sheet)
        verbose (bool): Whether to print loading messages. Defaults to False
    
    Returns:
        pd.DataFrame: DataFrame containing the Excel data
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        if verbose:
            print(f"Successfully loaded Excel file: {file_path}")
            print(f"Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None


def list_sheet_names(file_path):
    """
    Get all sheet names from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file
    
    Returns:
        list: List of sheet names
    """
    try:
        xls = pd.ExcelFile(file_path)
        return xls.sheet_names
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None


def ingest_excel(file_name: str, sheet_name: Union[str, int] = 0, verbose: bool = False) -> Optional[pd.DataFrame]:
    """
    Ingest an Excel file from the data directory.
    
    Args:
        file_name (str): Name of the Excel file in the data directory
        sheet_name (str or int): Sheet name or index to read. Defaults to 0
        verbose (bool): Whether to print loading messages. Defaults to False
    
    Returns:
        pd.DataFrame: DataFrame containing the Excel data
    """
    data_dir = Path(__file__).parent / "data"
    file_path = data_dir / file_name
    return load_excel_file(str(file_path), sheet_name=sheet_name, verbose=verbose)


def get_schema(df):
    """
    Get DataFrame schema (columns and data types).
    
    Args:
        df (pd.DataFrame): Input DataFrame
    
    Returns:
        pd.DataFrame: Schema information
    """
    schema = pd.DataFrame({
        'Column': df.columns,
        'Data Type': df.dtypes.values,
        'Non-Null Count': df.count().values,
        'Null Count': df.isnull().sum().values
    })
    return schema


def print_schema(df):
    """
    Pretty print DataFrame schema with column information.
    
    Args:
        df (pd.DataFrame): Input DataFrame
    """
    print("\n" + "-"*60)
    print("SCHEMA INFORMATION")
    print("-"*60)
    schema_df = get_schema(df)
    print(schema_df.to_string(index=False))
    print(f"\nShape: {df.shape[0]} rows × {df.shape[1]} columns")
    print("-"*60 + "\n")
