import sys
import os
# import torch
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ai.models import LapTimePredictor, AnomalyDetector, RaceCoach

def test_ai():
    print("Testing AI Models...")
    
    # Test LapTimePredictor
    model = LapTimePredictor(input_size=5, hidden_size=10)
    dummy_input = np.random.randn(1, 10, 5) # Batch=1, Seq=10, Feat=5
    output = model.forward(dummy_input)
    print(f"LapTimePredictor Output Shape: {output.shape}")
    assert output.shape == (1, 1)
    
    # Test AnomalyDetector
    detector = AnomalyDetector()
    data = np.random.rand(100, 5)
    detector.train(data)
    preds = detector.predict(data[:5])
    print(f"AnomalyDetector Predictions: {preds}")
    assert len(preds) == 5
    
    # Test RaceCoach
    coach = RaceCoach()
    df = pd.DataFrame({
        'NUMBER': [14, 14, 14, 14, 14, 14],
        'TOTAL_TIME_SEC': [90, 181, 272, 363, 454, 545],
        'FL_TIME_SEC': [90, 91, 91, 91, 91, 91]
    })
    insights = coach.analyze_driver(df, 14)
    print("Coach Insights:")
    for i in insights:
        print(f"- {i}")
    assert len(insights) > 0

    print("\nAI Tests Passed!")

if __name__ == "__main__":
    test_ai()
