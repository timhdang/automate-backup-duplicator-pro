from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import config #import config.py
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import datetime
import numpy as np
import csv
import re
from PIL import Image
from io import BytesIO
import requests
from word2number import w2n
import threading
import smtplib
from email.mime.image import MIMEImage
from email.message import EmailMessage
from email.mime.text import MIMEText
# And imghdr to find the types of our images
import imghdr
from email.utils import make_msgid

msg = EmailMessage()

asparagus_cid = make_msgid()
msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'
msg.set_content('Daily Backup Report!')

def send_email(time_stamp, image):
    header = 'Daily Backup WordPress' + time_stamp
    msg['Subject'] = header
    msg['From'] = config.smtp_account
    msg['To'] = config.smtp_account
    # Send the message via our own SMTP server.
    server = smtplib.SMTP('smtp-relay.sendinblue.com', 587)
    server.ehlo()
    server.starttls()
    server.login(config.smtp_account,config.smtp_password)
    msg.add_alternative("""\
    <html>
    <head></head>
    <body>
        <p>Daily Backup Report.</p>
        <p>
            Screenshot of backup is in the attachment        
        </p>
        <img src="cid:{asparagus_cid}" />
    </body>
    </html>
    """.format(asparagus_cid=asparagus_cid[1:-1]), subtype='html')
    # open image as a binary file and read the contents
    with open(fname, 'rb') as img:
	    msg.get_payload()[1].add_related(img.read(), 'image', 'jpeg', cid=asparagus_cid)
    # attach image to email 
    msg.attach(MIMEText("body", "plain"))
    server.send_message(msg)
    print("Email sent!")

def take_screenshot(element, driver, filename='screenshot.png'):
  location = element.location_once_scrolled_into_view
  size = element.size
  png = driver.get_screenshot_as_png() # saves screenshot of entire page

  im = Image.open(BytesIO(png)) # uses PIL library to open image in memory

  left = location['x']
  top = location['y']
  right = location['x'] + size['width']
  bottom = location['y'] + size['height']
  im = im.crop((left, top, right, bottom)) # defines crop points
  im.save(filename) # saves new cropped image



def doMath(num1, num2, ops): 
    n1 = w2n.word_to_num(num1)
    n2 = w2n.word_to_num(num2)
    print(n1)
    print(ops)
    print(n2)
    if (ops == "+"):
        return n1 + n2
    elif (ops == "−"):
        return n1 - n2
    elif (ops == "×"):
        return n1 * n2
    else :
        return n1/n2

driver = webdriver.Chrome()
driver.get("https://change-me.com/change-me") #login url

driver.implicitly_wait(2)
username = driver.find_element_by_id("user_login")
password = driver.find_element_by_id("user_pass")
username.send_keys(config.wp_acc)
password.send_keys(config.wp_password)
driver.implicitly_wait(2)
#DEBUG
e = driver.find_element_by_css_selector("#loginform > div.aiowps-captcha-equation > strong")
take_screenshot(e, driver,"screenshot.png")
#print(e.text)

e_array = e.text.split(" ")
math_res = doMath(e_array[0], e_array[2], e_array[1])
print(math_res)
captcha_answer = driver.find_element_by_id("aiowps-captcha-answer")
captcha_answer.send_keys(math_res)

# click submit
wp_submit = driver.find_element_by_id("wp-submit")
wp_submit.click()

driver.implicitly_wait(15)

input_check_box_checked = None
def clickCheckBox():
  global input_check_box_checked
  if (input_check_box_checked != True):
    threading.Timer(5.0, clickCheckBox).start()
    try:
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)
        input_check_box = driver.find_element_by_id("dup-scan-warning-continue-checkbox")
        input_check_box.click()
        input_check_box_checked = True
        if (input_check_box.is_selected()):
            print("input_check_box clicked!")
        else: 
            print("Scanning Site") #popup later
    except:
        print("Not found") #popup later
    

driver.implicitly_wait(3)
duplicator_pro_page =  driver.get("https://change-me.com/wp-admin/admin.php?page=duplicator-pro")
driver.implicitly_wait(3)

create_new = driver.find_element_by_id("dup-pro-create-new")
try:    
    create_new.click()
    print("Build Creation Starts")
except:
    print("Build Creation Stops")


html = driver.find_element_by_tag_name('html')
html.send_keys(Keys.END)
next_btn = driver.find_element_by_id("button-next")
next_btn.click()
driver.implicitly_wait(8)

import pymsgbox
count = 0
while (count < 5):
    clickCheckBox()
    print("loop = " + str(count))
    count = count+1

html = driver.find_element_by_tag_name('html')
html.send_keys(Keys.END)
build = driver.find_element_by_id("dup-build-button")
build.click()    
pymsgbox.alert('Data backup created successfully','OK')
time_stamp =  datetime.datetime.now().strftime("%DD%MM").replace('/','')
driver.save_screenshot("screenshot" + time_stamp +".png")
fname = "screenshot" + time_stamp +".png"
send_email(time_stamp, fname)




