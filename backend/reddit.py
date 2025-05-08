import praw
import os
from dotenv import load_dotenv
import datetime


load_dotenv()

## Setup
reddit = praw.Reddit(
    client_id=os.getenv("reddit_client_id"),
    client_secret=os.getenv("reddit_client_secret"),
    user_agent=os.getenv("reddit_user_agent"),
)


def fetch_posts(stock_symbol):
    ### subreddit
    subreddit = reddit.subreddit("stocks")

    ### search query
    query = f"title:{stock_symbol}"

    ### fetch posts
    results = subreddit.search(query, limit=100, sort="new")

    return results


def model_post(post, prediction):
    ## Safely get author name
    author_name = post.author.name if post.author else "[deleted]"

    ## Estimate downvotes
    score = post.score
    upvote_ratio = post.upvote_ratio
    estimated_downvotes = int((1 - upvote_ratio) * score)

    ## Format date
    created_date = datetime.datetime.utcfromtimestamp(post.created_utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    ## Build dictionary
    post_data = {
        "title": post.title,
        "content": post.selftext,
        "author": author_name,
        "upvotes": score,
        "estimated_downvotes": estimated_downvotes,
        "sentiment": prediction,
        "created_utc": created_date,
    }

    return post_data
