import getpass
import os
import pathlib
import re
import ssl
import sys
import time
import urllib

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

# Enter Credentials information here
username = "WTENG002@student.main.ntu.edu.sg"
password = ""
CHUNK_SIZE = 1024 * 1024 # 1MB

# Keywords to access
KEYWORDS_MAIN = ['Content', 'material']
KEYWORDS_SIDEBAR_FOLDERS = ['Lecture Slides', 'Tutorials', 'Labs', 'eLearning Week', 'Additional Material', 'Top10MainCausesofFailures']

# Chromedriver options
options = Options()
options.add_argument("--headless")
options.add_argument('user-agent="Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"')
driver = webdriver.Chrome(r'C:\Users\wilso\\Documents\chromedriver.exe', options=options)
driver.set_window_size(3000, 3000)

CWD = os.getcwd()
MOTHER_LINK = r'https://ntulearn.ntu.edu.sg'
global requests_session, response # requests session
requests_session = requests.Session() # requests session

def check_url(url):
    if MOTHER_LINK not in url:
        url = MOTHER_LINK + url
    return url

def print_level(level):
    if level >= 1:
        print("|_", end="")
        for _ in range(level-1):
            print("._", end="")
        print(" ", end="")

def download_file(url, save_dir):
    save_dir = save_dir.replace(":", "").replace("?", "")
    # ext = os.path.splitext(save_dir)[1][1:]
    # if ext == "mp4":
    #     print(f"Video: Not downloaded - {save_dir}")
        # return (True, save_dir)
    if pathlib.Path(save_dir).is_file():
        print("[!file-exist]")
        return (False, save_dir)
    if not os.path.exists(os.path.dirname(save_dir)):
        os.makedirs(os.path.dirname(save_dir))
    with requests_session.get(url, stream=True) as response:
        with open(save_dir, 'wb') as handle:
            for data in tqdm(response.iter_content(chunk_size=CHUNK_SIZE)): # 1MB
                handle.write(data)
    return (True, save_dir)

def find_course_material_keywords(keyword_ls):    
    valid_keywords = []
    for idx, keyword in enumerate(keyword_ls):
        try:
            driver.find_element_by_partial_link_text(keyword)
            valid_keywords.append(keyword)
            print(f"[!VALID KEYWORD] ({idx+1}) {keyword}")
        except:
            pass
    return valid_keywords

def download_folder(href, folder_name, path_name, level=1):
    curr_url = driver.current_url
    driver.get(href)

    soup = BeautifulSoup(driver.page_source,features="lxml")
    containerHTML = soup.findAll("ul", {"class": "contentList"})[0]
    anonymous_elements = re.findall("anonymous_element_\d+",str(containerHTML))
    ContentNames = BeautifulSoup(str(containerHTML),features="lxml").find("ul").findAll("li", recursive=False)
    print("Parent Length : ", len(ContentNames))

    ContentNamesList = []
    for (index, contentName) in enumerate(ContentNames):
        children = BeautifulSoup(str(contentName),features="lxml").findAll("a", href=True)
        # print(f"Children len : {len(children)}")
        for child in children:
            name = child.get_text()
            if name == "":
                print("[!EMPTY CHILD]")
                continue
            ContentNamesList.append(name)
            url = check_url(child['href'])
            if "/webapps/blackboard/content/listContent.jsp" in child['href']:
                # is folder
                download_folder(url, name, os.path.join(path_name, folder_name), level=level+1)
            elif "/bbcswebdav/" in child['href']:
                # is file
                print_level(level)
                print(f"{index + 1}) {name} ")
                success = download_file(url, os.path.join(path_name, folder_name, name))
                if (success[0]): NEWLY_DOWNLOADED_FILES.append(success[1])
    driver.get(curr_url)

def access_and_download_files(keyword, base_path):
    element = driver.find_element_by_partial_link_text(keyword)
    driver.execute_script("arguments[0].click();", element)
    soup = BeautifulSoup(driver.page_source,features="lxml")
    containerHTML = soup.findAll("ul", {"class": "contentList"})
    if len(containerHTML) == 0: 
        print("[!INFO] No content to download.\n")
        driver.switch_to.window(driver.window_handles[0])
        driver.get(mainCourseLink)
        return
    containerHTML = containerHTML[0]
    anonymous_elements = re.findall("anonymous_element_\d+",str(containerHTML))
    print("\n")
    print("      List of Content      ")
    print("=============================")
    ContentNames = BeautifulSoup(str(containerHTML),features="lxml").find("ul").findAll("li", recursive=False)
    print("Parent Length : ", len(ContentNames))
    ContentNamesList = []
    for (index, contentName) in enumerate(ContentNames):
        children = BeautifulSoup(str(contentName),features="lxml").findAll("a", href=True)
        for child in children:
            name = child.get_text()
            print(f"{index + 1}) {name} ")
            ContentNamesList.append(name)
            url = check_url(child['href'])
            if "/webapps/blackboard/content/listContent.jsp" in child['href']:
                # is folder
                download_folder(url, name, base_path)
            elif "/bbcswebdav/" in child['href']:
                # is file
                success = download_file(url, os.path.join(base_path, str(name)))
                if (success[0]): NEWLY_DOWNLOADED_FILES.append(success[1])

    driver.switch_to.window(driver.window_handles[0])
    driver.back()


