import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO

chrome_path = os.path.join(os.path.dirname(__file__), '../drivers', 'chromedriver')
chrome_options1 = Options()
chrome_options1.add_argument("--incognito")
# chrome_options1.add_argument("--headless")
driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options1)

baseurl = 'https://twitter.com/GrandpaPen/status/'
tweet_1 = '1217738319880060928'
tweet_2 = '1217341587409162240'
tweet_3 = '1217039541539758080'
tweet_4 = '1216943724262879232'

def screenshotPost(postid):
    driver.get(baseurl + postid)
    # css-1dbjc4n r-my5ep6 r-qklmqi r-1adg3ll
    post_content = driver.find_element_by_class_name('permalink-tweet-container')
    location = post_content.location
    size = post_content.size
    png = driver.get_screenshot_as_png()  # saves screenshot of entire page
    im = Image.open(BytesIO(png))  # uses PIL library to open image in memory

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']

    im = im.crop((left, top, right, bottom))  # defines crop points
    return im

im_1 = screenshotPost(tweet_1)
im_2 = screenshotPost(tweet_2)
im_3 = screenshotPost(tweet_3)
im_4 = screenshotPost(tweet_4)

width_1, height_1 = im_1.size
width_2, height_2 = im_2.size
width_3, height_3 = im_3.size
width_4, height_4 = im_4.size

hgap = 10
ygap = 20

row_1_width = width_1 + width_2
row_1_height = max(height_1, height_2)

row_2_width = width_3 + width_4
row_2_height = max(height_3, height_4)

total_width = max(row_1_width, row_2_width) + hgap
total_height = row_1_height + row_2_height + ygap

new_im = Image.new('RGBA', (total_width, total_height), (255, 255, 255, 0))

x_offset = 0
y_offset = 0

new_im.paste(im_1, (x_offset, y_offset))
x_offset += width_1 + hgap

new_im.paste(im_2, (x_offset, y_offset))
x_offset = 0
y_offset += row_1_height + ygap

new_im.paste(im_3, (x_offset, y_offset))
x_offset += width_3 + hgap

new_im.paste(im_4, (x_offset, y_offset))

new_im.save('./res/screenshot_combined.png')             # saves new cropped image
