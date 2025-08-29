# src/data_processing/feature_engineering.py
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.feature import VectorAssembler
import re

class FeatureEngineer:
    """Advanced feature engineering for Instagram posts"""
    
    @staticmethod
    def sentiment_features(df):
        """Extract sentiment-related features"""
        
        # Positive sentiment words
        positive_words = ["amazing", "awesome", "fantastic", "love", "great", 
                         "beautiful", "perfect", "excellent", "wonderful", "brilliant"]
        
        # Negative sentiment words  
        negative_words = ["terrible", "awful", "hate", "bad", "horrible", 
                         "worst", "disappointing", "annoying", "stupid", "boring"]
        
        # Create positive word count
        positive_pattern = "|".join(positive_words)
        df = df.withColumn(
            "positive_word_count",
            size(split(lower(col("content")), f"\\b({positive_pattern})\\b")) - 1
        )
        
        # Create negative word count
        negative_pattern = "|".join(negative_words)
        df = df.withColumn(
            "negative_word_count", 
            size(split(lower(col("content")), f"\\b({negative_pattern})\\b")) - 1
        )
        
        # Sentiment ratio
        df = df.withColumn(
            "sentiment_ratio",
            when(col("negative_word_count") == 0, col("positive_word_count"))
            .otherwise(col("positive_word_count") / col("negative_word_count"))
        )
        
        return df
    
    @staticmethod
    def engagement_features(df):
        """Create advanced engagement features"""
        
        # Engagement velocity (engagement per hour since posting)
        df = df.withColumn(
            "hours_since_post",
            (unix_timestamp(col("processed_timestamp")) - 
             unix_timestamp(col("timestamp"))) / 3600
        )
        
        df = df.withColumn(
            "engagement_velocity",
            (col("likes") + col("comments") + col("shares") + col("saves")) / 
            greatest(col("hours_since_post"), lit(1))
        )
        
        # Normalized engagement scores
        df = df.withColumn("likes_per_word", col("likes") / greatest(col("word_count"), lit(1)))
        df = df.withColumn("comments_per_word", col("comments") / greatest(col("word_count"), lit(1)))
        
        # Engagement diversity (how distributed the engagement is)
        total_engagement = col("likes") + col("comments") + col("shares") + col("saves")
        df = df.withColumn(
            "engagement_diversity",
            4 - (
                pow(col("likes") / greatest(total_engagement, lit(1)), 2) +
                pow(col("comments") / greatest(total_engagement, lit(1)), 2) +
                pow(col("shares") / greatest(total_engagement, lit(1)), 2) +
                pow(col("saves") / greatest(total_engagement, lit(1)), 2)
            ) * 4
        )
        
        return df
    
    @staticmethod
    def temporal_features(df):
        """Extract time-based features"""
        
        # Peak hours (typically 6-9 AM and 7-9 PM)
        df = df.withColumn(
            "is_peak_hour",
            when((col("hour_of_day").between(6, 9)) | 
                 (col("hour_of_day").between(19, 21)), 1).otherwise(0)
        )
        
        # Weekend posting
        df = df.withColumn(
            "is_weekend", 
            when(col("day_of_week").isin([1, 7]), 1).otherwise(0)  # Sunday=1, Saturday=7
        )
        
        # Business hours
        df = df.withColumn(
            "is_business_hours",
            when(col("hour_of_day").between(9, 17) & 
                 col("day_of_week").between(2, 6), 1).otherwise(0)
        )
        
        return df
    
    @staticmethod
    def content_quality_features(df):
        """Features indicating content quality"""
        
        # Caption completeness (has substantive text beyond hashtags)
        df = df.withColumn(
            "caption_quality_score",
            when(col("word_count") >= 10, 1.0)
            .when(col("word_count") >= 5, 0.7)
            .when(col("word_count") >= 2, 0.4)
            .otherwise(0.1)
        )
        
        # Hashtag optimization (3-11 hashtags is optimal for Instagram)
        df = df.withColumn(
            "hashtag_optimization_score",
            when(col("hashtag_count").between(3, 11), 1.0)
            .when(col("hashtag_count").between(1, 2) | 
                  col("hashtag_count").between(12, 20), 0.7)
            .when(col("hashtag_count") > 20, 0.3)
            .otherwise(0.1)
        )
        
        # Text-to-hashtag ratio
        df = df.withColumn(
            "text_hashtag_ratio",
            col("word_count") / greatest(col("hashtag_count"), lit(1))
        )
        
        return df
    
    @staticmethod
    def create_feature_vector(df, feature_cols=None):
        """Combine all features into a single vector for ML"""
        
        if feature_cols is None:
            feature_cols = [
                "content_length", "hashtag_count", "mention_count", "word_count",
                "exclamation_count", "question_count", "engagement_rate", 
                "positive_word_count", "negative_word_count", "sentiment_ratio",
                "engagement_velocity", "likes_per_word", "engagement_diversity",
                "is_peak_hour", "is_weekend", "is_business_hours",
                "caption_quality_score", "hashtag_optimization_score", "text_hashtag_ratio",
                "hour_of_day", "day_of_week"
            ]
        
        # Add binary hashtag features
        hashtag_features = [f"has_{tag}" for tag in ["love", "instagood", "photooftheday", 
                                                    "fashion", "beautiful", "happy", "cute", "followme"]]
        feature_cols.extend(hashtag_features)
        
        assembler = VectorAssembler(
            inputCols=feature_cols,
            outputCol="features"
        )
        
        return assembler.transform(df)
    
    @staticmethod
    def apply_all_features(df):
        """Apply all feature engineering transformations"""
        return df \
            .transform(FeatureEngineer.sentiment_features) \
            .transform(FeatureEngineer.engagement_features) \
            .transform(FeatureEngineer.temporal_features) \
            .transform(FeatureEngineer.content_quality_features)