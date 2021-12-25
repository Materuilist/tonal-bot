from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from youtube import get_comments
import plotly.express as px
import pandas as pd

credential = AzureKeyCredential("83afdf0969b64c1ea8bd5617aaf24afe")

text_analytics_client = TextAnalyticsClient(endpoint="https://tadviexample.cognitiveservices.azure.com/", credential=credential)

def get_sentiments(documents):
    response = text_analytics_client.analyze_sentiment(documents)
    return [
        {'sentiment':doc.sentiment, 'positive': doc.confidence_scores.positive, 'negative': doc.confidence_scores.negative, 'neutral': doc.confidence_scores.neutral} 
        for doc in response if not doc.is_error
    ]

def get_stats(video_id):
    comments = get_comments(video_id)
    mapped_comments = [{'id':index + 1,'language':'en','text':comment} for index, comment in enumerate(comments)]
    sentiments = get_sentiments(mapped_comments)
    print(sentiments)

    sentiments_frequency = {'positive':0, 'negative':0, 'mixed': 0, 'neutral': 0}

    for sentiment in sentiments:
        sentiments_frequency[sentiment['sentiment']] += 1

    most_frequent_sentiment = max(sentiments_frequency, key=sentiments_frequency.get)
    positivity = sum([sentiment['positive'] for sentiment in sentiments]) / len(sentiments) * 100
    
    df = pd.DataFrame()
    sentiments_frequency_filtered = {sentiment:frequency for sentiment, frequency in sentiments_frequency.items() if frequency != 0}
    df['category'] = sentiments_frequency_filtered.keys()
    df['share'] = sentiments_frequency_filtered.values()
    chart = px.pie(df, values='share', names='category', title='Tonality for video ' + video_id).to_image(format="png")

    overall_summary = '\n'.join([
        'Общая тональность: ' + most_frequent_sentiment, 
        'Позитивность комментариев: ' + str(positivity) + '%',
        'Процент позитивных комментариев = ' + str(sentiments_frequency['positive'] / len(sentiments) * 100) + '%', 
        'Процент негативных комментариев = ' + str(sentiments_frequency['negative'] / len(sentiments) * 100) + '%', 
        'Процент смешанных комментариев = ' + str(sentiments_frequency['mixed'] / len(sentiments) * 100) + '%', 
        'Процент нейтральных комментариев = ' + str(sentiments_frequency['neutral'] / len(sentiments) * 100) + '%'
    ])
    return overall_summary, chart