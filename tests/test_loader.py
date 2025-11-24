import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.data_loader import DataLoader

def test_loader():
    loader = DataLoader()
    csv_path = os.path.join(os.path.dirname(__file__), 'test_data.csv')
    
    print(f"Testing load from: {csv_path}")
    if loader.load_csv(csv_path):
        print("Load successful.")
        df = loader.preprocess()
        print("\nProcessed Data Head:")
        print(df[['POSITION', 'NUMBER', 'TOTAL_TIME_SEC', 'GAP_FIRST_SEC', 'FL_TIME_SEC']].head())
        
        # Assertions
        assert df.iloc[0]['TOTAL_TIME_SEC'] > 5400 # 1:30:45 is > 5400s
        assert df.iloc[1]['GAP_FIRST_SEC'] == 5.333
        assert df.iloc[2]['GAP_FIRST_SEC'] == 74.985 # 1:14.985 = 60 + 14.985
        print("\nAll checks passed!")
    else:
        print("Load failed.")

if __name__ == "__main__":
    test_loader()
