import pyodbc
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

# Download the VADER lexicon for sentiment analysis if not already present.
nltk.download('vader_lexicon')

def fetch_data_from_sql():
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost,1433;"
        "Database=PortfolioProject_MarketingAnalytics;"
        "UID=sa;"
        "PWD=YourStrong!Passw0rd;"
        "Trusted_Connection=no;"
    )

    conn = pyodbc.connect(conn_str)
    query = "SELECT ReviewID, CustomerID, ProductID, ReviewDate, Rating, ReviewText FROM dbo.customer_reviews"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fetch the data and display the first few rows
customer_reviews_df = fetch_data_from_sql()
print(customer_reviews_df.head())

# Initialize the VADER sentiment intensity analyzer for analyzing the sentiment of text data
sia = SentimentIntensityAnalyzer()

# Define a function to calculate sentiment scores using VADER
def calculate_sentiment(review):
    sentiment = sia.polarity_scores(review)
    return sentiment['compound']

# Define a function to categorize sentiment using both the sentiment score and the review rating
def categorize_sentiment(score, rating):
    if score > 0.05:
        if rating >= 4:
            return 'Positive'
        elif rating == 3:
            return 'Mixed Positive'
        else:
            return 'Mixed Negative'
    elif score < -0.05:
        if rating <= 2:
            return 'Negative'
        elif rating == 3:
            return 'Mixed Negative'
        else:
            return 'Mixed Positive'
    else:
        if rating >= 4:
            return 'Positive'
        elif rating <= 2:
            return 'Negative'
        else:
            return 'Neutral'

# Define a function to bucket sentiment scores into text ranges
def sentiment_bucket(score):
    if score >= 0.5:
        return '0.5 to 1.0'
    elif 0.0 <= score < 0.5:
        return '0.0 to 0.49'
    elif -0.5 <= score < 0.0:
        return '-0.49 to 0.0'
    else:
        return '-1.0 to -0.5'

# Apply sentiment analysis to calculate sentiment scores for each review
customer_reviews_df['SentimentScore'] = customer_reviews_df['ReviewText'].apply(calculate_sentiment)

# Apply sentiment categorization using both text and rating
customer_reviews_df['SentimentCategory'] = customer_reviews_df.apply(
    lambda row: categorize_sentiment(row['SentimentScore'], row['Rating']), axis=1)

# Apply sentiment bucketing to categorize scores into defined ranges
customer_reviews_df['SentimentBucket'] = customer_reviews_df['SentimentScore'].apply(sentiment_bucket)

# Display the first few rows of the DataFrame with sentiment scores, categories, and buckets
print(customer_reviews_df.head())

# Define the file path to save the CSV file
file_path = '/Users/vanuveer/Desktop/SQL PROJECT/fact_customer_reviews_with_sentiment.csv'

# Save the DataFrame with sentiment scores, categories, and buckets to the CSV file
customer_reviews_df.to_csv(file_path, index=False)

# Print the location of the CSV file
print(f"The CSV file has been saved to: {os.path.abspath(file_path)}")
