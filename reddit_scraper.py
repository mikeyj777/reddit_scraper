import requests
import json
import time
from typing import List, Dict, Optional

subreddit = "ClaudeAI"

class RedditClaudeAIScraper:
    def __init__(self, subreddit: str = 'ClaudeAI'):
        self.subreddit = subreddit
        self.base_url = "https://www.reddit.com"
        self.subreddit_url = f"{self.base_url}/r/{self.subreddit}.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.claude_posts_list = []
        
    def fetch_subreddit_json(self) -> Optional[Dict]:
        """Fetch the main subreddit JSON data"""
        try:
            response = requests.get(self.subreddit_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching subreddit data: {e}")
            return None
    
    def fetch_post_json(self, post_link: str) -> Optional[Dict]:
        """Fetch individual post JSON data"""
        try:
            # Add .json extension to the post link
            json_link = f"{post_link}.json"
            response = requests.get(json_link, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching post data from {post_link}: {e}")
            return None
    
    def extract_post_info(self, post_data: Dict) -> Dict[str, str]:
        """Extract relevant information from post data"""
        try:
            data = post_data['data']
            post_description = data.get('title', 'No title')
            post_link = f"{self.base_url}{data.get('permalink', '')}"
            
            return {
                'post_description': post_description,
                'post_link': post_link
            }
        except KeyError as e:
            print(f"Error extracting post info: {e}")
            return {
                'post_description': 'Error extracting title',
                'post_link': ''
            }
    
    def scrape_all_posts(self, delay: float = 1.0) -> List[Dict]:
        """Main method to scrape all posts from the subreddit"""
        print("Fetching ClaudeAI subreddit data...")
        subreddit_data = self.fetch_subreddit_json()
        
        if not subreddit_data:
            print("Failed to fetch subreddit data")
            return []
        
        try:
            posts = subreddit_data['data']['children']
            print(f"Found {len(posts)} posts to process...")
            
            for i, post in enumerate(posts, 1):
                print(f"Processing post {i}/{len(posts)}")
                
                # Extract basic post info
                post_info = self.extract_post_info(post)
                
                if post_info['post_link']:
                    # Fetch the detailed post JSON
                    post_json = self.fetch_post_json(post_info['post_link'])
                    
                    # Create the dictionary entry
                    post_entry = {
                        'post_description': post_info['post_description'],
                        'post_link': f"{post_info['post_link']}.json",
                        'post_json': post_json
                    }
                    
                    self.claude_posts_list.append(post_entry)
                    print(f"✓ Added: {post_info['post_description'][:50]}...")
                else:
                    print(f"✗ Skipped post due to missing link")
                
                # Add delay to be respectful to Reddit's servers
                if i < len(posts):
                    time.sleep(delay)
        
        except KeyError as e:
            print(f"Error parsing subreddit data structure: {e}")
            return []
        
        print(f"\nCompleted! Scraped {len(self.claude_posts_list)} posts.")
        return self.claude_posts_list
    
    def save_to_file(self, filename: str = 'claude_posts.json'):
        """Save the scraped data to a JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.claude_posts_list, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")
    
    def get_posts_summary(self) -> Dict:
        """Get a summary of the scraped posts"""
        if not self.claude_posts_list:
            return {"total_posts": 0, "posts": []}
        
        summary = {
            "total_posts": len(self.claude_posts_list),
            "posts": []
        }
        
        for post in self.claude_posts_list:
            summary["posts"].append({
                "title": post["post_description"],
                "link": post["post_link"],
                "has_json": post["post_json"] is not None
            })
        
        return summary

def main(subreddit: str = 'ClaudeAI') -> List[Dict]:
    """Main function to run the scraper"""
    scraper = RedditClaudeAIScraper()
    
    # Scrape all posts
    claude_posts_list = scraper.scrape_all_posts(delay=1.0)
    
    # Save to file
    scraper.save_to_file('claude_posts.json')
    
    # Print summary
    summary = scraper.get_posts_summary()
    print(f"\n--- SUMMARY ---")
    print(f"Total posts scraped: {summary['total_posts']}")
    
    if summary['posts']:
        print("\nFirst 5 posts:")
        for i, post in enumerate(summary['posts'][:5], 1):
            print(f"{i}. {post['title'][:60]}...")
            print(f"   Link: {post['link']}")
            print(f"   JSON loaded: {post['has_json']}")
            print()
    
    return claude_posts_list

if __name__ == "__main__":
    claude_posts_list = main(subreddit=subreddit)