import praw
import datetime
import re
from config.index import Config

SOURCE_SUBREDDITS = [
    "stocks",
    "StockMarket",
    "investing",
    "wallstreetbets",
    "options",
    "ValueInvesting",
    "SecurityAnalysis",
    "pennystocks",
    "trading",
]
MAX_RESULTS = 100
MAX_SEARCH_RESULTS = 500
MAX_NEW_PER_SUBREDDIT = 120

## Setup
reddit = praw.Reddit(
    client_id=Config.REDDIT_CLIENT_ID,
    client_secret=Config.REDDIT_CLIENT_SECRET,
    user_agent=Config.REDDIT_USER_AGENT,
)


def fetch_posts(stock_symbol):
    symbol_pattern = re.compile(rf"(?<!\w)\$?{re.escape(stock_symbol)}(?!\w)", re.IGNORECASE)
    subreddit_group = reddit.subreddit("+".join(SOURCE_SUBREDDITS))
    posts = []
    seen_ids = set()

    def add_if_match(post):
        post_text = f"{post.title}\n{post.selftext or ''}"
        if post.id in seen_ids or not symbol_pattern.search(post_text):
            return False
        posts.append(post)
        seen_ids.add(post.id)
        return True

    for post in subreddit_group.search(
        stock_symbol,
        sort="new",
        limit=MAX_SEARCH_RESULTS,
    ):
        add_if_match(post)
        if len(posts) >= MAX_RESULTS:
            break

    if len(posts) < MAX_RESULTS:
        for subreddit_name in SOURCE_SUBREDDITS:
            subreddit = reddit.subreddit(subreddit_name)
            for post in subreddit.new(limit=MAX_NEW_PER_SUBREDDIT):
                add_if_match(post)
                if len(posts) >= MAX_RESULTS:
                    break
            if len(posts) >= MAX_RESULTS:
                break

    if len(posts) < MAX_RESULTS:
        for post in subreddit_group.search(
            f'title:"{stock_symbol}"',
            sort="new",
            limit=MAX_SEARCH_RESULTS,
        ):
            add_if_match(post)
            if len(posts) >= MAX_RESULTS:
                break

    posts.sort(key=lambda post: post.created_utc, reverse=True)

    return posts[:MAX_RESULTS]


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
