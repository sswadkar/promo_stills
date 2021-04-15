from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import collections
import requests
import os
import cv2
import shutil
from instagrapi import Client

path = "../promo_stills/images/"
post = []
search_query = 'https://tvline.com/gallery/the-flash-season-7-photos/'
imageset = {}
def find_faces(imagePath):
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(30, 30)
    )
    return len(faces)

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")

driver = webdriver.Chrome(executable_path='../promo_stills/chromedriver',chrome_options=options)

driver.get(search_query)

links = []

for x in range(20):
    element = driver.find_element_by_xpath("//img[@alt='The Flash Season 7 Photos']")
    webdriver.ActionChains(driver).move_to_element(element ).click(element ).perform()

images = driver.find_elements_by_tag_name('img')
for image in images:
    link = image.get_attribute('src')
    if link.find("the-flash-season-7") != -1:
        links.append(link)
        
for link in links:
    image_url = link.split("?")[0]+"?w=1080"
    filename = image_url.split("/")[-1].split("?")[0]
    r = requests.get(image_url, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        if os.path.isfile(path+filename) == False:
            with open("images/"+filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            post.append(path+filename)
            print('Image sucessfully Downloaded: ', filename)
        else:
            print("Image downloaded previously")
    else:
        print('Image Couldn\'t be retreived')

for image in post:
    imageset[image] = find_faces(image)

final = sorted(imageset.items(), key=lambda kv: kv[1])

final = collections.OrderedDict(final)

instapost = []

numofimages = 0

for number in range(len(final)-1,-1,-1):
    if numofimages < 10:
        instapost.append(list(final.keys())[number])
        numofimages += 1

if len(instapost) != 0:
    bot = Client()
    bot.login("username", "password")

    album_path = instapost
    text = "caption"

    bot.album_upload(
        album_path,
        caption = text
    )
    print("Posted!")
else:
    print("No need to post")

driver.quit()
