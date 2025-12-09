# trigger_video_creation.py
from app.scraper import get_reddit_posts

# Import the configured Celery app instance
from celeryconfig import app
from app.tasks.tasks import create_video_from_post

def main():
    """
    Finds new Reddit posts and triggers a background task for each one.
    """
    print("Searching for new Reddit posts...")
    subreddits = ["TIFU"]
    posts = get_reddit_posts(subreddits, limit=1)

    if not posts:
        print("No new posts found. Exiting.")
        return

    for post in posts:
        print(f"Found post: '{post['title']}'. Dispatching video creation task...")
        # This sends the job to your Celery worker and immediately continues
        create_video_from_post.delay(post)

if __name__ == "__main__":
    main()