import pymysql.cursors
from Utils import MySQLConfigs
from datetime import datetime
from sqlalchemy import create_engine
import logging
logging.basicConfig(level=logging.INFO)


class MySQLStore:

    def __init__(self, subreddit, crawled_posts, create_new_table):
        DB_NAME="crawler"
        self.subreddit = subreddit
        self.crawled_posts = crawled_posts
        self.create_new_table = create_new_table

        # connect to mysql
        self.cnx = pymysql.connect(host='localhost',
                                   user='suqinhou',
                                   password=MySQLConfigs.password,
                                   db=f'{DB_NAME}',
                                   charset='utf8mb4',
                                   cursorclass=pymysql.cursors.DictCursor)

        self.sqlalchemy_cnx = create_engine(f"mysql+pymysql://suqinhou:{MySQLConfigs.password}@localhost/{DB_NAME}")

    def create_table(self):
        """
        create table that stores historical reddit posts if not exists
        :return:
        """

        create_table = f'''
        CREATE TABLE IF NOT EXISTS `reddit` (
            `subreddit` varchar(64) NOT NULL,
            `crawl_dt` date NOT NULL,
            `title` varchar(512) NOT NULL
        ) ENGINE=InnoDB
        '''
        with self.cnx.cursor() as cursor:
            if self.create_new_table is True:
                cursor.execute('DROP TABLE IF EXISTS `reddit`')
                logging.info("dropped existing table")
            cursor.execute(create_table)
        self.cnx.commit() # connection is not autocommitted by default
        logging.info("Created reddit table if not exists.")

    def crawled_data_upload(self):
        """
        upload crawled data to table reddit
        :return:
        """
        tmp_data = self.crawled_posts
        # modify columns before uploading
        tmp_data['subreddit'] = self.subreddit
        tmp_data['crawl_dt'] = datetime.now().strftime('%Y%m%d')

        tmp_data = tmp_data[['subreddit', 'crawl_dt', 'Title']]
        # # upload data
        # try:
        #     tmp_data.to_sql(con=self.sqlalchemy_cnx, name='reddit', if_exists='append', flavor='mysql')
        #     logging.info("Uploaded scraped data into mysql.")
        # except:
        #     logging.info("Can't upload data; Error occurred; Abort. ")
        #     return

        tmp_data.to_sql(con=self.sqlalchemy_cnx, name='reddit', if_exists='append', index= False)
        logging.info("Uploaded scraped data into mysql.")

    def overlap_gt_80(self) -> bool:
        """
        check if the current batch of crawled posts and the last batch in the database
        have 80% or more identical posts
        :return:
        """
        query = f'''
        SELECT DISTINCT title
        FROM crawler.reddit
        WHERE crawl_dt = (SELECT max(crawl_dt) FROM crawler.reddit WHERE subreddit = "{self.subreddit}")
        AND subreddit = "{self.subreddit}"
        '''

        with self.cnx.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            results_list = [i['title'] for i in result]


        repeat = 0 # initiate repeated title count
        for post in self.crawled_posts['Title']:
            if post in results_list:
                repeat += 1

        # overlap between the newly pulled posts and the existing posts
        repeat_ratio = float(repeat)/self.crawled_posts.shape[0]
        if repeat_ratio >= 0.8:
            logging.info(
                f"There is a {repeat_ratio * 100}% overlap between the scrawled posts and the most updated contents.")
            return True
        else:
            return False

    def run(self):
        self.create_table() # create crawler.reddit if it does not exist
        if self.overlap_gt_80(): # if new posts are >= 80% overlapped with the latest existing posts
            logging.info("New posts are above 80% overlapped with the latest existing posts.")
            return False
        else:
            self.crawled_data_upload()
            return True
