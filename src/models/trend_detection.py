# src/models/trend_detection.py
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime, timedelta
import json
import os
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import re

class InstagramTrendDetector:
    def __init__(self, trend_window_hours=24, min_mentions=5):
        self.trend_window_hours = trend_window_hours
        self.min_mentions = min_mentions
        self.hashtag_trends = {}
        self.engagement_trends = {}
        self.content_trends = {}
        
    def load_processed_data(self, data_path="data/processed/instagram_posts"):
        """Load processed Instagram data"""
        try:
            import glob
            parquet_files = glob.glob(f"{data_path}/*.parquet")
            if parquet_files:
                dataframes = []
                for file in parquet_files:
                    df = pd.read_parquet(file)
                    dataframes.append(df)
                return pd.concat(dataframes, ignore_index=True)
            else:
                return self.generate_sample_trend_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            return self.generate_sample_trend_data()
    
    def generate_sample_trend_data(self, n_samples=2000):
        """Generate sample data with trending patterns"""
        np.random.seed(42)
        
        # Trending hashtags with different popularity patterns
        trending_hashtags = {
            '#AI': {'base_freq': 0.3, 'trend_multiplier': 3.0, 'trend_start': 12},
            '#MachineLearning': {'base_freq': 0.2, 'trend_multiplier': 2.5, 'trend_start': 18},
            '#DataScience': {'base_freq': 0.15, 'trend_multiplier': 2.0, 'trend_start': 6},
            '#Tech': {'base_freq': 0.25, 'trend_multiplier': 1.8, 'trend_start': 14},
            '#Innovation': {'base_freq': 0.1, 'trend_multiplier': 2.2, 'trend_start': 10}
        }
        
        regular_hashtags = ['#instagram', '#love', '#photooftheday', '#instagood', 
                           '#beautiful', '#happy', '#fitness', '#food', '#travel']
        
        data = []
        base_time = datetime.now() - timedelta(hours=48)
        
        for i in range(n_samples):
            # Generate timestamp
            timestamp = base_time + timedelta(minutes=i*2)
            hour = timestamp.hour
            
            # Generate hashtags with trending patterns
            post_hashtags = []
            
            # Add trending hashtags based on time
            for hashtag, pattern in trending_hashtags.items():
                base_prob = pattern['base_freq']
                
                # Check if in trending period
                if abs(hour - pattern['trend_start']) <= 3:
                    prob = base_prob * pattern['trend_multiplier']
                else:
                    prob = base_prob
                
                if np.random.random() < prob:
                    post_hashtags.append(hashtag)
            
            # Add random regular hashtags
            n_regular = np.random.poisson(2)
            post_hashtags.extend(np.random.choice(regular_hashtags, min(n_regular, 3), replace=False))
            
            # Generate engagement with trending boost
            base_engagement = np.random.lognormal(4, 1)
            if any(h in trending_hashtags for h in post_hashtags):
                base_engagement *= np.random.uniform(1.5, 3.0)
            
            likes = int(base_engagement * np.random.uniform(0.7, 1.3))
            comments = int(likes * np.random.uniform(0.05, 0.15))
            shares = int(likes * np.random.uniform(0.01, 0.05))
            saves = int(likes * np.random.uniform(0.02, 0.08))
            
            # Generate content
            content_templates = [
                "Amazing day with new discoveries!",
                "Just learned something incredible about",
                "Working on exciting projects in",
                "Breakthrough moment in my",
                "Incredible progress in",
                "New insights about"
            ]
            
            content = np.random.choice(content_templates)
            if post_hashtags:
                content += " " + " ".join(post_hashtags)
            
            data.append({
                'post_id': f'trend_{i}',
                'content': content,
                'cleaned_content': content.lower(),
                'hashtags': post_hashtags,
                'timestamp': timestamp.isoformat(),
                'processed_timestamp': timestamp.isoformat(),
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'saves': saves,
                'hour_of_day': hour,
                'day_of_week': timestamp.weekday() + 1,
                'hashtag_count': len(post_hashtags),
                'total_engagement': likes + comments + shares + saves
            })
        
        return pd.DataFrame(data)
    
    def detect_hashtag_trends(self, df):
        """Detect trending hashtags based on frequency and growth"""
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter recent data
        cutoff_time = df['timestamp'].max() - timedelta(hours=self.trend_window_hours)
        recent_df = df[df['timestamp'] >= cutoff_time]
        
        # Extract all hashtags
        all_hashtags = []
        for hashtags in recent_df['hashtags']:
            if isinstance(hashtags, list):
                all_hashtags.extend(hashtags)
            elif isinstance(hashtags, str) and hashtags.startswith('['):
                # Handle string representation of list
                try:
                    hashtag_list = eval(hashtags)
                    all_hashtags.extend(hashtag_list)
                except:
                    pass
        
        # Count hashtag frequency
        hashtag_counts = Counter(all_hashtags)
        
        # Calculate hashtag growth rate
        hashtag_trends = {}
        
        for hashtag, count in hashtag_counts.items():
            if count >= self.min_mentions:
                # Calculate hourly frequency
                hashtag_posts = recent_df[recent_df['hashtags'].apply(
                    lambda x: hashtag in x if isinstance(x, list) else False
                )]
                
                if len(hashtag_posts) > 0:
                    # Calculate average engagement for this hashtag
                    avg_engagement = hashtag_posts['total_engagement'].mean()
                    
                    # Calculate posting frequency (posts per hour)
                    time_span = (recent_df['timestamp'].max() - recent_df['timestamp'].min()).total_seconds() / 3600
                    frequency = count / max(time_span, 1)
                    
                    # Calculate trend score (combination of frequency and engagement)
                    trend_score = frequency * np.log(avg_engagement + 1)
                    
                    hashtag_trends[hashtag] = {
                        'count': count,
                        'frequency_per_hour': frequency,
                        'avg_engagement': avg_engagement,
                        'trend_score': trend_score,
                        'posts': len(hashtag_posts)
                    }
        
        # Sort by trend score
        sorted_trends = sorted(hashtag_trends.items(), 
                              key=lambda x: x[1]['trend_score'], 
                              reverse=True)
        
        return dict(sorted_trends[:20])  # Top 20 trends
    
    def detect_engagement_patterns(self, df):
        """Detect unusual engagement patterns"""
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['total_engagement'] = df['likes'] + df['comments'] + df['shares'] + df['saves']
        
        # Group by hour to find peak engagement times
        df['hour'] = df['timestamp'].dt.hour
        hourly_engagement = df.groupby('hour')['total_engagement'].agg(['mean', 'count', 'std'])
        
        # Find peak hours (above average engagement)
        avg_engagement = hourly_engagement['mean'].mean()
        peak_hours = hourly_engagement[hourly_engagement['mean'] > avg_engagement * 1.2]
        
        # Detect viral posts (high engagement outliers)
        engagement_threshold = df['total_engagement'].quantile(0.95)
        viral_posts = df[df['total_engagement'] > engagement_threshold].copy()
        
        # Analyze posting patterns
        posting_patterns = {
            'peak_hours': peak_hours.to_dict(),
            'viral_posts': len(viral_posts),
            'avg_engagement_by_hour': hourly_engagement['mean'].to_dict(),
            'total_posts': len(df)
        }
        
        return posting_patterns
    
    def detect_content_trends(self, df, n_clusters=10):
        """Detect trending content themes using text clustering"""
        # Prepare text data
        texts = df['cleaned_content'].fillna('').astype(str)
        
        # Remove hashtags and mentions for content analysis
        cleaned_texts = []
        for text in texts:
            # Remove hashtags and mentions
            clean_text = re.sub(r'#\w+', '', text)
            clean_text = re.sub(r'@\w+', '', clean_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            cleaned_texts.append(clean_text)
        
        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
            
            # K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(tfidf_matrix)
            
            # Analyze clusters
            feature_names = vectorizer.get_feature_names_out()
            content_trends = {}
            
            for i in range(n_clusters):
                cluster_mask = clusters == i
                cluster_posts = df[cluster_mask]
                
                if len(cluster_posts) > 0:
                    # Get top terms for this cluster
                    cluster_center = kmeans.cluster_centers_[i]
                    top_indices = cluster_center.argsort()[-10:][::-1]
                    top_terms = [feature_names[idx] for idx in top_indices]
                    
                    # Calculate cluster stats
                    avg_engagement = cluster_posts['total_engagement'].mean()
                    post_count = len(cluster_posts)
                    
                    content_trends[f'theme_{i}'] = {
                        'top_terms': top_terms,
                        'post_count': post_count,
                        'avg_engagement': avg_engagement,
                        'posts_percentage': post_count / len(df) * 100
                    }
            
            return content_trends
            
        except Exception as e:
            print(f"Error in content trend detection: {e}")
            return {}
    
    def generate_trend_report(self, save_path="data/models/trend_report.json"):
        """Generate comprehensive trend analysis report"""
        print("Loading data for trend analysis...")
        df = self.load_processed_data()
        print(f"Analyzing {len(df)} Instagram posts...")
        
        # Detect different types of trends
        print("Detecting hashtag trends...")
        hashtag_trends = self.detect_hashtag_trends(df)
        
        print("Analyzing engagement patterns...")
        engagement_patterns = self.detect_engagement_patterns(df)
        
        print("Detecting content trends...")
        content_trends = self.detect_content_trends(df)
        
        # Compile report
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'data_period': {
                'start': df['timestamp'].min() if 'timestamp' in df.columns else 'N/A',
                'end': df['timestamp'].max() if 'timestamp' in df.columns else 'N/A',
                'total_posts': len(df)
            },
            'hashtag_trends': hashtag_trends,
            'engagement_patterns': engagement_patterns,
            'content_trends': content_trends,
            'summary': {
                'top_hashtags': list(hashtag_trends.keys())[:5],
                'trending_themes': len(content_trends),
                'peak_engagement_hours': max(engagement_patterns['avg_engagement_by_hour'].items(), 
                                           key=lambda x: x[1])[0] if engagement_patterns['avg_engagement_by_hour'] else None
            }
        }
        
        # Save report
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Trend report saved to {save_path}")
        
        # Print summary
        print(f"\n=== INSTAGRAM TREND ANALYSIS REPORT ===")
        print(f"Analysis Period: {report['data_period']['start']} to {report['data_period']['end']}")
        print(f"Total Posts Analyzed: {report['data_period']['total_posts']}")
        
        print(f"\nTop 5 Trending Hashtags:")
        for i, (hashtag, data) in enumerate(list(hashtag_trends.items())[:5], 1):
            print(f"{i}. {hashtag}: {data['count']} mentions, {data['avg_engagement']:.0f} avg engagement")
        
        if engagement_patterns['peak_hours']:
            print(f"\nPeak Engagement Hours:")
            for hour, data in list(engagement_patterns['peak_hours']['mean'].items())[:3]:
                print(f"  Hour {hour}: {data:.0f} avg engagement")
        
        print(f"\nContent Themes Detected: {len(content_trends)}")
        
        return report

if __name__ == "__main__":
    # Run trend detection
    trend_detector = InstagramTrendDetector()
    report = trend_detector.generate_trend_report()
    
    print("Trend detection analysis completed!")