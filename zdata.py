import pandas as pd
import json
import sys
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

browser = None

try:
    # chrome
    #browser = webdriver.Chrome(executable_path='/home/springpc-1/python/chromedriver/chromedriver')

    # firefox
    browser = webdriver.Firefox(
        executable_path='/home/springpc-1/python/geckodriver-v0.25.0-linux64/geckodriver')

except Exception as error:
    print(error)


class Zdata:

    def __init__(self, url):
        self.url = url
        self.html_text = None
        try:
            browser.get(self.url)
            self.html_text = browser.page_source
            
        except Exception as err:
            print(str(err))
            return

        self.soup = None
        if self.html_text is not None:
            self.soup = BeautifulSoup(self.html_text, "html.parser")



    def load_all_reviews(self):
        '''
        This function finds load more and click on load more and fetch more data
        '''
        while (True):
            try:
                load_more = WebDriverWait(browser, 20).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "res-page-load-more")))
                browser.execute_script(
                    "arguments[0].scrollIntoView(true);", load_more)
                load_more = WebDriverWait(browser, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "res-page-load-more")))
                browser.execute_script(
                    'arguments[0].setAttribute("data-limit", 20)', load_more)

                load_more.click()

            except (NoSuchElementException, TimeoutException):
                print("There is no button load more")
                break



    def get_reviews(self):

        try:
            browser.get(self.url+'/reviews')
            self.review_html_text = browser.page_source

        except Exception as err:
            print(str(err))
            return

        self.reviewSoup = BeautifulSoup(self.review_html_text, "html.parser")
        link = browser.find_element_by_xpath(
            "//a[@data-sort='reviews-dd']")

        print("waiting to load")
        time.sleep(15)

        print("clicking all review btn " + link.text)
        link.click()

        # This will load all reviews 
        self.load_all_reviews()

        new_source = browser.execute_script(
            "return document.body.innerHTML")

        new_soup = BeautifulSoup(new_source, "html.parser")

        reviews_body = new_soup.find_all(
            'div', attrs={"class": "res-review-body"})

        reviews = []
        for review_body in reviews_body:
            review = dict()

            review_rating = review_body.find(
                'div', attrs={'class': 'zdhl2'}).attrs['aria-label'].strip()

            review_senti = review_body.find(
                'p', attrs={'class': 'sentiment-text'})
            if review_senti:
                senti = review_senti.text.strip()
                review['sentiment'] = senti

            review_text = review_body.find(
                'div', attrs={"class": "rev-text"}).text.strip()

            review_author = review_body.find(
                'div', attrs={"class": "header"}).text.strip()

            review_date = review_body.find('time').text.strip()

            review_likes = review_body.find(
                'div', attrs={'class': 'stats-thanks'}).text.strip()

            reivew_cmts = review_body.find(
                'div', attrs={'class': 'stats-comment'}).text.strip()

            # comments section
            if reivew_cmts and int(reivew_cmts) > 0:

                print('Found ' + reivew_cmts + ' comments')

                comts_body = review_body.find_all(
                    'div', attrs={"class": "review_comment_item"})

                cmt_list = []

                for cmts in comts_body:
                    comments = dict()

                    comments_author = cmts.find(
                        'a', attrs={"class": "author"}).text.strip()

                    comments_txt = cmts.find(
                        'span', attrs={'class': 'review_comment_text'}).text.strip()

                    cmt_text = " ".join(comments_txt.split())
                    cmt_author = " ".join(comments_author.split())

                    comments['cmt_text'] = cmt_text
                    comments['cmt_author'] = cmt_author

                    cmt_list.append(comments)

                review['comments'] = cmt_list

            review_text = " ".join(review_text.split()[1:])
            review_author = " ".join(review_author.split())

            review['rated'] = " ".join(review_rating.split()[1:])
            review['likes'] = review_likes
            review['text'] = review_text
            review['author'] = review_author
            review['date'] = review_date

            reviews.append(review)

        return reviews


# Entry point for Program
if __name__ == '__main__':

    if browser is None:
        sys.exit()

    # json
    out_file = open("reviews.json", "a")
    url = 'https://www.zomato.com/ahmedabad/shreejikrupa-gurukul'
    zr = Zdata(url)
    json.dump(zr.get_reviews(), out_file)

    # csv
    # url = 'https://www.zomato.com/ahmedabad/havmor-ice-cream-1-gurukul'
    # zr = ZomatoRestaurant(url)
    # df = pd.DataFrame(zr.get_reviews())
    # df.to_csv('out1.csv')
