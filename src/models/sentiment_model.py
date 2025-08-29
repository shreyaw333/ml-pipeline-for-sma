# src/models/sentiment_model.py
import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Embedding, LSTM, GlobalMaxPooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import glob
from datetime import datetime

class InstagramSentimentModel:
    def __init__(self, max_features=10000, max_length=100):
        self.max_features = max_features
        self.max_length = max_length
        self.tokenizer = None
        self.label_encoder = None
        self.model = None
        
    def load_processed_data(self, data_path="data/processed/instagram_posts"):
        """Load processed Instagram data from Spark output"""
        try:
            # Try to read Parquet files from Spark
            parquet_files = glob.glob(f"{data_path}/*.parquet")
            if parquet_files:
                print(f"Loading {len(parquet_files)} Parquet files...")
                dataframes = []
                for file in parquet_files[:5]:  # Limit for training
                    df = pd.read_parquet(file)
                    dataframes.append(df)
                return pd.concat(dataframes, ignore_index=True)
            else:
                print("No Parquet files found. Generating sample data...")
                return self.generate_sample_data()
                
        except Exception as e:
            print(f"Error loading data: {e}")
            print("Generating sample data for training...")
            return self.generate_sample_data()
    
    def generate_sample_data(self, n_samples=1000):
        """Generate sample Instagram data for training if real data not available"""
        np.random.seed(42)
        
        # Sample Instagram captions
        positive_captions = [
            "Amazing day at the beach! #love #beautiful #happy",
            "Just had the best coffee ever! #perfect #morning #blessed",
            "Incredible sunset tonight #gorgeous #nature #peaceful",
            "Love spending time with family #family #happiness #grateful",
            "New workout routine is amazing! #fitness #strong #motivated"
        ]
        
        negative_captions = [
            "Terrible weather ruining my plans #frustrated #annoyed",
            "Worst customer service ever #disappointed #angry",
            "Having an awful day #stressed #upset #bad",
            "Traffic is horrible today #hate #annoying #worst",
            "Food was terrible at this restaurant #disappointed #bad"
        ]
        
        neutral_captions = [
            "Just another day at work #work #office #normal",
            "Regular coffee this morning #coffee #morning #okay",
            "Standard workout session #fitness #gym #routine",
            "Typical Tuesday activities #tuesday #regular #fine",
            "Average weather today #weather #okay #normal"
        ]
        
        data = []
        for i in range(n_samples):
            if i % 3 == 0:
                content = np.random.choice(positive_captions)
                sentiment = 'positive'
            elif i % 3 == 1:
                content = np.random.choice(negative_captions)
                sentiment = 'negative'
            else:
                content = np.random.choice(neutral_captions)
                sentiment = 'neutral'
            
            # Add some variation
            content = content + f" Post number {i}"
            
            data.append({
                'post_id': f'sample_{i}',
                'content': content,
                'cleaned_content': content.lower(),
                'content_length': len(content),
                'hashtag_count': content.count('#'),
                'mention_count': content.count('@'),
                'word_count': len(content.split()),
                'exclamation_count': content.count('!'),
                'likes': np.random.randint(10, 1000),
                'comments': np.random.randint(0, 100),
                'shares': np.random.randint(0, 50),
                'saves': np.random.randint(0, 200),
                'sentiment_hint': sentiment,
                'hour_of_day': np.random.randint(0, 24),
                'day_of_week': np.random.randint(1, 8)
            })
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df):
        """Prepare text and numerical features for training"""
        # Text preprocessing
        texts = df['cleaned_content'].fillna('').astype(str).tolist()
        
        # Tokenize text
        self.tokenizer = Tokenizer(num_words=self.max_features, oov_token="<OOV>")
        self.tokenizer.fit_on_texts(texts)
        
        # Convert texts to sequences
        sequences = self.tokenizer.texts_to_sequences(texts)
        X_text = pad_sequences(sequences, maxlen=self.max_length)
        
        # Numerical features
        numerical_features = [
            'content_length', 'hashtag_count', 'mention_count', 'word_count',
            'exclamation_count', 'likes', 'comments', 'shares', 'saves',
            'hour_of_day', 'day_of_week'
        ]
        
        # Fill missing values and normalize
        for feature in numerical_features:
            if feature not in df.columns:
                df[feature] = 0
        
        X_numerical = df[numerical_features].fillna(0).values
        
        # Normalize numerical features
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_numerical = scaler.fit_transform(X_numerical)
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(df['sentiment_hint'].fillna('neutral'))
        
        return X_text, X_numerical, y, scaler
    
    def build_model(self, num_classes, numerical_features_dim):
        """Build hybrid model combining text and numerical features"""
        # Text input branch
        text_input = tf.keras.Input(shape=(self.max_length,), name='text_input')
        text_embedding = Embedding(self.max_features, 128)(text_input)
        text_lstm = LSTM(64, dropout=0.3, recurrent_dropout=0.3)(text_embedding)
        
        # Numerical input branch
        numerical_input = tf.keras.Input(shape=(numerical_features_dim,), name='numerical_input')
        numerical_dense = Dense(32, activation='relu')(numerical_input)
        numerical_dropout = Dropout(0.3)(numerical_dense)
        
        # Combine branches
        combined = tf.keras.layers.concatenate([text_lstm, numerical_dropout])
        
        # Final layers
        dense1 = Dense(64, activation='relu')(combined)
        dropout1 = Dropout(0.5)(dense1)
        dense2 = Dense(32, activation='relu')(dropout1)
        dropout2 = Dropout(0.3)(dense2)
        output = Dense(num_classes, activation='softmax')(dropout2)
        
        # Create model
        model = tf.keras.Model(inputs=[text_input, numerical_input], outputs=output)
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, epochs=20, batch_size=32, validation_split=0.2):
        """Train the sentiment analysis model"""
        print("Loading and preparing data...")
        df = self.load_processed_data()
        print(f"Loaded {len(df)} Instagram posts")
        
        # Show data distribution
        print("\nSentiment distribution:")
        print(df['sentiment_hint'].value_counts())
        
        # Prepare features
        X_text, X_numerical, y, scaler = self.prepare_features(df)
        num_classes = len(np.unique(y))
        
        print(f"\nFeature shapes:")
        print(f"Text features: {X_text.shape}")
        print(f"Numerical features: {X_numerical.shape}")
        print(f"Labels: {y.shape}")
        print(f"Number of classes: {num_classes}")
        
        # Split data
        X_text_train, X_text_test, X_num_train, X_num_test, y_train, y_test = train_test_split(
            X_text, X_numerical, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Build model
        self.model = self.build_model(num_classes, X_numerical.shape[1])
        print(f"\nModel architecture:")
        self.model.summary()
        
        # Training callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(patience=3, factor=0.5)
        ]
        
        # Train model
        print(f"\nStarting training...")
        history = self.model.fit(
            [X_text_train, X_num_train], y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate model
        print(f"\nEvaluating on test set...")
        test_loss, test_accuracy = self.model.evaluate([X_text_test, X_num_test], y_test)
        print(f"Test accuracy: {test_accuracy:.4f}")
        
        # Detailed evaluation
        y_pred = self.model.predict([X_text_test, X_num_test])
        y_pred_classes = np.argmax(y_pred, axis=1)
        
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred_classes, 
                                  target_names=self.label_encoder.classes_))
        
        # Save model and preprocessing objects
        self.save_model(scaler)
        
        return history
    
    def save_model(self, scaler, model_dir="data/models"):
        """Save trained model and preprocessing objects"""
        os.makedirs(model_dir, exist_ok=True)
        
        # Save model
        model_path = f"{model_dir}/sentiment_model.h5"
        self.model.save(model_path)
        
        # Save preprocessing objects
        with open(f"{model_dir}/tokenizer.pkl", 'wb') as f:
            pickle.dump(self.tokenizer, f)
        
        with open(f"{model_dir}/label_encoder.pkl", 'wb') as f:
            pickle.dump(self.label_encoder, f)
            
        with open(f"{model_dir}/scaler.pkl", 'wb') as f:
            pickle.dump(scaler, f)
        
        print(f"Model saved to {model_path}")
    
    def predict(self, texts, numerical_features):
        """Predict sentiment for new Instagram posts"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Preprocess text
        sequences = self.tokenizer.texts_to_sequences(texts)
        X_text = pad_sequences(sequences, maxlen=self.max_length)
        
        # Predict
        predictions = self.model.predict([X_text, numerical_features])
        predicted_classes = np.argmax(predictions, axis=1)
        predicted_labels = self.label_encoder.inverse_transform(predicted_classes)
        
        return predicted_labels, predictions

if __name__ == "__main__":
    # Train sentiment model
    sentiment_model = InstagramSentimentModel()
    history = sentiment_model.train(epochs=10)
    
    print("Sentiment analysis model training completed!")