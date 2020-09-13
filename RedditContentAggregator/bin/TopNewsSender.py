import argparse
from RedditContentAggregator.tasks.RedditScraper import RedditScraper
from RedditContentAggregator.tasks.EmailSender import EmailSender
from RedditContentAggregator.tasks.MySQLStore import MySQLStore

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
Parser.add_argument("-pages", help="total pages you'd like to scrape")

# top N results stored, default is 10
Parser.add_argument("-results", help="top results you'd like to scrape")

# whether creating new mysql table or not
Parser.add_argument('-new_table', help="whether create new subreddit table in mysql or not")

args = Parser.parse_args()
print(args)

if __name__ == "__main__":
    # default: scrape the top 3 pages in that subreddit, return the top 10 results with most upvotes
    if args.pages is None:
        args.pages = 3

    if args.results is None:
        args.results = 10

    if args.new_table is None:
        args.new_table = False

    reddit = RedditScraper(subreddit_name=args.subreddit,
                           total_pages_scrape=args.pages,
                           total_posts=args.results)
    results_df, results_html = reddit.scraper() # store scraped results

    # create mysql object that stores pulled results
    mysql = MySQLStore(subreddit=args.subreddit, crawled_posts=results_df, create_new_table=args.new_table)

    if mysql.run(): # new posts have less than 80% overlap with the latest posts in the database
        # compose email
        email = EmailSender(emailRecipients=args.address,
                            emailBody=results_html,
                            emailSubject=f'Top {args.results} results from /reddit/{args.subreddit}/'
                            )

        email.sendEmail()
    else:
        print("No new posts today.")