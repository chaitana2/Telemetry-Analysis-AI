"""
Analysis Summary Generator

Creates a comprehensive HTML dashboard summarizing all analysis results.
"""

import os
import json
from pathlib import Path
from datetime import datetime

def generate_html_summary(reports_dir: str, output_file: str):
    """Generate an HTML summary of all reports."""
    
    # Find all PDF reports
    pdf_reports = []
    for root, dirs, files in os.walk(reports_dir):
        for file in files:
            if file.endswith('.pdf'):
                rel_path = os.path.relpath(os.path.join(root, file), reports_dir)
                size_mb = os.path.getsize(os.path.join(root, file)) / (1024 * 1024)
                pdf_reports.append({
                    'name': file,
                    'path': rel_path,
                    'size_mb': size_mb,
                    'category': os.path.dirname(rel_path)
                })
    
    # Group by category
    categories = {}
    for report in pdf_reports:
        cat = report['category'] if report['category'] else 'Root'
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(report)
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telemetry Analysis Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            margin-bottom: 2rem;
        }}
        
        h1 {{
            color: #2d3748;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: #718096;
            font-size: 1.1rem;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        .category-section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            margin-bottom: 2rem;
        }}
        
        .category-title {{
            color: #2d3748;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #667eea;
        }}
        
        .report-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        
        .report-card {{
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .report-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            border-color: #667eea;
        }}
        
        .report-name {{
            color: #2d3748;
            font-weight: 600;
            margin-bottom: 0.5rem;
            word-break: break-word;
        }}
        
        .report-meta {{
            color: #718096;
            font-size: 0.85rem;
        }}
        
        .download-btn {{
            display: inline-block;
            margin-top: 0.5rem;
            padding: 0.5rem 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }}
        
        .download-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 2rem;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏁 Telemetry Analysis Dashboard</h1>
            <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(pdf_reports)}</div>
                    <div class="stat-label">Total Reports</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(categories)}</div>
                    <div class="stat-label">Categories</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(r['size_mb'] for r in pdf_reports):.1f} MB</div>
                    <div class="stat-label">Total Size</div>
                </div>
            </div>
        </div>
"""
    
    # Add category sections
    for category, reports in sorted(categories.items()):
        html += f"""
        <div class="category-section">
            <h2 class="category-title">📊 {category}</h2>
            <div class="report-grid">
"""
        
        for report in sorted(reports, key=lambda x: x['name']):
            html += f"""
                <div class="report-card">
                    <div class="report-name">{report['name']}</div>
                    <div class="report-meta">Size: {report['size_mb']:.2f} MB</div>
                    <a href="{report['path']}" class="download-btn" download>📥 Download Report</a>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
    
    html += """
        <div class="footer">
            <p>Automated Telemetry Analysis System | Powered by AI</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"HTML dashboard generated: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_html_summary("reports", "reports/dashboard.html")
