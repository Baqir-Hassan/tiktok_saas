import praw
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Path to tracking folder
TRACKING_FOLDER = "tracking_files"
os.makedirs(TRACKING_FOLDER, exist_ok=True)

SEEN_FILE = os.path.join(TRACKING_FOLDER, "seen_posts.txt")


def load_seen_ids(filename=SEEN_FILE):
    """Load previously seen post IDs from file."""
    if not os.path.exists(filename):
        return set()
    with open(filename, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())


def save_seen_ids(seen_ids, filename=SEEN_FILE):
    """Save seen post IDs to file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(seen_ids))


def get_reddit_posts(subreddits, limit=3):
    results = []
    seen_posts = load_seen_ids()

    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        for post in subreddit.top(time_filter="day", limit=limit * 3):
            if post.id not in seen_posts:  # skip if already scraped
                seen_posts.add(post.id)
                results.append({
                    "subreddit": sub,
                    "title": post.title,
                    "text": post.selftext
                })
                if len(results) >= limit:
                    break

    save_seen_ids(seen_posts)
    return results


# For quick testing (only runs if you run this file directly)
if __name__ == "__main__":
    subs = ["EntitledParents"]
    posts = get_reddit_posts(subs, limit=3)
    for post in posts:
        print(f"[{post['subreddit']}] {post['title']}\n{post['text']}\n---")
