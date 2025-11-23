#!/usr/bin/env python3
"""
Reddit Cross-Post Script for ChatGPT Prompt Packs
Automates posting product announcements to relevant subreddits
"""

import os
import time
from datetime import datetime
from typing import List, Dict

# CONFIGURATION
# =============================================================================
# Progress Display Configuration
PROGRESS_UPDATE_INTERVAL_SHORT = 30  # seconds, for waits < 5 minutes
PROGRESS_UPDATE_INTERVAL_LONG = 60   # seconds, for waits >= 5 minutes
PROGRESS_UPDATE_THRESHOLD = 5        # minutes, threshold for choosing interval

# Reddit API Configuration (Get these from https://www.reddit.com/prefs/apps)
REDDIT_CONFIG = {
    'client_id': os.getenv('REDDIT_CLIENT_ID'),
    'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
    'username': os.getenv('REDDIT_USERNAME'),
    'password': os.getenv('REDDIT_PASSWORD'),
    'user_agent': 'ChatGPT_Prompt_Curator/1.0'
}

# Product Information
PRODUCT_INFO = {
    'title': '20 Battle-Tested ChatGPT Prompts for [Category]',
    'gumroad_url': 'https://gumroad.com/your-product-url',
    'price': '$10',
    'description': 'Professional ChatGPT prompt pack with usage guides',
}

# Subreddit Targets with Custom Post Templates
# NOTE: 'flair' should be the flair ID (not text). To get flair IDs:
# 1. Check subreddit's flair options in Reddit
# 2. Use reddit.subreddit('name').flair.link_templates to list available flairs
# 3. Set to None to post without flair
SUBREDDIT_TARGETS = [
    {
        'subreddit': 'ChatGPT',
        'title': 'I curated 20 tested ChatGPT prompts for [Category] - with usage guides',
        'flair': None,  # Set to actual flair_id if you have it
        'delay_minutes': 0
    },
    {
        'subreddit': 'ChatGPTPromptGenius',
        'title': '[Resource] 20 Professional ChatGPT Prompts for [Category]',
        'flair': None,  # Set to actual flair_id if you have it
        'delay_minutes': 30
    },
    {
        'subreddit': 'OpenAI',
        'title': 'Curated collection of 20 ChatGPT prompts for [Category]',
        'flair': None,
        'delay_minutes': 60
    },
    {
        'subreddit': 'ArtificialIntelligence',
        'title': 'Practical AI: 20 tested ChatGPT prompts for [Category]',
        'flair': None,
        'delay_minutes': 90
    },
    {
        'subreddit': 'SideProject',
        'title': 'I built a curated ChatGPT prompt pack - feedback welcome',
        'flair': None,
        'delay_minutes': 120
    }
]

# Post Content Template
POST_TEMPLATE = """
Hey everyone! 👋

I've spent the last few months testing and refining ChatGPT prompts for {category}, and I wanted to share what I've learned.

**What I created:**
{bullet_points}

**What makes this different:**
Unlike basic prompt lists, each prompt includes:
- Detailed usage instructions
- Real-world examples
- Pro tips for better results
- Common pitfalls to avoid

**Price:** {price}

You can check it out here: {url}

**Sample Prompt (Free):**
{sample_prompt}

I'm offering a {discount}% discount for the Reddit community. Use code: REDDIT{discount}

Happy to answer any questions! 🚀

---
*This is a paid product. I've tried to provide value by including a free sample and detailed documentation.*
"""

