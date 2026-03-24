import sys
from fetcher import get_post_comments_data

if __name__ == "__main__":
    # Accept post id or url as argument, or use a default HN post id
    post_id = sys.argv[1] if len(sys.argv) > 1 else "47501729"  # Example: top story id
    result = get_post_comments_data(post_id, max_comments=10)
    print(result)
