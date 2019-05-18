from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime as dt


def scrape_all():

    browser = Browser("chrome", executable_path="chromedriver.exe", headless=True)
    news_title, news_paragraph = mars_news(browser)
    
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    browser.quit()
    return data


def mars_news(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    html = browser.html
    soup = bs(html, "html.parser")

    try:
        news_title = soup.find("div", class_="content_title").get_text()
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    browser.find_by_id("full_image").click()

    # Find the more info button and click that
    browser.is_element_present_by_text("more info", wait_time=0.5)
    more_info_elem = browser.find_link_by_partial_text("more info")
    more_info_elem.click()

    
    html = browser.html
    img_soup = bs(html, 'html.parser')

    image = img_soup.find('img',class_='main_image')
    
    try:
        image_src = image.get("src")

    except AttributeError:
        return None

    featured_img_url = f'https://www.jpl.nasa.gov/spaceimages/{image_src}'
    
    return featured_img_url


def twitter_weather(browser):
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    html = browser.html
    weather_soup = bs(html, "html.parser")

    # First, find a tweet with the data-name `Mars Weather`
    tweet_attrs = {"class": "tweet", "data-name": "Mars Weather"}
    mars_weather_tweet = weather_soup.find("div", attrs=tweet_attrs)

    # Next, search within the tweet for the p tag containing the tweet text
    mars_weather = mars_weather_tweet.find("p", "tweet-text").get_text()

    return mars_weather


def mars_facts():
    try:
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["description", "value"]
    df.set_index("description", inplace=True)

    # Add some bootstrap styling to <table>
    return df.to_html(classes="table table-striped")


def scrape_hemisphere(html_text):

    hemi_soup = bs(html_text, "html.parser")

    # Try to get href and text except if error.
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:

        # Image error returns None for better front-end handling
        title_elem = None
        sample_elem = None

    hemisphere = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemisphere


def hemispheres(browser):

    # A way to break up long strings
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(url)
    
    hemisphere_image_urls = []
    for i in range(4):
        
        browser.find_by_css("a.product-item h3")[i].click()

        hemi_data = scrape_hemisphere(browser.html)

        hemisphere_image_urls.append(hemi_data)

        browser.back()

    return hemisphere_image_urls


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())