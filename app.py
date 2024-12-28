import streamlit as st
import pandas as pd
from textblob import TextBlob

# App title
st.title("Twitter Sentiment Analysis App")

# Choose input method
input_method = st.radio("Choose Input Method:", ("Enter a Tweet", "Upload a Dataset"))

if input_method == "Enter a Tweet":
    # Text input for a single tweet
    user_input = st.text_area("Enter your tweet:")
    
    if st.button("Analyze Tweet"):
        if user_input.strip():
            # Perform sentiment analysis
            analysis = TextBlob(user_input)
            sentiment = analysis.sentiment.polarity

            # Determine sentiment category
            if sentiment > 0:
                sentiment_label = "Positive 😊"
            elif sentiment < 0:
                sentiment_label = "Negative 😔"
            else:
                sentiment_label = "Neutral 😐"

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
        # Load the file into a DataFrame
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
                # Perform sentiment analysis on the selected column
                df['Sentiment Score'] = df[text_column].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
                df['Sentiment'] = df['Sentiment Score'].apply(
                    lambda x: "Positive 😊" if x > 0 else ("Negative 😔" if x < 0 else "Neutral 😐")
                )
                st.write("Analyzed Dataset:")
                st.dataframe(df)
                
                # Downloadable processed data
                st.download_button(
                    label="Download Analyzed Dataset",
                    data=df.to_csv(index=False),
                    file_name="analyzed_dataset.csv",
                    mime="text/csv"
                )
            else:
                st.warning(f"The selected column '{text_column}' does not contain valid text data.")
