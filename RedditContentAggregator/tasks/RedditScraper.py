import requests  # scrape data through web urls
from bs4 import BeautifulSoup  # extract data from HTML objects
import time  # to have a few seconds in between consecutive requests
import pandas as pd
pd.set_option('display.max_colwidth', -1)  # force pandas to not truncate contents
import logging

logging.basicConfig(level=logging.INFO)


class RedditScraper:

    def __init__(self, subreddit_name, total_pages_scrape, total_posts):
        self.useragent = 'your bot 0.1' # self-defined useragent
        self.basic_url = "https://www.reddit.com"
        self.subreddit = subreddit_name
        self.full_url = self.basic_url + "/r/" + self.subreddit
        self.pages_scrape = int(total_pages_scrape) # total number of pages needed to be scraped
        self.total_posts = int(total_posts) # total posts needed
        self.upvoted_posts = [] # list to store top posts

    def scraper(self):
        # make a request to get content from the specified subreddit url
        page = requests.get(url=self.full_url, headers={'User-agent': self.useragent})
        soup = BeautifulSoup(page.text, 'html.parser') # parse the html contents

        attrs = {'class': 'thing', 'data-subreddit': self.subreddit}

        counter = self.pages_scrape
        while counter > 0:
            logging.info("Page #: " + str(self.pages_scrape - counter + 1))
            for post in soup.find_all('div', attrs=attrs):
                # title of the post
                title = post.find('p', class_="title").find('a', class_='title').text
                # total number of upvotes
                likes = post.find('div', class_="score likes").text
                if likes == "•":  # the post is too new to have any upvotes yet
                    likes = int('0')
                else:
                    likes = self.string_to_int(likes)
                # url
                url = self.basic_url + post.attrs['data-permalink']

                post_dic = {'Title': title, 'Likes': likes, 'url': url}

                # determine if the requested number of posts have been obtained already;
                # if not, add it in the list; if so, replace the one with the lowest upvotes
                if len(self.upvoted_posts) < self.total_posts:
                    # add it to the list
                    self.upvoted_posts.append(post_dic)
                else:
                    min_score = min([i['Likes'] for i in self.upvoted_posts])
                    if likes > min_score:
                        # remove the one with the min score
                        self.upvoted_posts = [i for i in self.upvoted_posts if i['Likes'] != min_score]
                        self.upvoted_posts.append(post_dic)  # add the current one to the list

            # find url to next page
            next_page_url = soup.find('span', class_='next-button').find('a').attrs['href']
            time.sleep(2)  # pause parsing for 2 seconds
            page = requests.get(url=next_page_url, headers={'User-agent': self.useragent})
            soup = BeautifulSoup(page.text, 'html.parser')

            counter -= 1

        # convert upvotes list into a pandas data frame
        self.upvoted_posts = pd.DataFrame(self.upvoted_posts).\
            sort_values(by='Likes', ascending=False).set_index('Likes')
        # link the title to its corresponding url
        self.upvoted_posts['url'] = [f'<a href="{i}">Link</a>'for i in self.upvoted_posts['url']]

        return self.upvoted_posts, self.upvoted_posts.to_html(escape=False)  # convert list -> pandas data frame -> html object

    def string_to_int(self, number):  # convert digit strings (with possible abbreviation at the end) to int
        letter_abbrev_converter = {'k': 1000, 'm': 1000000, 'b': 1000000000}

        if number[-1].isdigit(): # no letter abbrev as postfix: convert to int directly
            return int(number)
        else:
            letter_abbrev = number[-1]
            return int(float(number[:-1]) * letter_abbrev_converter[letter_abbrev])


if __name__ == "__main__":
    reddit_scrap = RedditScraper(subreddit_name='terracehouse', total_pages_scrape=3, total_posts=10)
    print(reddit_scrap.scraper())

