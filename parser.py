import feedparser
from bs4 import BeautifulSoup
import time
import calendar
import json
import os
import ssl

# Data Definitions
# ==============================================================================

# Image is atomic distinct (String)
# interp. A single image url

IMG1 = "https://i2.wp.com/www.geek-art.net/wp-content/uploads/2017/07/Filip-Hodas-Mario.jpg?w=1120"
IMG2 = "https://i0.wp.com/www.geek-art.net/wp-content/uploads/2017/06/Spider-Gwen-Phantom-City-Creative.jpg?w=750"


# listOfImage is one of:
# - empty
# - [Image] + [listofImage]
# - OR listOfImage.insert(0, Image)
# interp. a list of Image
LOI1 = []
LOI2 = [IMG1, IMG2]

# Template for listofImage
# def fn_for_loi(loi):
#     if len(loi) == 0:
#         ...
#     else:
#         ...
#             fn_for_image(loi[0])
#             fn_for_loi(loi[1:])


# Post is compound (title, url, date, images)
# Post is makePost(string, string, tuple, (listof Images))
# interp. a single RSS Post item with it's title, url and list of all the images in the article
class makePost:
    def __init__(self, title, url, date, images):
        self.title = title
        self.url = url
        self.date = date
        self.images = images

PST1 = makePost("SpiderGwen", "http://www.geek-art.net/en/its-spider-gwen-day-on-mondo/", (2004, 1, 1, 19, 48, 21, 3, 1, 0), LOI1)
PST2 = makePost("Post 2", "https://docs.python.org/2/tutorial/datastructures.html", (2004, 1, 1, 19, 48, 21, 3, 1, 0), LOI2)
PST3 = makePost("Post 3", "https://url.html", (2004, 1, 1, 19, 48, 21, 3, 1, 0), LOI2)

# Template for post
# def fn_for_post(post):
#     ...
#         post.title
#         post.url
#         fn_for_loi(post.images)

# listOfPosts is one of:
# - empty
# - [Post] + [listofPosts]
# - OR listOfPosts.insert(0, Image)
# interp. a list of Image
LOP1 = []
LOP2 = [PST1, PST2]
LOP3 = [PST1, PST2, PST3]

# Template for listofPosts
# def fn_for_lop(lop):
#     if len(lop) == 0:
#         ...
#     else:
#         ...
#             fn_for_post(loi[0])
#             fn_for_lop(lop[1:])

# ImageElement is compound (url, source, date)
# ImageElement is makeImgEle (string, string, integer)
# interp. a single image element with it's image url, source url and post date
# TODO
class makeImgEle:
    def __init__(self, url, source, date):
        self.url = url
        self.source = source
        self.date = date

IE1 = makeImgEle("www.image.com/image1.jpg", "www.url1.com", 1234)
IE2 = makeImgEle("www.image.com/image2.jpg", "www.url2.com", 3211)
IE3 = makeImgEle("www.image.com/image3.jpg", "www.url2.com", 2345)

# listOfImageElements is one of:
# - empty
# - [Post] + [listofPosts]
# interp. a list of Image
LOIE1 = [IE1, IE2, IE3]


# Functions
# ==============================================================================

# disable ssl verification
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Url (string) -> (listof Posts)
# Takes a URL and parses the information to return a list of Posts
# test with get_posts('http://www.geek-art.net/en/feed/')
def get_posts(url):
    # Url (string) -> (listof Posts)
    # Takes a URL and parses the information to return a list of Posts
    # TODO
    def string_to_lop(url):
        feed = feedparser.parse(url)
        # Error handling if the feed is a "bozo" (badly formed) rss feed. No data is
        # returned
        if (feed.bozo == 1):
            print ('Bozo Feed ' + feed.bozo_exception)
            return []

        lop = []
        for post in feed.entries:
            newpost = makePost("no title", "#", (2004, 1, 1, 19, 48, 21, 3, 1, 0), [])
            try:
                newpost.title = post.title
            except:
                print("post has no title tag ")
            try:
                newpost.url = post.link
            except:
                print("post has no link tag ")
            try:
                newpost.date = post.published_parsed
            except:
                print("post has no date tag ")
            try:
                newpost.images = parse_for_images(post.content)
                lop.append(newpost)
                continue
            except:
                print("post has no content tag ")
            try:
                newpost.images = html_to_loi(string_to_image(post.description))
                lop.append(newpost)
                continue
            except:
                print("post has no description tag ")
            try:
                newpost.images = html_to_loi(string_to_image(post.summary))
                lop.append(newpost)
                continue
            except:
                print("post has no summary tag ")

            print("failed to parse post " + post.link)

        return lop

    # (dictof Key/HTMLString) -> (listof Images)
    # Takes a dict of html elements and produces a list of all the images in it
    # TODO make this more general
    def parse_for_images(dict_html):
        return html_to_loi(string_to_image(dict_html[0].value))

    # (listof HTMLimgTags) -> (listof Images)
    # takes a list of HTML Img tag strings and parses them for just image src url
    def html_to_loi(list_html_img):
        return list(map(find_image, list_html_img))

    # HTMLimgTag -> ImageSourceUrl
    # parses a single html image tag (string) for the first image (png/jpg/gif) source
    # url and return it as a string
    def find_image(img):
        try:
            # removes ads
            if (img.attrs['src'].find('feedads')) == -1:
                return img.attrs['src']
        except:
            print ('no src tag in ' + img)

    # HTMLString -> (listof HTMLimgTags)
    # takes a string containing html tags and returns a list of html image tags
    def string_to_image (str):
        return BeautifulSoup(str, 'html.parser').find_all('img')

    return string_to_lop(url)

# (listof Post) -> (listof ImageElement)
# takes a list of posts and returns a combined list of all the images
def lop_to_loie(lop):
    if not lop:
        return []
    return post_to_loie(lop[0]) + lop_to_loie(lop[1:])

# Post(string, string, (listof Image)) -> (listof ImageElement)
# takes a single post and returns a list ImageElements
def post_to_loie(post):
    loie = []
    for image in post.images:
        loie.append(makeImgEle(image, post.url, calendar.timegm(post.date)))
    return loie

# (listof ImageElement) -> (listof ImageElement)
# Takes a list of image elements and sorts them by date descending
def sort_date(loie):
    return sorted(loie, key=lambda x: x.date, reverse=True)

# URL(string) -> (listof ImageElements)
# takes a url and returns a list of all the image elements
def get_images(url):
    return lop_to_loie(get_posts(url))

# (listof ImageElements) -> (array JSON)
# Takes a list of image elements and returns a webfriendly array of json
def loie_to_json(loie):
    return json.JSONEncoder().encode(list(map(lambda x: x.__dict__, loie)))

# URL -> (array JSON)
# takes a url and produces an array of image elements in json format
def url_to_json(url):
    return loie_to_json(get_images(url))

# (listof URL) -> (listof ImageElement)
# Takes a list of URLS (strings) and returns and combined list of all ImageElements
# sorted by date
# example ["www.1.com", "www.2.com"], LOIE1
def lourl_to_loie(lourl):
    if not lourl:
        return []
    return get_images(lourl[0]) + lourl_to_loie(lourl[1:])

# JSON, Integer -> File
# takes json and writes it to a file in feed_content folder with unique website ID
def write_json (json, int):
    f = open('feed_content/' + str(int) +'.json', 'w+')
    f.write(json)
