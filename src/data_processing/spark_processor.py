# src/data_processing/spark_processor.py
import os
import json
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
from pyspark.ml import Pipeline

class InstagramDataProcessor:
    def __init__(self, kafka_servers="localhost:9092", batch_duration=10):
        """Initialize Spark session with Kafka support"""
        self.kafka_servers = kafka_servers
        self.batch_duration = batch_duration
        
        # Configure Spark session
        self.spark = SparkSession.builder \
            .appName("InstagramAnalytics") \
            .config("spark.jars.packages", 
                   "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        
        # Define schema for Instagram posts
        self.post_schema = StructType([
            StructField("post_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("username", StringType(), True),
            StructField("content", StringType(), True),
            StructField("platform", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("hashtags", ArrayType(StringType()), True),
            StructField("mentions", ArrayType(StringType()), True),
            StructField("likes", IntegerType(), True),
            StructField("comments", IntegerType(), True),
            StructField("shares", IntegerType(), True),
            StructField("saves", IntegerType(), True),
            StructField("location", StringType(), True),
            StructField("language", StringType(), True),
            StructField("has_image", BooleanType(), True),
            StructField("image_url", StringType(), True),
            StructField("sentiment_hint", StringType(), True)
        ])
    
    def read_kafka_stream(self, topic="social_media_posts"):
        """Read streaming data from Kafka"""
        return self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_servers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .load()
    
    def parse_instagram_posts(self, kafka_df):
        """Parse JSON messages from Kafka into structured DataFrame"""
        return kafka_df \
            .select(from_json(col("value").cast("string"), self.post_schema).alias("post")) \
            .select("post.*") \
            .withColumn("processed_timestamp", current_timestamp())
    
    def clean_text(self, df):
        """Clean and preprocess text content"""
        # UDF for text cleaning
        def clean_text_content(text):
            if not text:
                return ""
            # Remove URLs
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            # Remove special characters but keep hashtags and mentions
            text = re.sub(r'[^\w\s#@]', '', text)
            return text.strip().lower()
        
        clean_text_udf = udf(clean_text_content, StringType())
        
        return df.withColumn("cleaned_content", clean_text_udf(col("content")))
    
    def extract_features(self, df):
        """Engineer features for ML models"""
        return df \
            .withColumn("content_length", length(col("cleaned_content"))) \
            .withColumn("hashtag_count", size(col("hashtags"))) \
            .withColumn("mention_count", size(col("mentions"))) \
            .withColumn("engagement_rate", 
                       (col("likes") + col("comments") + col("shares") + col("saves")) / 
                       greatest(col("likes"), lit(1))) \
            .withColumn("hour_of_day", hour(col("processed_timestamp"))) \
            .withColumn("day_of_week", dayofweek(col("processed_timestamp"))) \
            .withColumn("has_location", col("location").isNotNull()) \
            .withColumn("word_count", size(split(col("cleaned_content"), " "))) \
            .withColumn("exclamation_count", 
                       length(col("content")) - length(regexp_replace(col("content"), "!", ""))) \
            .withColumn("question_count",
                       length(col("content")) - length(regexp_replace(col("content"), "\\?", "")))
    
    def extract_hashtag_features(self, df):
        """Extract popular hashtags and create features"""
        # Convert hashtags array to string for processing
        df_with_hashtag_text = df.withColumn(
            "hashtag_text", 
            concat_ws(" ", col("hashtags"))
        )
        
        # Create binary features for popular hashtags
        popular_hashtags = ["#love", "#instagood", "#photooftheday", "#fashion", 
                          "#beautiful", "#happy", "#cute", "#followme"]
        
        for hashtag in popular_hashtags:
            clean_name = hashtag.replace("#", "has_")
            df_with_hashtag_text = df_with_hashtag_text.withColumn(
                clean_name,
                when(array_contains(col("hashtags"), hashtag), 1).otherwise(0)
            )
        
        return df_with_hashtag_text
    
    def create_text_features(self, df):
        """Create TF-IDF features from text content"""
        # Tokenization
        tokenizer = Tokenizer(inputCol="cleaned_content", outputCol="words")
        
        # Remove stop words
        stop_words_remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
        
        # TF-IDF
        hashing_tf = HashingTF(inputCol="filtered_words", outputCol="raw_features", numFeatures=1000)
        idf = IDF(inputCol="raw_features", outputCol="text_features")
        
        # Create pipeline
        pipeline = Pipeline(stages=[tokenizer, stop_words_remover, hashing_tf, idf])
        
        return pipeline
    
    def process_batch(self, df, epoch_id):
        """Process each micro-batch"""
        if df.count() > 0:
            print(f"Processing batch {epoch_id} with {df.count()} records")
            
            # Apply all transformations
            processed_df = df \
                .transform(self.clean_text) \
                .transform(self.extract_features) \
                .transform(self.extract_hashtag_features)
            
            # Show sample results
            print("Sample processed records:")
            processed_df.select(
                "post_id", "cleaned_content", "content_length", 
                "hashtag_count", "engagement_rate", "sentiment_hint"
            ).show(5, truncate=False)
            
            # Save to storage (Parquet format)
            processed_df.write \
                .mode("append") \
                .parquet("data/processed/instagram_posts")
            
            print(f"Batch {epoch_id} processed and saved")
    
    def start_streaming(self):
        """Start the streaming processing pipeline"""
        print("Starting Instagram data processing pipeline...")
        
        # Read from Kafka
        kafka_stream = self.read_kafka_stream()
        
        # Parse Instagram posts
        instagram_stream = self.parse_instagram_posts(kafka_stream)
        
        # Start streaming query
        query = instagram_stream.writeStream \
            .foreachBatch(self.process_batch) \
            .outputMode("append") \
            .trigger(processingTime=f"{self.batch_duration} seconds") \
            .option("checkpointLocation", "data/checkpoints/instagram_processing") \
            .start()
        
        print(f"Streaming started. Processing batches every {self.batch_duration} seconds...")
        print("Press Ctrl+C to stop")
        
        try:
            query.awaitTermination()
        except KeyboardInterrupt:
            print("Stopping streaming...")
            query.stop()
            self.spark.stop()

if __name__ == "__main__":
    processor = InstagramDataProcessor()
    processor.start_streaming()