if __name__ == "__main__":
    while True:
        print("\n Loading... \n\n")
        login_url = "https://ntulearn.ntu.edu.sg/webapps/login/"

        driver.get(login_url)
        time.sleep(1)
        # driver.implicitly_wait(2)
        driver.find_element_by_id("userNameInput").send_keys(username)
        driver.find_element_by_id("passwordInput").send_keys(password)
        driver.find_element_by_id("submitButton").click()
        driver.implicitly_wait(2)
        try:
            driver.find_element_by_id("agree_button").click()
        except:
            pass

        cookies = driver.get_cookies()
        for cookie in cookies:
            requests_session.cookies.set(cookie['name'], cookie['value'])

        html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        time.sleep(1)
        lst = re.findall("termCourses",driver.page_source)
        mainCourseLink = driver.current_url
        soup = BeautifulSoup(driver.page_source,features="lxml")
        mydivs = soup.findAll("ul", {"class": "portletList-img courseListing coursefakeclass u_indent"})

        if (len(mydivs) == 0):
            print("Log in information incorrect, try again")
            username = None
            password = None
        else:
            break

    # Find courses
    courseLst = []
    
    for div in mydivs:
        soup = BeautifulSoup(str(div),features="lxml")
        myList = soup.findAll("li")

        for lst in myList:
            course = BeautifulSoup(str(lst),features="lxml").findAll("a")
            course = course[0].get_text()
            courseLst.append(course)

    while True:
        NEWLY_DOWNLOADED_FILES = []

        print(f"Welcome to NTU Lecture Content Downloader (CWD : '{CWD}')")
        print("\n   Please Select the Subject: ")
        for (index, item) in enumerate(courseLst):
            print(f"{index+1}) {item}")
        
        download_all_int = len(courseLst) + 1
        print("--------------------------------")
        print(f"{download_all_int}) --- Download All")

        print("\n\n")

        while True:
            userChoice = (input("Please enter the course number: "));
            try:
                all = False
                userChoiceInt = int(userChoice)
                if (userChoiceInt <= 0 or userChoiceInt > len(courseLst)+1):
                    raise IndexError
                if userChoiceInt == download_all_int:
                    userChoiceCourseLst = courseLst
                else:
                    userChoiceCourseLst = [str(courseLst[userChoiceInt - 1])]
                print(userChoiceCourseLst)
                break
            except ValueError:
                print("[!ERROR] Please input only digits, not any other character.\n")
                continue
            except IndexError:
                print("[!ERROR] Invalid Input, the choice is not listed, please try again.\n")
                continue
    
        for course in userChoiceCourseLst:
            skip = False
            print(f"Curr course : {course}");
            element = driver.find_element_by_link_text(course);
            driver.execute_script("arguments[0].click();", element);

            # Download from main course materials folder
            valid_main_keyword = find_course_material_keywords(KEYWORDS_MAIN)
            print(f"[!INFO] No. of valid keywords (Main): {len(valid_main_keyword)}")
            for idx, keyword in enumerate(valid_main_keyword):
                try:
                    access_and_download_files(keyword, course)
                except StaleElementReferenceException:
                    print(f"[!ERROR] {idx} {keyword} - StaleElementReferenceException")
            
            # Download from course material folders organised in sidebar
            valid_sidebar_folder_keywords = find_course_material_keywords(KEYWORDS_SIDEBAR_FOLDERS)
            print(f"[!INFO] No. of valid keywords (Sidebar folders): {len(valid_sidebar_folder_keywords)}")
            for idx, keyword in enumerate(valid_sidebar_folder_keywords):            
                try:
                    access_and_download_files(keyword, os.path.join(course, str(keyword)))
                except StaleElementReferenceException:
                    print(f"[!ERROR] {idx} {keyword} - StaleElementReferenceException")
                
            print("--------------------------------")
            print(f"[!INFO] Download finished for [{course}]\n")
            # driver.switch_to.window(window_before)
            driver.get(mainCourseLink)

        if NEWLY_DOWNLOADED_FILES:
            print(f"\n================= New Files ({len(NEWLY_DOWNLOADED_FILES)}) =================")
            print(*NEWLY_DOWNLOADED_FILES, sep="\n")
            print()

        driver.switch_to.window(driver.window_handles[0])
        driver.get(mainCourseLink)

driver.quit()