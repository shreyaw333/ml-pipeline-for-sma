# src/data_processing/simple_processor.py
import json
import pandas as pd
import re
from kafka import KafkaConsumer
from datetime import datetime
import time

class SimpleInstagramProcessor:
    def __init__(self, kafka_servers="localhost:9092"):
        self.kafka_servers = kafka_servers
        self.consumer = KafkaConsumer(
            'social_media_posts',
            bootstrap_servers=[kafka_servers],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest'
        )
        
    def clean_text(self, text):
        """Clean text content"""
        if not text:
            return ""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip().lower()
    
    def extract_features(self, post):
        """Extract features from Instagram post"""
        content = post.get('content', '')
        cleaned_content = self.clean_text(content)
        
        # Basic features
        features = {
            'post_id': post.get('post_id'),
            'username': post.get('username'),
            'content': content,
            'cleaned_content': cleaned_content,
            'content_length': len(cleaned_content),
            'word_count': len(cleaned_content.split()),
            'hashtag_count': len(post.get('hashtags', [])),
            'mention_count': len(post.get('mentions', [])),
            'likes': post.get('likes', 0),
            'comments': post.get('comments', 0),
            'shares': post.get('shares', 0),
            'saves': post.get('saves', 0),
            'location': post.get('location'),
            'timestamp': post.get('timestamp'),
            'sentiment_hint': post.get('sentiment_hint')
        }
        
        # Engagement features
        total_engagement = features['likes'] + features['comments'] + features['shares'] + features['saves']
        features['total_engagement'] = total_engagement
        features['engagement_rate'] = total_engagement / max(features['likes'], 1)
        
        # Content features
        features['exclamation_count'] = content.count('!')
        features['question_count'] = content.count('?')
        
        # Sentiment features
        positive_words = ['amazing', 'awesome', 'love', 'great', 'beautiful', 'perfect']
        negative_words = ['terrible', 'awful', 'hate', 'bad', 'horrible', 'worst']
        
        features['positive_word_count'] = sum(1 for word in positive_words if word in cleaned_content)
        features['negative_word_count'] = sum(1 for word in negative_words if word in cleaned_content)
        
        # Time features
        if post.get('timestamp'):
            dt = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
            features['hour_of_day'] = dt.hour
            features['day_of_week'] = dt.weekday()
        
        return features
    
    def process_posts(self, batch_size=10):
        """Process posts in batches"""
        print("Starting Instagram post processing...")
        print("Waiting for posts from Kafka...")
        
        batch = []
        
        try:
            for message in self.consumer:
                post = message.value
                features = self.extract_features(post)
                batch.append(features)
                
                print(f"Processed post {features['post_id'][:8]}... - {features['content'][:50]}...")
                
                # Process batch when it reaches batch_size
                if len(batch) >= batch_size:
                    self.save_batch(batch)
                    batch = []
                    
        except KeyboardInterrupt:
            print("Stopping processor...")
            if batch:
                self.save_batch(batch)
    
    def save_batch(self, batch):
        """Save batch to CSV"""
        df = pd.DataFrame(batch)
        
        # Save to CSV (append mode)
        filename = f"../../data/processed/instagram_features_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)
        
        print(f"Saved batch of {len(batch)} posts to {filename}")
        
        # Show sample
        print("\nSample features:")
        print(df[['post_id', 'content_length', 'hashtag_count', 'total_engagement', 'sentiment_hint']].head())
        print("-" * 50)

if __name__ == "__main__":
    processor = SimpleInstagramProcessor()
    processor.process_posts(batch_size=5)