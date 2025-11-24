"""
Example module demonstrating PEP 257 docstring standards.

This module serves as a template for contributors to follow when
creating new modules in the Telemetry Analysis Tool project.

Typical usage example:

    from src.example import ExampleClass
    
    processor = ExampleClass(config_path="config.yaml")
    result = processor.process_data(data)
"""

from typing import Optional, List, Dict, Any
import pandas as pd


class ExampleClass:
    """
    Example class demonstrating proper docstring format.
    
    This class shows how to document classes with attributes,
    methods, and examples following PEP 257 conventions.
    
    Attributes:
        config (Dict[str, Any]): Configuration dictionary.
        data (Optional[pd.DataFrame]): Loaded data.
        processed (bool): Whether data has been processed.
    
    Example:
        >>> processor = ExampleClass({"threshold": 0.5})
        >>> processor.load_data("data.csv")
        >>> result = processor.process_data()
        >>> print(result.shape)
        (100, 5)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ExampleClass.
        
        Args:
            config (Dict[str, Any]): Configuration parameters including
                'threshold', 'max_iterations', and 'verbose'.
        
        Raises:
            ValueError: If required config keys are missing.
        """
        self.config = config
        self.data: Optional[pd.DataFrame] = None
        self.processed = False
    
    def load_data(self, filepath: str, validate: bool = True) -> bool:
        """
        Load data from a CSV file.
        
        Args:
            filepath (str): Absolute path to the CSV file.
            validate (bool, optional): Whether to validate data integrity.
                Defaults to True.
        
        Returns:
            bool: True if loading succeeded, False otherwise.
        
        Raises:
            FileNotFoundError: If filepath does not exist.
            pd.errors.ParserError: If CSV is malformed.
        
        Example:
            >>> processor = ExampleClass({})
            >>> success = processor.load_data("telemetry.csv")
            >>> if success:
            ...     print("Data loaded successfully")
        """
        try:
            self.data = pd.read_csv(filepath)
            if validate:
                self._validate_data()
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def process_data(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Process the loaded data.
        
        Applies transformations specified in the config to the loaded
        data. If no data is loaded, raises an exception.
        
        Args:
            columns (Optional[List[str]], optional): Specific columns to
                process. If None, processes all columns. Defaults to None.
        
        Returns:
            pd.DataFrame: Processed dataframe with transformed values.
        
        Raises:
            RuntimeError: If no data has been loaded.
            KeyError: If specified columns don't exist in data.
        
        Note:
            This method modifies the internal state by setting
            self.processed to True.
        
        Example:
            >>> processor = ExampleClass({"threshold": 0.5})
            >>> processor.load_data("data.csv")
            >>> result = processor.process_data(columns=["col1", "col2"])
            >>> print(result.head())
        """
        if self.data is None:
            raise RuntimeError("No data loaded. Call load_data() first.")
        
        # Processing logic here
        result = self.data.copy()
        self.processed = True
        return result
    
    def _validate_data(self) -> None:
        """
        Validate the loaded data (private method).
        
        Private methods should still have docstrings but can be briefer.
        This method checks for required columns and data types.
        
        Raises:
            ValueError: If validation fails.
        """
        if self.data is None or self.data.empty:
            raise ValueError("Data is empty or None")


def utility_function(input_value: float, threshold: float = 0.5) -> bool:
    """
    Example utility function with simple docstring.
    
    Checks if input_value exceeds the threshold.
    
    Args:
        input_value (float): The value to check.
        threshold (float, optional): Comparison threshold. Defaults to 0.5.
    
    Returns:
        bool: True if input_value > threshold, False otherwise.
    
    Example:
        >>> utility_function(0.7)
        True
        >>> utility_function(0.3, threshold=0.5)
        False
    """
    return input_value > threshold
