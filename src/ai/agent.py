"""
AI Agent - Autonomous Telemetry Analysis Agent

This agent automatically:
- Analyzes telemetry data
- Generates insights in real-time
- Creates comprehensive reports
- Provides recommendations
- Monitors performance continuously
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from src.ai.llm_engine import SimpleLLMEngine


@dataclass
class Insight:
    """Represents a single insight."""
    category: str  # 'performance', 'anomaly', 'recommendation', 'warning'
    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    title: str
    description: str
    data: Dict
    timestamp: str
    confidence: float  # 0.0 to 1.0


@dataclass
class AnalysisReport:
    """Comprehensive analysis report."""
    report_id: str
    timestamp: str
    data_summary: Dict
    insights: List[Insight]
    recommendations: List[str]
    performance_metrics: Dict
    anomalies: List[Dict]
    driver_rankings: List[Dict]
    key_findings: List[str]


class TelemetryAIAgent:
    """
    Autonomous AI Agent for Telemetry Analysis.
    
    Capabilities:
    - Automatic data analysis
    - Real-time insight generation
    - Performance monitoring
    - Anomaly detection
    - Report generation
    - Coaching recommendations
    """
    
    def __init__(self):
        """Initialize the AI agent."""
        self.insights = []
        self.reports = []
        self.monitoring_active = False
        self.analysis_history = []
        self.llm_engine = SimpleLLMEngine()  # LLM for natural language analysis
    
    def ask_llm(self, df: pd.DataFrame, question: str) -> str:
        """
        Ask the LLM a question about the data in plain English.
        
        Args:
            df (pd.DataFrame): Telemetry data
            question (str): Plain English question
        
        Returns:
            str: Natural language answer
        """
        return self.llm_engine.analyze_with_instruction(df, question)
        
    def analyze_data(self, df: pd.DataFrame, auto_report: bool = True) -> AnalysisReport:
        """
        Perform comprehensive automated analysis.
        
        Args:
            df (pd.DataFrame): Telemetry data
            auto_report (bool): Automatically generate report
        
        Returns:
            AnalysisReport: Complete analysis report
        """
        print("🤖 AI Agent: Starting automated analysis...")
        
        # Generate report ID
        report_id = f"REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 1. Data Summary
        data_summary = self._analyze_data_summary(df)
        
        # 2. Performance Analysis
        performance_metrics = self._analyze_performance(df)
        
        # 3. Anomaly Detection
        anomalies = self._detect_anomalies(df)
        
        # 4. Driver Rankings
        driver_rankings = self._rank_drivers(df)
        
        # 5. Generate Insights
        insights = self._generate_insights(df, performance_metrics, anomalies)
        
        # 6. Generate Recommendations
        recommendations = self._generate_recommendations(insights, performance_metrics)
        
        # 7. Key Findings
        key_findings = self._extract_key_findings(insights, performance_metrics)
        
        # Create report
        report = AnalysisReport(
            report_id=report_id,
            timestamp=datetime.now().isoformat(),
            data_summary=data_summary,
            insights=insights,
            recommendations=recommendations,
            performance_metrics=performance_metrics,
            anomalies=anomalies,
            driver_rankings=driver_rankings,
            key_findings=key_findings
        )
        
        self.reports.append(report)
        
        if auto_report:
            self._save_report(report)
        
        print(f"✅ Analysis complete! Generated {len(insights)} insights")
        
        return report
    
    def _analyze_data_summary(self, df: pd.DataFrame) -> Dict:
        """Analyze data summary statistics."""
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': len(df.select_dtypes(include=['object']).columns),
            'missing_values': int(df.isna().sum().sum()),
            'duplicate_rows': int(df.duplicated().sum()),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
        }
    
    def _analyze_performance(self, df: pd.DataFrame) -> Dict:
        """Analyze performance metrics."""
        metrics = {}
        
        # Find relevant columns
        lap_time_col = self._find_column(df, ['lap_time', 'laptime', 'fl_time'])
        speed_col = self._find_column(df, ['speed', 'kph', 'mph'])
        position_col = self._find_column(df, ['position', 'pos'])
        
        if lap_time_col:
            lap_times = pd.to_numeric(df[lap_time_col], errors='coerce').dropna()
            metrics['lap_time'] = {
                'mean': float(lap_times.mean()),
                'median': float(lap_times.median()),
                'std': float(lap_times.std()),
                'min': float(lap_times.min()),
                'max': float(lap_times.max()),
                'consistency': float(1 / (lap_times.std() + 1))  # Higher = more consistent
            }
        
        if speed_col:
            speeds = pd.to_numeric(df[speed_col], errors='coerce').dropna()
            metrics['speed'] = {
                'mean': float(speeds.mean()),
                'max': float(speeds.max()),
                'min': float(speeds.min()),
                'std': float(speeds.std())
            }
        
        if position_col:
            positions = pd.to_numeric(df[position_col], errors='coerce').dropna()
            metrics['position'] = {
                'best': int(positions.min()),
                'worst': int(positions.max()),
                'average': float(positions.mean()),
                'final': int(positions.iloc[-1]) if len(positions) > 0 else None
            }
        
        return metrics
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict]:
        """Detect anomalies in the data."""
        anomalies = []
        
        # Check numeric columns for outliers
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols[:10]:  # Limit to first 10 numeric columns
            data = df[col].dropna()
            if len(data) < 10:
                continue
            
            # IQR method
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            
            if len(outliers) > 0:
                anomalies.append({
                    'column': col,
                    'type': 'statistical_outlier',
                    'count': int(len(outliers)),
                    'percentage': float(len(outliers) / len(data) * 100),
                    'severity': 'high' if len(outliers) / len(data) > 0.1 else 'medium'
                })
        
        return anomalies
    
    def _rank_drivers(self, df: pd.DataFrame) -> List[Dict]:
        """Rank drivers by performance."""
        driver_col = self._find_column(df, ['driver', 'driver_name'])
        lap_time_col = self._find_column(df, ['lap_time', 'laptime', 'fl_time'])
        
        if not driver_col or not lap_time_col:
            return []
        
        # Calculate average lap time per driver
        driver_stats = df.groupby(driver_col).agg({
            lap_time_col: ['mean', 'min', 'std', 'count']
        }).reset_index()
        
        driver_stats.columns = ['driver', 'avg_lap_time', 'best_lap_time', 'consistency', 'laps']
        driver_stats = driver_stats.sort_values('avg_lap_time')
        
        rankings = []
        for idx, row in driver_stats.iterrows():
            rankings.append({
                'rank': idx + 1,
                'driver': str(row['driver']),
                'avg_lap_time': float(row['avg_lap_time']),
                'best_lap_time': float(row['best_lap_time']),
                'consistency': float(row['consistency']),
                'laps': int(row['laps'])
            })
        
        return rankings
    
    def _generate_insights(self, df: pd.DataFrame, metrics: Dict, anomalies: List[Dict]) -> List[Insight]:
        """Generate intelligent insights."""
        insights = []
        timestamp = datetime.now().isoformat()
        
        # Performance insights
        if 'lap_time' in metrics:
            lap_metrics = metrics['lap_time']
            
            # Consistency insight
            if lap_metrics['consistency'] > 0.8:
                insights.append(Insight(
                    category='performance',
                    severity='info',
                    title='Excellent Consistency',
                    description=f"Lap time consistency is very high ({lap_metrics['consistency']:.2f}). Driver maintains steady pace.",
                    data={'consistency': lap_metrics['consistency']},
                    timestamp=timestamp,
                    confidence=0.95
                ))
            elif lap_metrics['consistency'] < 0.5:
                insights.append(Insight(
                    category='performance',
                    severity='medium',
                    title='Inconsistent Lap Times',
                    description=f"Lap time consistency is low ({lap_metrics['consistency']:.2f}). Focus on maintaining steady pace.",
                    data={'consistency': lap_metrics['consistency']},
                    timestamp=timestamp,
                    confidence=0.90
                ))
            
            # Speed insight
            if lap_metrics['std'] > lap_metrics['mean'] * 0.1:
                insights.append(Insight(
                    category='warning',
                    severity='medium',
                    title='High Lap Time Variation',
                    description=f"Lap times vary significantly (σ={lap_metrics['std']:.2f}s). Investigate causes.",
                    data={'std': lap_metrics['std'], 'mean': lap_metrics['mean']},
                    timestamp=timestamp,
                    confidence=0.85
                ))
        
        # Anomaly insights
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                insights.append(Insight(
                    category='anomaly',
                    severity='high',
                    title=f"Anomalies Detected in {anomaly['column']}",
                    description=f"Found {anomaly['count']} outliers ({anomaly['percentage']:.1f}%) in {anomaly['column']}",
                    data=anomaly,
                    timestamp=timestamp,
                    confidence=0.80
                ))
        
        # Data quality insights
        missing_pct = df.isna().sum().sum() / (len(df) * len(df.columns)) * 100
        if missing_pct > 5:
            insights.append(Insight(
                category='warning',
                severity='medium',
                title='Missing Data Detected',
                description=f"{missing_pct:.1f}% of data is missing. Consider data cleaning.",
                data={'missing_percentage': missing_pct},
                timestamp=timestamp,
                confidence=0.95
            ))
        
        return insights
    
    def _generate_recommendations(self, insights: List[Insight], metrics: Dict) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Based on insights
        for insight in insights:
            if insight.category == 'performance' and insight.severity == 'medium':
                if 'consistency' in insight.data:
                    recommendations.append(
                        "🎯 Focus on consistency: Practice maintaining steady lap times through rhythm drills"
                    )
            
            if insight.category == 'anomaly' and insight.severity == 'high':
                recommendations.append(
                    f"🔍 Investigate anomalies in {insight.data.get('column', 'data')}: Review telemetry for unusual patterns"
                )
        
        # Based on metrics
        if 'lap_time' in metrics:
            if metrics['lap_time']['std'] > 2.0:
                recommendations.append(
                    "⏱️ Reduce lap time variation: Work on corner entry/exit consistency"
                )
        
        if 'speed' in metrics:
            if metrics['speed']['std'] > 20:
                recommendations.append(
                    "🏎️ Optimize speed management: Smooth throttle application in corners"
                )
        
        # General recommendations
        recommendations.append(
            "📊 Regular data review: Analyze telemetry after each session for continuous improvement"
        )
        
        return recommendations
    
    def _extract_key_findings(self, insights: List[Insight], metrics: Dict) -> List[str]:
        """Extract key findings from analysis."""
        findings = []
        
        # Top insights
        critical_insights = [i for i in insights if i.severity in ['critical', 'high']]
        if critical_insights:
            findings.append(f"⚠️ {len(critical_insights)} critical issues require immediate attention")
        
        # Performance summary
        if 'lap_time' in metrics:
            findings.append(
                f"⏱️ Average lap time: {metrics['lap_time']['mean']:.2f}s "
                f"(Best: {metrics['lap_time']['min']:.2f}s)"
            )
        
        if 'position' in metrics:
            findings.append(
                f"🏁 Position: Best {metrics['position']['best']}, "
                f"Average {metrics['position']['average']:.1f}"
            )
        
        # Consistency
        if 'lap_time' in metrics:
            consistency = metrics['lap_time']['consistency']
            if consistency > 0.8:
                findings.append("✅ Excellent consistency maintained throughout session")
            elif consistency < 0.5:
                findings.append("⚠️ Inconsistent performance - focus area for improvement")
        
        return findings
    
    def _find_column(self, df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
        """Find column matching keywords."""
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in keywords):
                return col
        return None
    
    def _save_report(self, report: AnalysisReport):
        """Save report to file."""
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"{report.report_id}.json"
        
        # Convert to dict
        report_dict = {
            'report_id': report.report_id,
            'timestamp': report.timestamp,
            'data_summary': report.data_summary,
            'insights': [asdict(i) for i in report.insights],
            'recommendations': report.recommendations,
            'performance_metrics': report.performance_metrics,
            'anomalies': report.anomalies,
            'driver_rankings': report.driver_rankings,
            'key_findings': report.key_findings
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        print(f"📄 Report saved: {report_file}")
    
    def generate_real_time_insights(self, df: pd.DataFrame, window_size: int = 10) -> List[Insight]:
        """
        Generate real-time insights on streaming data.
        
        Args:
            df (pd.DataFrame): Latest data window
            window_size (int): Number of recent rows to analyze
        
        Returns:
            List[Insight]: Real-time insights
        """
        insights = []
        timestamp = datetime.now().isoformat()
        
        # Analyze recent data
        recent_data = df.tail(window_size)
        
        # Check for sudden changes
        lap_time_col = self._find_column(df, ['lap_time', 'laptime'])
        if lap_time_col:
            recent_times = pd.to_numeric(recent_data[lap_time_col], errors='coerce').dropna()
            
            if len(recent_times) >= 2:
                # Check for improvement
                if recent_times.iloc[-1] < recent_times.iloc[0]:
                    improvement = recent_times.iloc[0] - recent_times.iloc[-1]
                    insights.append(Insight(
                        category='performance',
                        severity='info',
                        title='Lap Time Improving',
                        description=f"Lap time improved by {improvement:.2f}s in last {window_size} laps",
                        data={'improvement': float(improvement)},
                        timestamp=timestamp,
                        confidence=0.90
                    ))
                
                # Check for degradation
                elif recent_times.iloc[-1] > recent_times.iloc[0] * 1.05:
                    degradation = recent_times.iloc[-1] - recent_times.iloc[0]
                    insights.append(Insight(
                        category='warning',
                        severity='medium',
                        title='Lap Time Degrading',
                        description=f"Lap time increased by {degradation:.2f}s - possible tire wear or fatigue",
                        data={'degradation': float(degradation)},
                        timestamp=timestamp,
                        confidence=0.85
                    ))
        
        return insights
    
    def format_report_text(self, report: AnalysisReport) -> str:
        """Format report as readable text."""
        text = f"""
╔══════════════════════════════════════════════════════════════╗
║                    TELEMETRY ANALYSIS REPORT                  ║
╚══════════════════════════════════════════════════════════════╝

Report ID: {report.report_id}
Generated: {report.timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DATA SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Rows: {report.data_summary['total_rows']:,}
Total Columns: {report.data_summary['total_columns']}
Missing Values: {report.data_summary['missing_values']:,}
Duplicate Rows: {report.data_summary['duplicate_rows']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 KEY FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for finding in report.key_findings:
            text += f"{finding}\n"
        
        text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 INSIGHTS ({len(report.insights)})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for insight in report.insights[:10]:  # Top 10 insights
            text += f"[{insight.severity.upper()}] {insight.title}\n"
            text += f"  {insight.description}\n"
            text += f"  Confidence: {insight.confidence:.0%}\n\n"
        
        text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for rec in report.recommendations:
            text += f"{rec}\n"
        
        if report.driver_rankings:
            text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 DRIVER RANKINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            for ranking in report.driver_rankings[:5]:  # Top 5
                text += f"{ranking['rank']}. {ranking['driver']} - Avg: {ranking['avg_lap_time']:.2f}s\n"
        
        text += "\n" + "═" * 64 + "\n"
        
        return text
