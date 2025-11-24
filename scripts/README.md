# Reddit Cross-Post Script

## Overview
This script automates cross-posting your ChatGPT prompt pack announcements to relevant subreddits.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..." at the bottom
3. Fill in the form:
   - **name**: ChatGPT Prompt Curator
   - **type**: Select "script"
   - **description**: Script for posting prompt packs
   - **about url**: (leave empty)
   - **redirect uri**: http://localhost:8080
4. Click "create app"
5. Note down:
   - **client_id**: The string under "personal use script"
   - **client_secret**: The secret string

### 3. Configure the Script

Option A: Environment Variables (Recommended)
```bash
export REDDIT_CLIENT_ID='your_client_id'
export REDDIT_CLIENT_SECRET='your_client_secret'
export REDDIT_USERNAME='your_username'
export REDDIT_PASSWORD='your_password'
```

Option B: Edit Script Directly
Edit `reddit_crosspost.py` and update the `REDDIT_CONFIG` dictionary.

### 4. Customize Your Product Information

Edit these variables in `reddit_crosspost.py`:
```python
PRODUCT_INFO = {
    'title': 'Your product title',
    'gumroad_url': 'https://gumroad.com/your-product',
    'price': '$10',
    'description': 'Your description',
}
```

## Usage

### Dry Run (Test Mode - Recommended First)
```bash
python reddit_crosspost.py
```

This will show you what would be posted without actually posting.

### List Available Flairs
```bash
python reddit_crosspost.py --list-flairs
```

This will show all available post flairs for each target subreddit. Use this to find flair IDs before posting.

### Live Posting
```bash
python reddit_crosspost.py --live
```

⚠️ **Warning**: This will actually post to Reddit!

### Custom Category
```bash
python reddit_crosspost.py --category "Content Creation"
```

## Target Subreddits

The script posts to these subreddits by default:
- r/ChatGPT
- r/ChatGPTPromptGenius
- r/OpenAI
- r/ArtificialIntelligence
- r/SideProject

**Note**: Post flairs are set to None by default. Use `--list-flairs` to find available flair IDs for each subreddit.

### Posting Schedule
Posts are staggered with delays between each subreddit to avoid appearing as spam:
- Subreddit 1: Immediate
- Subreddit 2: 30 minutes delay
- Subreddit 3: 60 minutes delay
- Subreddit 4: 90 minutes delay
- Subreddit 5: 120 minutes delay

## Customization

### Add More Subreddits
Edit the `SUBREDDIT_TARGETS` list in the script:
```python
{
    'subreddit': 'SubredditName',
    'title': 'Your custom title for this subreddit',
    'flair': 'flair_id_here',  # Use --list-flairs to find ID, or None
    'delay_minutes': 150  # minutes after previous post
}
```

### Customize Post Content
Edit the `POST_TEMPLATE` variable to change the post format.

### Change Discount Code
Modify the discount percentage in the `format_post_content` function.

## Best Practices

### Before Posting
1. ✅ Read each subreddit's rules about self-promotion
2. ✅ Build karma by participating in discussions first
3. ✅ Check if the subreddit allows product promotion
4. ✅ Look for specific days for promotion (e.g., "Self-Promotion Sunday")
5. ✅ Test with dry-run first

### While Posting
1. ✅ Monitor posts for comments
2. ✅ Respond to questions promptly
3. ✅ Provide value in your responses
4. ✅ Accept feedback gracefully

### After Posting
1. ✅ Track which subreddits perform best
2. ✅ Note optimal posting times
3. ✅ Wait at least 7 days before posting again to same subreddit
4. ✅ Adjust content based on feedback

## Reddit Self-Promotion Guidelines

**The 10:1 Rule**: For every 1 self-promotional post, make 10 value-adding posts/comments.

**What Works**:
- Providing free value (sample prompts)
- Engaging with comments
- Offering Reddit-exclusive discounts
- Being transparent about it being a paid product
- Sharing your journey/story

**What Doesn't Work**:
- Pure advertising with no value
- Posting to irrelevant subreddits
- Ignoring comments
- Being defensive about criticism
- Spamming multiple subreddits at once

## Troubleshooting

### Authentication Errors
```
❌ Authentication failed: ...
```
**Solution**: Double-check your credentials. Make sure you're using app credentials, not personal password.

### Rate Limiting
```
❌ You're doing that too much...
```
**Solution**: Reddit limits new accounts. Build karma first, or increase delays between posts.

### Shadowban
If posts don't appear:
**Solution**: Check if you're shadowbanned at r/ShadowBan. Follow Reddit's self-promotion guidelines.

### Subreddit Rules
```
❌ Failed to post: ...
```
**Solution**: Read the subreddit's rules. Some require moderator approval for promotional content.

## Safety Features

- Dry-run mode by default
- Confirmation required for live posting
- Rate limiting with delays
- Subreddit rules checking
- Progress tracking and logging

## Support

For issues or questions:
- Check Reddit API docs: https://www.reddit.com/dev/api
- PRAW documentation: https://praw.readthedocs.io

## Legal

- Follow Reddit's User Agreement and Content Policy
- Respect subreddit rules
- Don't manipulate votes
- Don't create multiple accounts to promote
- Be transparent about commercial content
