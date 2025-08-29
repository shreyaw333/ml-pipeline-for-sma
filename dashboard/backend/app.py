# dashboard/backend/app.py
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import json
import os
import glob
from datetime import datetime, timedelta
from collections import Counter
import numpy as np

app = Flask(__name__)
CORS(app)

class DashboardAPI:
    def __init__(self):
        # Fix the path - go up two levels from dashboard/backend/
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
        print(f"Looking for data in: {self.data_dir}")
        
    def load_processed_data(self):
        """Load processed Instagram data"""
        try:
            # Load CSV files from simple processor
            csv_pattern = os.path.join(self.data_dir, "processed", "*.csv")
            csv_files = glob.glob(csv_pattern)
            print(f"Found CSV files: {csv_files}")
            
            if csv_files:
                dfs = []
                for file in csv_files:
                    print(f"Loading file: {file}")
                    df = pd.read_csv(file)
                    dfs.append(df)
                combined_df = pd.concat(dfs, ignore_index=True)
                print(f"Total records loaded: {len(combined_df)}")
                return combined_df
            else:
                print("No CSV files found in processed directory")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error loading processed data: {e}")
            return pd.DataFrame()
    
    def load_trend_report(self):
        """Load trend detection report"""
        try:
            report_path = os.path.join(self.data_dir, "models", "trend_report.json")
            print(f"Looking for trend report at: {report_path}")
            if os.path.exists(report_path):
                with open(report_path, 'r') as f:
                    report = json.load(f)
                    print("Trend report loaded successfully")
                    return report
            else:
                print("Trend report not found")
                return {}
        except Exception as e:
            print(f"Error loading trend report: {e}")
            return {}
    
    def get_live_metrics(self):
        """Calculate live pipeline metrics"""
        df = self.load_processed_data()
        
        if df.empty:
            print("No data available, returning defaults")
            return {
                "total_posts": 0,
                "avg_engagement": 0,
                "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
                "top_hashtags": [],
                "processing_rate": 0
            }
        
        # Calculate metrics
        total_posts = len(df)
        avg_engagement = df['total_engagement'].mean() if 'total_engagement' in df.columns else 0
        
        # Sentiment distribution
        if 'sentiment_hint' in df.columns:
            sentiment_counts = df['sentiment_hint'].value_counts()
            sentiment_dist = {
                "positive": int(sentiment_counts.get('positive', 0)),
                "negative": int(sentiment_counts.get('negative', 0)),
                "neutral": int(sentiment_counts.get('neutral', 0))
            }
        else:
            sentiment_dist = {"positive": 0, "negative": 0, "neutral": 0}
        
        # Calculate processing rate
        processing_rate = 30 if total_posts > 0 else 0  # Default rate from generator
        
        # Get hashtags from actual data
        top_hashtags = []
        if 'content' in df.columns:
            # Extract hashtags from content
            all_hashtags = []
            for content in df['content'].dropna():
                hashtags = [word for word in content.split() if word.startswith('#')]
                all_hashtags.extend(hashtags)
            
            if all_hashtags:
                hashtag_counts = Counter(all_hashtags)
                top_hashtags = [
                    {"hashtag": hashtag, "count": count}
                    for hashtag, count in hashtag_counts.most_common(10)
                ]
        
        # If no hashtags found in content, try trend report
        if not top_hashtags:
            trend_report = self.load_trend_report()
            hashtag_trends = trend_report.get('hashtag_trends', {})
            top_hashtags = [
                {"hashtag": hashtag, "count": data.get("count", 0)}
                for hashtag, data in list(hashtag_trends.items())[:10]
            ]
        
        metrics = {
            "total_posts": total_posts,
            "avg_engagement": round(avg_engagement, 1),
            "sentiment_distribution": sentiment_dist,
            "top_hashtags": top_hashtags,
            "processing_rate": round(processing_rate, 1)
        }
        
        print(f"Returning metrics: {metrics}")
        return metrics

# Initialize API
dashboard_api = DashboardAPI()

@app.route('/')
def index():
    """Serve the dashboard HTML"""
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """Get current pipeline metrics"""
    try:
        metrics = dashboard_api.get_live_metrics()
        return jsonify(metrics)
    except Exception as e:
        print(f"Error in /api/metrics: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        data_available = len(dashboard_api.load_processed_data()) > 0
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "data_available": data_available,
            "data_path": dashboard_api.data_dir
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/debug')
def debug_info():
    """Debug endpoint to check data availability"""
    try:
        df = dashboard_api.load_processed_data()
        trend_report = dashboard_api.load_trend_report()
        
        return jsonify({
            "data_dir": dashboard_api.data_dir,
            "csv_files": glob.glob(os.path.join(dashboard_api.data_dir, "processed", "*.csv")),
            "total_records": len(df),
            "columns": list(df.columns) if not df.empty else [],
            "sample_data": df.head().to_dict('records') if not df.empty else [],
            "trend_report_available": bool(trend_report),
            "trend_report_keys": list(trend_report.keys()) if trend_report else []
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)