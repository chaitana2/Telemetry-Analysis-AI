"""
Multi-File Manager - Handle multiple CSV files with intelligent merging.

This module provides capabilities for importing multiple CSV files,
detecting relationships, and intelligently merging data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from fuzzywuzzy import fuzz
import os



@dataclass
class FileInfo:
    """Information about an imported file."""
    filepath: str
    filename: str
    rows: int
    columns: int
    column_names: List[str]
    schema_hash: str


@dataclass
class RelationshipInfo:
    """Information about detected relationships between files."""
    file1: str
    file2: str
    common_columns: List[str]
    correlation_score: float
    suggested_join_type: str
    join_keys: List[str]


class MultiFileManager:
    """
    Manages multiple CSV file imports and intelligent merging.
    """
    
    def __init__(self):
        """Initialize the manager."""
        self.files: Dict[str, pd.DataFrame] = {}
        self.file_info: Dict[str, FileInfo] = {}
        self.relationships: List[RelationshipInfo] = []
    
    def import_multiple_files(self, filepaths: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Import multiple CSV files.
        
        Args:
            filepaths (List[str]): List of file paths to import.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping filenames to dataframes.
        """
        for filepath in filepaths:
            try:
                df = pd.read_csv(filepath)
                filename = os.path.basename(filepath)
                
                self.files[filename] = df
                self.file_info[filename] = FileInfo(
                    filepath=filepath,
                    filename=filename,
                    rows=len(df),
                    columns=len(df.columns),
                    column_names=df.columns.tolist(),
                    schema_hash=self._generate_schema_hash(df)
                )
                
                print(f"Imported {filename}: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                print(f"Error importing {filepath}: {e}")
        
        # Detect relationships after all files are loaded
        if len(self.files) > 1:
            self.relationships = self.detect_relationships()
        
        return self.files
    
    def detect_relationships(self) -> List[RelationshipInfo]:
        """
        Detect relationships between imported files.
        
        Returns:
            List[RelationshipInfo]: List of detected relationships.
        """
        relationships = []
        filenames = list(self.files.keys())
        
        # Compare each pair of files
        for i in range(len(filenames)):
            for j in range(i + 1, len(filenames)):
                file1 = filenames[i]
                file2 = filenames[j]
                
                relationship = self._analyze_relationship(file1, file2)
                if relationship:
                    relationships.append(relationship)
        
        return relationships
    
    def _analyze_relationship(self, file1: str, file2: str) -> Optional[RelationshipInfo]:
        """
        Analyze relationship between two files.
        
        Args:
            file1 (str): First filename.
            file2 (str): Second filename.
        
        Returns:
            Optional[RelationshipInfo]: Relationship info if found.
        """
        df1 = self.files[file1]
        df2 = self.files[file2]
        
        # Find common columns (exact match)
        common_exact = set(df1.columns) & set(df2.columns)
        
        # Find similar columns (fuzzy match)
        common_fuzzy = self._find_similar_columns(df1.columns, df2.columns)
        
        common_columns = list(common_exact) + common_fuzzy
        
        if not common_columns:
            return None
        
        # Calculate correlation score
        correlation_score = len(common_columns) / max(len(df1.columns), len(df2.columns))
        
        # Suggest join keys
        join_keys = self._suggest_join_keys(df1, df2, common_columns)
        
        # Suggest join type
        join_type = self._suggest_join_type(df1, df2, join_keys)
        
        return RelationshipInfo(
            file1=file1,
            file2=file2,
            common_columns=common_columns,
            correlation_score=correlation_score,
            suggested_join_type=join_type,
            join_keys=join_keys
        )
    
    def _find_similar_columns(self, cols1: List[str], cols2: List[str], 
                             threshold: int = 80) -> List[str]:
        """
        Find similar column names using fuzzy matching.
        
        Args:
            cols1 (List[str]): Columns from first dataframe.
            cols2 (List[str]): Columns from second dataframe.
            threshold (int): Similarity threshold (0-100).
        
        Returns:
            List[str]: List of similar column pairs.
        """
        similar = []
        
        for col1 in cols1:
            for col2 in cols2:
                if col1 == col2:
                    continue
                
                similarity = fuzz.ratio(col1.lower(), col2.lower())
                if similarity >= threshold:
                    similar.append(f"{col1}~{col2}")
        
        return similar
    
    def _suggest_join_keys(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                          common_columns: List[str]) -> List[str]:
        """
        Suggest appropriate join keys.
        
        Args:
            df1 (pd.DataFrame): First dataframe.
            df2 (pd.DataFrame): Second dataframe.
            common_columns (List[str]): Common columns.
        
        Returns:
            List[str]: Suggested join keys.
        """
        join_keys = []
        
        # Priority keywords for join keys
        priority_keywords = ['id', 'number', 'driver', 'lap', 'time', 'position']
        
        for col in common_columns:
            col_lower = col.lower()
            
            # Check if column name suggests it's a key
            if any(keyword in col_lower for keyword in priority_keywords):
                # Check if values are suitable for joining (not all unique or all same)
                if col in df1.columns and col in df2.columns:
                    unique_ratio1 = df1[col].nunique() / len(df1)
                    unique_ratio2 = df2[col].nunique() / len(df2)
                    
                    # Good join key has moderate uniqueness (not 100%, not 0%)
                    if 0.1 < unique_ratio1 < 0.9 and 0.1 < unique_ratio2 < 0.9:
                        join_keys.append(col)
        
        # If no good keys found, use first common column
        if not join_keys and common_columns:
            join_keys = [common_columns[0]]
        
        return join_keys
    
    def _suggest_join_type(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                          join_keys: List[str]) -> str:
        """
        Suggest appropriate join type.
        
        Args:
            df1 (pd.DataFrame): First dataframe.
            df2 (pd.DataFrame): Second dataframe.
            join_keys (List[str]): Join keys.
        
        Returns:
            str: Suggested join type ('inner', 'outer', 'left', 'right').
        """
        if not join_keys:
            return 'outer'
        
        # Check overlap of key values
        key = join_keys[0]
        if key not in df1.columns or key not in df2.columns:
            return 'outer'
        
        values1 = set(df1[key].dropna().unique())
        values2 = set(df2[key].dropna().unique())
        
        overlap = len(values1 & values2)
        total = len(values1 | values2)
        
        overlap_ratio = overlap / total if total > 0 else 0
        
        # Suggest join type based on overlap
        if overlap_ratio > 0.8:
            return 'inner'  # High overlap - inner join
        elif overlap_ratio > 0.5:
            return 'outer'  # Moderate overlap - outer join
        elif len(values1) > len(values2):
            return 'left'   # More values in df1 - left join
        else:
            return 'right'  # More values in df2 - right join
    
    def merge_files(self, filenames: Optional[List[str]] = None, 
                   strategy: str = 'auto') -> pd.DataFrame:
        """
        Merge multiple files intelligently.
        
        Args:
            filenames (Optional[List[str]]): Files to merge. If None, merge all.
            strategy (str): Merge strategy ('auto', 'concat', 'join').
        
        Returns:
            pd.DataFrame: Merged dataframe.
        """
        if filenames is None:
            filenames = list(self.files.keys())
        
        if len(filenames) == 0:
            return pd.DataFrame()
        
        if len(filenames) == 1:
            return self.files[filenames[0]]
        
        # Auto strategy - detect best approach
        if strategy == 'auto':
            strategy = self._determine_merge_strategy(filenames)
        
        if strategy == 'concat':
            return self._merge_by_concat(filenames)
        else:  # join
            return self._merge_by_join(filenames)
    
    def _determine_merge_strategy(self, filenames: List[str]) -> str:
        """
        Determine best merge strategy.
        
        Args:
            filenames (List[str]): Files to merge.
        
        Returns:
            str: 'concat' or 'join'.
        """
        # Check if all files have same schema
        schemas = [self.file_info[f].schema_hash for f in filenames if f in self.file_info]
        
        if len(set(schemas)) == 1:
            return 'concat'  # Same schema - concatenate
        else:
            return 'join'    # Different schemas - join
    
    def _merge_by_concat(self, filenames: List[str]) -> pd.DataFrame:
        """
        Merge files by concatenation (same schema).
        
        Args:
            filenames (List[str]): Files to merge.
        
        Returns:
            pd.DataFrame: Concatenated dataframe.
        """
        dfs = [self.files[f] for f in filenames if f in self.files]
        
        # Add source column to track origin
        for i, df in enumerate(dfs):
            df['_source_file'] = filenames[i]
        
        return pd.concat(dfs, ignore_index=True)
    
    def _merge_by_join(self, filenames: List[str]) -> pd.DataFrame:
        """
        Merge files by joining (different schemas).
        
        Args:
            filenames (List[str]): Files to merge.
        
        Returns:
            pd.DataFrame: Joined dataframe.
        """
        if len(filenames) < 2:
            return self.files[filenames[0]] if filenames else pd.DataFrame()
        
        # Start with first file
        result = self.files[filenames[0]].copy()
        
        # Join with each subsequent file
        for i in range(1, len(filenames)):
            # Find relationship
            relationship = None
            for rel in self.relationships:
                if (rel.file1 == filenames[0] and rel.file2 == filenames[i]) or \
                   (rel.file2 == filenames[0] and rel.file1 == filenames[i]):
                    relationship = rel
                    break
            
            if relationship and relationship.join_keys:
                # Perform join
                join_key = relationship.join_keys[0]
                join_type = relationship.suggested_join_type
                
                result = result.merge(
                    self.files[filenames[i]],
                    on=join_key,
                    how=join_type,
                    suffixes=('', f'_{i}')
                )
            else:
                # No relationship found - use outer join on index
                result = result.merge(
                    self.files[filenames[i]],
                    left_index=True,
                    right_index=True,
                    how='outer',
                    suffixes=('', f'_{i}')
                )
        
        return result
    
    def compare_schemas(self, filenames: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Compare schemas across files.
        
        Args:
            filenames (Optional[List[str]]): Files to compare. If None, compare all.
        
        Returns:
            pd.DataFrame: Schema comparison table.
        """
        if filenames is None:
            filenames = list(self.files.keys())
        
        # Get all unique columns
        all_columns = set()
        for filename in filenames:
            if filename in self.files:
                all_columns.update(self.files[filename].columns)
        
        # Create comparison matrix
        comparison = {}
        for col in sorted(all_columns):
            comparison[col] = {}
            for filename in filenames:
                if filename in self.files:
                    if col in self.files[filename].columns:
                        dtype = str(self.files[filename][col].dtype)
                        comparison[col][filename] = dtype
                    else:
                        comparison[col][filename] = '-'
        
        return pd.DataFrame(comparison).T
    
    def _generate_schema_hash(self, df: pd.DataFrame) -> str:
        """Generate a hash representing the schema."""
        return '|'.join(sorted(df.columns))
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of imported files.
        
        Returns:
            Dict[str, Any]: Summary information.
        """
        return {
            'total_files': len(self.files),
            'total_rows': sum(info.rows for info in self.file_info.values()),
            'files': {name: {'rows': info.rows, 'columns': info.columns} 
                     for name, info in self.file_info.items()},
            'relationships': len(self.relationships),
            'relationship_details': [
                {
                    'file1': rel.file1,
                    'file2': rel.file2,
                    'common_columns': len(rel.common_columns),
                    'join_type': rel.suggested_join_type
                }
                for rel in self.relationships
            ]
        }
