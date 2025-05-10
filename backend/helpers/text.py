import re


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
