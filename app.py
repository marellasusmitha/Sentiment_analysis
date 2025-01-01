import streamlit as st
import pandas as pd
from textblob import TextBlob
import tweepy

# Twitter API credentials
API_KEY = "MUxiI8w3dBJpkIsx0EU2LuVO8"
API_SECRET = "LIwERqK1o0xlqWEt4kyhqila5jbCSoMOdXHXcC3oIOJwyS9kUs"
ACCESS_TOKEN = "1672263600499732480-SVxpO4VUefD6SUCRgljiKiE4kntm1g"
ACCESS_SECRET = "q3j4YXfWGFE9KBrlDaaUGjqEWsMo2LTekizUZmvP3iLpt"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAEcCxwEAAAAAI9PWArxdkH25BFF5l5O3AvCWVMQ%3DV3wm4YS9FZeRc1YawAbzVwyL816TlPCzdXCJBXW1siaSdjwra4"

# Authenticate with Twitter API
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# App title
st.title("Twitter Sentiment Analysis App")

# Sidebar for input method selection
st.sidebar.title("Input Options")
input_method = st.sidebar.radio("Choose Input Method:", ("Enter a Tweet", "Upload a Dataset", "Fetch Tweets"))

if input_method == "Enter a Tweet":
    # Text input for a single tweet
    user_input = st.text_area("Enter your tweet:")
    if st.button("Analyze Tweet"):
        if user_input.strip():
            # Perform sentiment analysis
            analysis = TextBlob(user_input)
            sentiment = analysis.sentiment.polarity
            sentiment_label = "Positive 😊" if sentiment > 0 else ("Negative 😔" if sentiment < 0 else "Neutral 😐")
            
            # Display results
            st.write(f"You entered: {user_input}")
            st.write(f"Sentiment Score: {sentiment}")
            st.write(f"Sentiment: {sentiment_label}")
        else:
            st.warning("Please enter a tweet.")

elif input_method == "Upload a Dataset":
    # File uploader for CSV or Excel
    uploaded_file = st.file_uploader("Upload a file containing tweets", type=["csv", "xlsx"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.write("Dataset preview:")
        st.dataframe(df.head())
        
        # Dynamically select a column for analysis
        text_column = st.selectbox("Select the column containing text data", df.columns)
        if st.button("Analyze Dataset"):
            if not df[text_column].isnull().all():
                df['Sentiment Score'] = df[text_column].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
                df['Sentiment'] = df['Sentiment Score'].apply(
                    lambda x: "Positive 😊" if x > 0 else ("Negative 😔" if x < 0 else "Neutral 😐")
                )
                st.write("Analyzed Dataset:")
                st.dataframe(df)
                st.download_button(
                    label="Download Analyzed Dataset",
                    data=df.to_csv(index=False),
                    file_name="analyzed_dataset.csv",
                    mime="text/csv"
                )
            else:
                st.warning(f"The selected column '{text_column}' does not contain valid text data.")

       elif input_method == "Fetch Tweets":
    # Inputs for Twitter search
    search_term = st.text_input("Enter hashtag, keyword, or username to fetch tweets:")
    tweet_count = st.number_input("Number of tweets to fetch:", min_value=1, max_value=100, value=10)
    
    if st.button("Fetch and Analyze Tweets"):
        if search_term.strip():
            try:
                # Fetch tweets with retry logic for rate-limiting
                query = f"{search_term} -is:retweet lang:en"
                
                def fetch_with_retry(client, query, max_results, retries=3):
                    for attempt in range(retries):
                        try:
                            return client.search_recent_tweets(
                                query=query, 
                                max_results=max_results, 
                                tweet_fields=["created_at", "author_id", "text"]
                            )
                        except tweepy.TooManyRequests:
                            st.warning(f"Rate limit reached. Retrying after a short wait...")
                            time.sleep(15 * 60)  # Wait for 15 minutes
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
                            return None

                tweets = fetch_with_retry(client, query, tweet_count)
                
                if tweets and tweets.data:
                    # Store tweets in a DataFrame
                    tweet_data = []
                    for tweet in tweets.data:
                        sentiment = TextBlob(tweet.text).sentiment.polarity
                        sentiment_label = "Positive 😊" if sentiment > 0 else ("Negative 😔" if sentiment < 0 else "Neutral 😐")
                        tweet_data.append([tweet.id, tweet.created_at, tweet.text, sentiment, sentiment_label])
                    
                    df = pd.DataFrame(tweet_data, columns=["Tweet ID", "Created At", "Text", "Sentiment Score", "Sentiment"])
                    st.write("Fetched and Analyzed Tweets:")
                    st.dataframe(df)
                    
                    st.download_button(
                        label="Download Analyzed Tweets",
                        data=df.to_csv(index=False),
                        file_name="fetched_tweets.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No tweets found or rate limit exceeded. Try again later.")
            except Exception as e:
                st.error(f"Error fetching tweets: {e}")
        else:
            st.warning("Please enter a valid search term.")

               
