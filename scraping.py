# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemispheres(browser):
   url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
   browser.visit(url)
   # Click the link, find the sample anchor, return the href
   hemisphere_image_urls = []
   for i in range(4):
       # Find the elements on each loop to avoid a stale element exception
       browser.find_by_css("a.product-item img")[i].click()
       hemi_data = scrape_hemisphere(browser.html)
       hemi_data['img_url'] = hemi_data['img_url']
       # Append hemisphere object to list
       hemisphere_image_urls.append(hemi_data)
       # Finally, we navigate backwards
       browser.back()
   return hemisphere_image_urls

def scrape_hemisphere(html_text):
   # parse html text
   hemi_soup = soup(html_text, "html.parser")
   # adding try/except for error handling
   try:
       title_elem = hemi_soup.find("h2", class_="title").get_text()
       sample_elem = hemi_soup.find("a", text="Sample").get("href")
   except AttributeError:
       # Image error will return None, for better front-end handling
       title_elem = None
       sample_elem = None
   hemispheres = {
       "title": title_elem,
       "img_url": sample_elem
   }
   return hemispheres


# def hemispheres(browser):
    
#     # Visit URL
#     url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
#     browser.visit(url)

#     # Parse the resulting html with soup
#     hemisphere_html = browser.html
#     hemisphere_soup = soup(hemisphere_html, 'html.parser')

#     # Retrieve all items for hemispheres information
#     items = hemisphere_soup.find_all('div', class_='item')

#     # 2. Create a list to hold the images and titles.
#     hemisphere_image_urls = []

#     # 3. Write code to retrieve the image urls and titles for each hemisphere.

#     main_url = "https://astrogeology.usgs.gov/"

#     # Create loop to scrape through all hemisphere information
#     for i in items:
#         hemisphere = {}
#         titles = i.find('h3').text
        
#         # create link for full image
#         link_ref = i.find('a', class_='itemLink product-item')['href']
        
#         # Use the base URL to create an absolute URL and browser visit
#         browser.visit(main_url + link_ref)
        
#         # parse the data
#         image_html = browser.html
#         image_soup = soup(image_html, 'html.parser')
#         download = image_soup.find('div', class_= 'downloads')
#         img_url = download.find('a')['href']
        
#         print(titles)
#         print(img_url)
        
#         # append list
#         hemisphere['img_url'] = img_url
#         hemisphere['title'] = titles
#         hemisphere_image_urls.append(hemisphere)
#         browser.back()
        
#     # 4. Print the list that holds the dictionary of each image url and title.
#     return hemisphere_image_urls


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())






