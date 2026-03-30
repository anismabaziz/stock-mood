import re
import spacy
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from functools import lru_cache

nltk.download("vader_lexicon")
nlp = spacy.load("en_core_web_sm")


@lru_cache(maxsize=1)
def get_vader():
    return SentimentIntensityAnalyzer()


def clean(post):
    ## concatenate title with text
    text = f"{post.title}\n{post.selftext}"

    ## remove links
    text = re.sub(r"http\S+", "", text)

    ## collapse whitespace
    text = re.sub(r"\s+", " ", text)

    ## remove unwanted chars
    text = re.sub(r'[^\w\s.,!?\'"]', "", text)

    return text.strip()


def count_words(text):
    doc = nlp(text)
    words = [token for token in doc if token.is_alpha]
    return len(words)


def vader_analysis(text):
    vader = get_vader()
    scores = vader.polarity_scores(text)
    return scores
