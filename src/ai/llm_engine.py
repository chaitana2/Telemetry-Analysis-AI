"""
LLM-Powered Analysis Engine

This module integrates a simple LLM interface for natural language
telemetry analysis and improvement recommendations.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import json


class SimpleLLMEngine:
    """
    Simple LLM-like engine for generating natural language insights.
    
    This provides a template-based approach that mimics LLM behavior
    for telemetry analysis. Can be replaced with actual LLM API calls
    (OpenAI, Anthropic, etc.) if needed.
    """
    
    def __init__(self):
        """Initialize the LLM engine."""
        self.context = []
        self.analysis_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load analysis templates."""
        return {
            'lap_time_analysis': {
                'improving': "Great progress! Your lap times are improving. The last lap was {improvement:.2f}s faster than your average. Keep this momentum by maintaining your current racing line and throttle application.",
                'degrading': "I notice your lap times are getting slower. You're now {degradation:.2f}s slower than your best. This could indicate tire degradation or fatigue. Consider: 1) Checking tire pressures, 2) Taking a short break, 3) Reviewing your braking points.",
                'consistent': "Excellent consistency! Your lap times vary by only {variation:.2f}s. This shows good racecraft. To improve further, focus on finding small gains in corner exit speed.",
                'inconsistent': "Your lap times are varying significantly (±{variation:.2f}s). For better consistency: 1) Use consistent braking points, 2) Maintain steady throttle application, 3) Focus on hitting the same apex each lap."
            },
            'speed_analysis': {
                'good_top_speed': "You're reaching good top speeds ({max_speed:.1f} km/h). To maximize this: 1) Optimize your exit from the previous corner, 2) Use all available track width, 3) Ensure smooth throttle application.",
                'low_top_speed': "Your top speed ({max_speed:.1f} km/h) suggests room for improvement. Try: 1) Carrying more speed through corners, 2) Earlier throttle application, 3) Using a lower drag setup if allowed.",
                'speed_variance': "Your speed varies significantly. For smoother driving: 1) Avoid sudden throttle inputs, 2) Brake progressively, 3) Maintain momentum through corners."
            },
            'position_analysis': {
                'gaining': "You're making progress! You've gained {positions} positions. Keep pushing but stay consistent. Focus on: 1) Maintaining your pace, 2) Avoiding mistakes, 3) Looking for overtaking opportunities.",
                'losing': "You've lost {positions} positions. Don't panic - focus on: 1) Getting back into rhythm, 2) Analyzing where you're losing time, 3) Staying calm and avoiding further mistakes.",
                'stable': "You're holding position well. To move forward: 1) Find where competitors are faster, 2) Experiment with different lines, 3) Look for mistakes from drivers ahead."
            },
            'improvement_points': [
                "🏁 **Braking Optimization**: Your braking points could be later. Try braking 5-10m later while maintaining control.",
                "🎯 **Apex Precision**: Focus on hitting the geometric apex consistently. Small variations compound over a lap.",
                "⚡ **Throttle Application**: Apply throttle progressively on corner exit. Smooth = fast.",
                "🔄 **Racing Line**: Use all available track width. Track out wide on exit for better speed.",
                "💨 **Momentum Management**: Maintain minimum speed through corners rather than hard braking.",
                "🎮 **Steering Smoothness**: Reduce steering corrections. Smooth inputs = better tire grip.",
                "⏱️ **Sector Analysis**: Identify your weakest sector and focus practice there.",
                "🔧 **Setup Optimization**: Consider adjusting tire pressures or suspension for better feel.",
                "👀 **Vision**: Look further ahead. Your eyes should be where you want to go, not where you are.",
                "🧘 **Mental Game**: Stay calm and focused. Consistency beats occasional fast laps."
            ]
        }
    
    def analyze_with_instruction(self, data: pd.DataFrame, instruction: str) -> str:
        """
        Analyze data based on plain English instruction.
        
        Args:
            data (pd.DataFrame): Telemetry data
            instruction (str): Plain English instruction
        
        Returns:
            str: Natural language analysis
        """
        instruction_lower = instruction.lower()
        
        # Parse instruction intent
        if any(word in instruction_lower for word in ['improve', 'better', 'faster', 'help']):
            return self._generate_improvement_analysis(data)
        elif any(word in instruction_lower for word in ['lap time', 'laptime', 'time']):
            return self._analyze_lap_times(data)
        elif any(word in instruction_lower for word in ['speed', 'velocity']):
            return self._analyze_speed(data)
        elif any(word in instruction_lower for word in ['position', 'rank', 'place']):
            return self._analyze_position(data)
        elif any(word in instruction_lower for word in ['consistency', 'consistent']):
            return self._analyze_consistency(data)
        else:
            # Default: comprehensive analysis
            return self._generate_comprehensive_analysis(data)
    
    def _generate_improvement_analysis(self, data: pd.DataFrame) -> str:
        """Generate improvement-focused analysis."""
        analysis = "# 🎯 Points of Improvement\n\n"
        analysis += "Based on your telemetry data, here are specific areas to focus on:\n\n"
        
        # Analyze lap times
        lap_time_col = self._find_column(data, ['lap_time', 'laptime', 'fl_time'])
        if lap_time_col:
            lap_times = pd.to_numeric(data[lap_time_col], errors='coerce').dropna()
            
            if len(lap_times) > 1:
                best = lap_times.min()
                avg = lap_times.mean()
                worst = lap_times.max()
                std = lap_times.std()
                
                analysis += f"## ⏱️ Lap Time Analysis\n\n"
                analysis += f"- **Best Lap**: {best:.2f}s\n"
                analysis += f"- **Average**: {avg:.2f}s\n"
                analysis += f"- **Gap to Best**: {avg - best:.2f}s\n\n"
                
                if std > 1.0:
                    analysis += "**🎯 Priority #1: Consistency**\n"
                    analysis += f"Your lap times vary by {std:.2f}s. This is your biggest opportunity!\n\n"
                    analysis += "**Action Steps:**\n"
                    analysis += "1. Use consistent reference points for braking\n"
                    analysis += "2. Aim for the same apex on every lap\n"
                    analysis += "3. Maintain steady throttle application\n"
                    analysis += "4. Practice the same racing line repeatedly\n\n"
                
                if avg - best > 2.0:
                    analysis += "**🚀 Priority #2: Pace**\n"
                    analysis += f"You're {avg - best:.2f}s off your best on average. You CAN go faster!\n\n"
                    analysis += "**Action Steps:**\n"
                    analysis += "1. Study your best lap - what did you do differently?\n"
                    analysis += "2. Brake later (but stay in control)\n"
                    analysis += "3. Carry more minimum speed through corners\n"
                    analysis += "4. Get on throttle earlier on exit\n\n"
        
        # Analyze speed
        speed_col = self._find_column(data, ['speed', 'kph', 'mph'])
        if speed_col:
            speeds = pd.to_numeric(data[speed_col], errors='coerce').dropna()
            
            if len(speeds) > 0:
                analysis += f"## 🏎️ Speed Analysis\n\n"
                analysis += f"- **Top Speed**: {speeds.max():.1f} km/h\n"
                analysis += f"- **Average Speed**: {speeds.mean():.1f} km/h\n\n"
                
                if speeds.std() > 30:
                    analysis += "**💡 Improvement: Smooth Speed Management**\n"
                    analysis += "Your speed varies significantly. Focus on:\n"
                    analysis += "- Progressive braking (not sudden)\n"
                    analysis += "- Smooth throttle application\n"
                    analysis += "- Maintaining momentum through corners\n\n"
        
        # Add general improvement points
        analysis += "## 📚 Key Improvement Areas\n\n"
        
        # Select relevant improvement points
        import random
        selected_points = random.sample(self.analysis_templates['improvement_points'], 5)
        for point in selected_points:
            analysis += f"{point}\n\n"
        
        analysis += "---\n\n"
        analysis += "**Remember**: Focus on one area at a time. Master consistency before chasing speed!\n"
        
        return analysis
    
    def _analyze_lap_times(self, data: pd.DataFrame) -> str:
        """Analyze lap times with natural language."""
        lap_time_col = self._find_column(data, ['lap_time', 'laptime', 'fl_time'])
        
        if not lap_time_col:
            return "I couldn't find lap time data in your telemetry. Please ensure your data includes lap times."
        
        lap_times = pd.to_numeric(data[lap_time_col], errors='coerce').dropna()
        
        if len(lap_times) < 2:
            return "Not enough lap time data to analyze. Please load more laps."
        
        analysis = "# ⏱️ Lap Time Analysis\n\n"
        
        best = lap_times.min()
        avg = lap_times.mean()
        worst = lap_times.max()
        std = lap_times.std()
        
        # Recent trend
        if len(lap_times) >= 5:
            recent_avg = lap_times.tail(5).mean()
            early_avg = lap_times.head(5).mean()
            
            if recent_avg < early_avg:
                improvement = early_avg - recent_avg
                analysis += self.analysis_templates['lap_time_analysis']['improving'].format(
                    improvement=improvement
                ) + "\n\n"
            elif recent_avg > early_avg:
                degradation = recent_avg - early_avg
                analysis += self.analysis_templates['lap_time_analysis']['degrading'].format(
                    degradation=degradation
                ) + "\n\n"
        
        # Consistency analysis
        if std < 0.5:
            analysis += self.analysis_templates['lap_time_analysis']['consistent'].format(
                variation=std
            ) + "\n\n"
        elif std > 1.5:
            analysis += self.analysis_templates['lap_time_analysis']['inconsistent'].format(
                variation=std
            ) + "\n\n"
        
        analysis += f"**Statistics:**\n"
        analysis += f"- Best: {best:.2f}s\n"
        analysis += f"- Average: {avg:.2f}s\n"
        analysis += f"- Worst: {worst:.2f}s\n"
        analysis += f"- Consistency: {std:.2f}s variation\n"
        
        return analysis
    
    def _analyze_speed(self, data: pd.DataFrame) -> str:
        """Analyze speed with natural language."""
        speed_col = self._find_column(data, ['speed', 'kph', 'mph'])
        
        if not speed_col:
            return "I couldn't find speed data in your telemetry."
        
        speeds = pd.to_numeric(data[speed_col], errors='coerce').dropna()
        
        analysis = "# 🏎️ Speed Analysis\n\n"
        
        max_speed = speeds.max()
        avg_speed = speeds.mean()
        
        if max_speed > 200:
            analysis += self.analysis_templates['speed_analysis']['good_top_speed'].format(
                max_speed=max_speed
            ) + "\n\n"
        else:
            analysis += self.analysis_templates['speed_analysis']['low_top_speed'].format(
                max_speed=max_speed
            ) + "\n\n"
        
        if speeds.std() > 40:
            analysis += self.analysis_templates['speed_analysis']['speed_variance'] + "\n\n"
        
        return analysis
    
    def _analyze_position(self, data: pd.DataFrame) -> str:
        """Analyze position changes."""
        position_col = self._find_column(data, ['position', 'pos', 'rank'])
        
        if not position_col:
            return "I couldn't find position data in your telemetry."
        
        positions = pd.to_numeric(data[position_col], errors='coerce').dropna()
        
        if len(positions) < 2:
            return "Not enough position data to analyze."
        
        analysis = "# 🏁 Position Analysis\n\n"
        
        start_pos = positions.iloc[0]
        current_pos = positions.iloc[-1]
        change = start_pos - current_pos  # Positive = gained positions
        
        if change > 0:
            analysis += self.analysis_templates['position_analysis']['gaining'].format(
                positions=int(change)
            ) + "\n\n"
        elif change < 0:
            analysis += self.analysis_templates['position_analysis']['losing'].format(
                positions=int(abs(change))
            ) + "\n\n"
        else:
            analysis += self.analysis_templates['position_analysis']['stable'] + "\n\n"
        
        return analysis
    
    def _analyze_consistency(self, data: pd.DataFrame) -> str:
        """Analyze consistency."""
        lap_time_col = self._find_column(data, ['lap_time', 'laptime'])
        
        if not lap_time_col:
            return "I need lap time data to analyze consistency."
        
        lap_times = pd.to_numeric(data[lap_time_col], errors='coerce').dropna()
        std = lap_times.std()
        
        analysis = "# 🎯 Consistency Analysis\n\n"
        
        if std < 0.5:
            analysis += "**Excellent!** Your consistency is outstanding. "
            analysis += f"Lap times vary by only {std:.2f}s. This is professional-level consistency.\n\n"
        elif std < 1.0:
            analysis += "**Good!** Your consistency is solid. "
            analysis += f"Lap times vary by {std:.2f}s. With minor improvements, you can be even more consistent.\n\n"
        elif std < 2.0:
            analysis += "**Room for Improvement.** Your lap times vary by {std:.2f}s. "
            analysis += "Focus on using consistent reference points and maintaining rhythm.\n\n"
        else:
            analysis += "**Needs Work.** Your lap times vary significantly ({std:.2f}s). "
            analysis += "This is your biggest opportunity for improvement. Focus on consistency before speed.\n\n"
        
        return analysis
    
    def _generate_comprehensive_analysis(self, data: pd.DataFrame) -> str:
        """Generate comprehensive analysis."""
        analysis = "# 📊 Comprehensive Telemetry Analysis\n\n"
        
        analysis += self._analyze_lap_times(data) + "\n\n"
        analysis += self._analyze_speed(data) + "\n\n"
        analysis += "---\n\n"
        analysis += self._generate_improvement_analysis(data)
        
        return analysis
    
    def _find_column(self, df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
        """Find column matching keywords."""
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in keywords):
                return col
        return None


# Example usage
if __name__ == "__main__":
    # Test the LLM engine
    llm = SimpleLLMEngine()
    
    # Create sample data
    sample_data = pd.DataFrame({
        'lap_time': [95.5, 94.8, 96.2, 94.5, 95.1, 97.0, 94.9],
        'speed': [180, 185, 178, 187, 182, 175, 184],
        'position': [5, 5, 4, 4, 3, 3, 3]
    })
    
    # Test different instructions
    print("=" * 70)
    print("TEST: 'How can I improve?'")
    print("=" * 70)
    print(llm.analyze_with_instruction(sample_data, "How can I improve?"))
    
    print("\n" + "=" * 70)
    print("TEST: 'Analyze my lap times'")
    print("=" * 70)
    print(llm.analyze_with_instruction(sample_data, "Analyze my lap times"))
