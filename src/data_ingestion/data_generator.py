# data_generator.py
import json
import random
import time
from datetime import datetime, timedelta
from faker import Faker
from kafka import KafkaProducer
import uuid

fake = Faker()

# Instagram-focused platform and hashtags
PLATFORMS = ['instagram']  # Focus on Instagram only
HASHTAGS = [
    '#instagram', '#instagood', '#photooftheday', '#love', '#fashion',
    '#beautiful', '#happy', '#cute', '#tbt', '#like4like',
    '#followme', '#picoftheday', '#follow', '#me', '#selfie',
    '#summer', '#art', '#instadaily', '#friends', '#repost',
    '#nature', '#fun', '#style', '#smile', '#food', '#instalike',
    '#family', '#travel', '#fitness', '#life', '#beauty'
]

SENTIMENT_WORDS = {
    'positive': ['amazing', 'fantastic', 'love', 'great', 'awesome', 'brilliant', 'excellent', 'wonderful'],
    'negative': ['terrible', 'awful', 'hate', 'bad', 'horrible', 'disappointing', 'worst', 'annoying'],
    'neutral': ['okay', 'fine', 'normal', 'standard', 'average', 'regular', 'typical', 'usual']
}

class SocialMediaDataGenerator:
    def __init__(self, kafka_host='localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_host],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8')
        )
        
    def generate_post(self):
        """Generate a realistic Instagram post"""
        platform = 'instagram'
        
        # Instagram-style content (shorter, more visual-focused)
        post_types = [
            f"Just posted a new photo! {fake.sentence()}",
            f"Loving this moment 📸 {fake.sentence()}",
            f"Check out my latest! {fake.sentence()}",
            f"Feeling grateful today ✨ {fake.sentence()}",
            f"Amazing day! {fake.sentence()}",
            f"New post alert! {fake.sentence()}"
        ]
        
        content = random.choice(post_types)
        
        # Add sentiment bias
        sentiment_type = random.choices(['positive', 'negative', 'neutral'], weights=[0.6, 0.1, 0.3])[0]
        sentiment_word = random.choice(SENTIMENT_WORDS[sentiment_type])
        
        if sentiment_type == 'positive':
            content = content.replace('!', f'! {sentiment_word.capitalize()}!')
        elif sentiment_type == 'negative':
            content = f"{sentiment_word.capitalize()}... {content.lower()}"
        
        
        hashtags = []
        if random.random() < 0.7:
            num_hashtags = random.randint(3, 8)  
            hashtags = random.sample(HASHTAGS, min(num_hashtags, len(HASHTAGS)))
            content += '\n\n' + ' '.join(hashtags)
        
        
        mentions = []
        if random.random() < 0.3:
            num_mentions = random.randint(1, 3)
            mentions = [f"@{fake.user_name()}" for _ in range(num_mentions)]
            content += f"\n📸 with {' '.join(mentions)}"
        
        post = {
            'post_id': str(uuid.uuid4()),
            'user_id': str(uuid.uuid4()),
            'username': fake.user_name(),
            'content': content,
            'platform': platform,
            'timestamp': datetime.now().isoformat(),
            'hashtags': hashtags,
            'mentions': mentions,
            'likes': random.randint(10, 5000),  # Instagram engagement
            'comments': random.randint(0, 200),
            'shares': random.randint(0, 50),
            'saves': random.randint(0, 100),  # Instagram-specific
            'location': fake.city() if random.random() < 0.4 else None,
            'language': 'en',
            'has_image': True,  # Instagram posts always have images
            'image_url': f"https://picsum.photos/400/400?random={random.randint(1,1000)}",
            'sentiment_hint': sentiment_type
        }
        
        return post
    
    def stream_data(self, topic='social_media_posts', posts_per_minute=60):
        """Stream generated posts to Kafka"""
        print(f"Starting data stream to topic '{topic}' at {posts_per_minute} posts/minute")
        
        interval = 60 / posts_per_minute  # seconds between posts
        
        try:
            while True:
                post = self.generate_post()
                
                # Send to Kafka
                self.producer.send(
                    topic,
                    key=post['post_id'],
                    value=post
                )
                
                print(f"Sent post: {post['post_id']} - {post['content'][:50]}...")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("Stopping data generator...")
            self.producer.close()

if __name__ == "__main__":
    generator = SocialMediaDataGenerator()
    
    # Generate sample posts for testing
    print("Sample posts:")
    for i in range(3):
        post = generator.generate_post()
        print(f"\nPost {i+1}:")
        print(json.dumps(post, indent=2))
    
    # Start streaming
    generator.stream_data(posts_per_minute=30)