# Sample prompt to include in posts
SAMPLE_PROMPT = """
[Paste one of your prompts here as a free sample]
Example: "Task Prioritizer Pro - Analyzes your tasks using the Eisenhower Matrix..."
"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def validate_config() -> bool:
    """Validate that all required configuration is present"""
    required_fields = ['client_id', 'client_secret', 'username', 'password']
    
    for field in required_fields:
        if not REDDIT_CONFIG[field]:
            print(f"❌ Error: {field} not configured")
            print(f"   Set environment variable: REDDIT_{field.upper()}")
            return False
    
    return True


def create_reddit_instance():
    """Create and return authenticated Reddit instance"""
    try:
        import praw
    except ImportError:
        print("❌ Error: praw not installed. Run: pip install praw")
        return None
    
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CONFIG['client_id'],
            client_secret=REDDIT_CONFIG['client_secret'],
            username=REDDIT_CONFIG['username'],
            password=REDDIT_CONFIG['password'],
            user_agent=REDDIT_CONFIG['user_agent']
        )
        
        # Test authentication
        print(f"✅ Authenticated as: u/{reddit.user.me()}")
        return reddit
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None


def list_subreddit_flairs(reddit, subreddit_name: str):
    """Helper function to list available flairs for a subreddit"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        flairs = list(subreddit.flair.link_templates)
        
        if not flairs:
            print(f"r/{subreddit_name}: No flairs available or not accessible")
            return
        
        print(f"\nr/{subreddit_name} available flairs:")
        for flair in flairs:
            print(f"  - ID: {flair['id']}")
            print(f"    Text: {flair['text']}")
            print(f"    Type: {flair['type']}")
            print()
    except Exception as e:
        print(f"❌ Error getting flairs for r/{subreddit_name}: {e}")


def format_post_content(category: str, bullet_points: List[str]) -> str:
    """Format the post content with product details"""
    bullets = '\n'.join([f"✅ {point}" for point in bullet_points])
    
    content = POST_TEMPLATE.format(
        category=category,
        bullet_points=bullets,
        price=PRODUCT_INFO['price'],
        url=PRODUCT_INFO['gumroad_url'],
        sample_prompt=SAMPLE_PROMPT,
        discount=20  # Discount percentage for Reddit users
    )
    
    return content


