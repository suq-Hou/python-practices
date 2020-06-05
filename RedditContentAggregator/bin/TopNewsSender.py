import argparse
from RedditContentAggregator.tasks.RedditScraper import RedditScraper
from RedditContentAggregator.tasks.EmailSender import EmailSender

Parser = argparse.ArgumentParser()

## mandatory args
# name of the subreddit
Parser.add_argument("--subreddit", type=str,
                    help="exact name of the subreddit you wish to parse posts from",
                    required=True
                    )

# email recipients
Parser.add_argument("--address", nargs='+', help='email address of the recipient', required=True)

## optional args
# total pages you'd like to scrape, default is 3
Parser.add_argument("-pages", "--Total pages scrape", help="total pages you'd like to scrape")

# top N results stored, default is 10
Parser.add_argument("-results", "--Top results", help="top results you'd like to scrape")

args = Parser.parse_args()

if __name__ == "__main__":
    # default: scrape the top 3 pages in that subreddit, return the top 10 results with most upvotes
    try:
        args.pages
    except:
        args.pages = 10

    try:
        args.results
    except:
        args.results = 3

    reddit = RedditScraper(subreddit_name=args.subreddit, total_pages_scrape=3, total_posts=10)
    results = reddit.scraper() # store scraped results

    # compose email
    email = EmailSender(emailRecipients=args.address,
                        emailBody=results,
                        emailSubject=f'Top {args.pages} results from /reddit/{args.subreddit}/'
                        )

    email.sendEmail()