def check_subreddit_rules(reddit, subreddit_name: str) -> Dict:
    """Check subreddit rules and requirements"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Check if we can post
        if subreddit.subreddit_type == 'private':
            return {'can_post': False, 'reason': 'Private subreddit'}
        
        # Get subreddit info
        info = {
            'can_post': True,
            'subscribers': subreddit.subscribers,
            'rules_count': len(list(subreddit.rules)),
            'allows_self_posts': True  # Assume true, adjust if needed
        }
        
        return info
        
    except Exception as e:
        return {'can_post': False, 'reason': str(e)}


def post_to_subreddit(reddit, target: Dict, content: str, dry_run: bool = True) -> bool:
    """Post content to a specific subreddit"""
    subreddit_name = target['subreddit']
    title = target['title']
    flair = target.get('flair')
    
    print(f"\n📝 Posting to r/{subreddit_name}")
    print(f"   Title: {title}")
    
    if dry_run:
        print(f"   [DRY RUN] Would post to r/{subreddit_name}")
        return True
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Submit the post
        submission = subreddit.submit(
            title=title,
            selftext=content,
            flair_id=flair
        )
        
        print(f"   ✅ Posted successfully!")
        print(f"   URL: {submission.url}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to post: {e}")
        return False


def wait_with_progress(minutes: int):
    """Wait for specified minutes with progress indicator"""
    if minutes == 0:
        return
    
    print(f"\n⏳ Waiting {minutes} minutes before next post...")
    
    # Adjust update interval based on wait time
    update_interval = (PROGRESS_UPDATE_INTERVAL_LONG 
                      if minutes >= PROGRESS_UPDATE_THRESHOLD 
                      else PROGRESS_UPDATE_INTERVAL_SHORT)
    
    for remaining in range(minutes * 60, 0, -update_interval):
        mins = remaining // 60
        secs = remaining % 60
        print(f"   Time remaining: {mins:02d}:{secs:02d}", end='\r')
        time.sleep(update_interval)
    
    print("\n   ✅ Wait complete!")


# =============================================================================
# MAIN SCRIPT
# =============================================================================

def main(dry_run: bool = True, category: str = "Productivity"):
    """
    Main function to cross-post to Reddit
    
    Args:
        dry_run: If True, simulates posting without actually posting
        category: Product category for post customization
    """
    
    print("=" * 70)
    print("Reddit Cross-Post Script for ChatGPT Prompt Packs")
    print("=" * 70)
    
    # Validate configuration
    if not validate_config():
        print("\n❌ Configuration incomplete. Please update REDDIT_CONFIG.")
        print("\nTo get Reddit API credentials:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Click 'create another app...'")
        print("3. Choose 'script' type")
        print("4. Copy client_id and client_secret")
        return
    
    # Create Reddit instance
    reddit = create_reddit_instance()
    if not reddit:
        return
    
    # Prepare post content
    bullet_points = [
        f"20 tested ChatGPT prompts for {category}",
        "Complete usage guides for each prompt",
        "Real-world examples and best practices",
        "Copy-paste ready templates",
        "Lifetime updates included"
    ]
    
    content = format_post_content(category, bullet_points)
    
    print(f"\n{'='*70}")
    print("POST PREVIEW")
    print(f"{'='*70}")
    print(content)
    print(f"{'='*70}\n")
    
    if dry_run:
        print("🔍 DRY RUN MODE - No actual posts will be made\n")
    else:
        confirm = input("⚠️  LIVE MODE - Posts will be made. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
    
    # Post to each subreddit
    results = []
    
    for i, target in enumerate(SUBREDDIT_TARGETS):
        # Check subreddit rules first
        print(f"\n[{i+1}/{len(SUBREDDIT_TARGETS)}] Checking r/{target['subreddit']}...")
        
        rules_check = check_subreddit_rules(reddit, target['subreddit'])
        
        if not rules_check['can_post']:
            print(f"   ⚠️  Cannot post: {rules_check['reason']}")
            results.append({'subreddit': target['subreddit'], 'status': 'skipped'})
            continue
        
        print(f"   Subscribers: {rules_check['subscribers']:,}")
        
        # Post to subreddit
        success = post_to_subreddit(reddit, target, content, dry_run)
        
        results.append({
            'subreddit': target['subreddit'],
            'status': 'success' if success else 'failed'
        })
        
        # Wait before next post (except for last one)
        if i < len(SUBREDDIT_TARGETS) - 1 and not dry_run:
            wait_with_progress(target['delay_minutes'])
    
    # Summary
    print(f"\n{'='*70}")
    print("POSTING SUMMARY")
    print(f"{'='*70}")
    
    for result in results:
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_emoji} r/{result['subreddit']}: {result['status']}")
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"\nTotal: {success_count}/{len(results)} successful")
    
    print("\n💡 Tips for better engagement:")
    print("   - Respond to comments quickly")
    print("   - Provide value in your responses")
    print("   - Don't spam - wait 24h between posts to same subreddit")
    print("   - Follow each subreddit's self-promotion rules")
    print("   - Build karma by contributing to discussions first")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Cross-post ChatGPT prompts to Reddit')
    parser.add_argument('--live', action='store_true', help='Actually post (default is dry-run)')
    parser.add_argument('--category', default='Productivity', help='Product category')
    parser.add_argument('--list-flairs', action='store_true', help='List available flairs for all target subreddits')
    
    args = parser.parse_args()
    
    # If list-flairs is requested, just list flairs and exit
    if args.list_flairs:
        print("=" * 70)
        print("Listing Subreddit Flairs")
        print("=" * 70)
        
        reddit = create_reddit_instance()
        if not reddit:
            print("\n❌ Failed to authenticate. Check your credentials.")
            exit(1)
        
        for target in SUBREDDIT_TARGETS:
            list_subreddit_flairs(reddit, target['subreddit'])
        
        print("\n💡 To use a flair, copy the 'ID' value and set it in SUBREDDIT_TARGETS")
        exit(0)
    
    main(dry_run=not args.live, category=args.category)
