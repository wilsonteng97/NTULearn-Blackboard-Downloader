import getpass
import os
import pathlib
import re
import ssl
import time
import urllib.request

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#Enter Credentials information here

username = "WTENG002@student.main.ntu.edu.sg"
password = ""

##

options = Options()
options.add_argument("--headless")
options.add_argument('user-agent="Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"')
driver = webdriver.Chrome(r'C:\Users\wilso\\Documents\chromedriver.exe', options=options)
driver.set_window_size(3000, 3000)

CWD = os.getcwd()

def show_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    
    if downloaded < total_size:
        printProgressBar(downloaded, total_size, prefix = 'Progress:', suffix = 'Complete', length = 50)


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

    

while True:

    if (password is None) or (username is None):

        username = input("Please input ntulearn username:   ")
        password = getpass.getpass('Password:')
        errorCheck = input("Are you sure the information are correct? press n to input again, press any other key to continue..")
        if (errorCheck == "n"):
            continue

    print("\n Loading... \n\n")

    driver.get("https://ntulearn.ntu.edu.sg/webapps/login/")
    time.sleep(1)
    driver.find_element_by_id("userNameInput").send_keys(username)
    driver.find_element_by_id("passwordInput").send_keys(password)
    driver.find_element_by_id("submitButton").click()
    driver.implicitly_wait(2)
    try:
        driver.find_element_by_id("agree_button").click()
    except:
        pass
    
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    time.sleep(2)
    lst = re.findall("termCourses",driver.page_source)
    mainCourseLink = driver.current_url
    soup = BeautifulSoup(driver.page_source,features="lxml")
    mydivs = soup.findAll("ul", {"class": "portletList-img courseListing coursefakeclass u_indent"})
    #mydivs = soup.findAll("ul", {"class": "portletList-img courseListing coursefakeclass"})

    if (len(mydivs) == 0):
        print("Log in information not correct, try again")
        username = None
        password = None
        continue
    
    else:
        break

while True:

    titleLst = []

    for div in mydivs:
        soup = BeautifulSoup(str(div),features="lxml")
        myList = soup.findAll("li")

        for lst in myList:
            title = BeautifulSoup(str(lst),features="lxml").findAll("a")
            title = (title[0].get_text())
            # title = re.findall(">(.*)<",str(title))
            titleLst.append([title])

    print(f"Welcome to NTU Lecture Content Downloader (CWD : '{CWD}')")
    print("\n Please Select the Subject: ")
    titleNamesLst = []
    for (index,item) in enumerate(titleLst):
        print(str(index + 1) + ") " + item[0])
        titleNamesLst.append(item[0])

  
    print("\n\n")

    while True:
        userChoice = (input("Please enter the course number: "))
        try:
            userChoiceInt = int(userChoice)
            if (userChoiceInt <= 0 or userChoiceInt > len(titleLst)):
                raise IndexError
            userChoiceTitle = str(titleLst[userChoiceInt - 1][0]).replace(":", "").replace("?", "")
            print(userChoiceTitle)
            
            if ("LEC" not in userChoiceTitle):
                print("This course does not have downloadable lecture videos, please try another one: ")
                continue
                
            break
                
        except ValueError:
            print("Please input only digits, not any other character: \n")
            continue
        except IndexError:
            print("Invalid Input, the choice is not listed, please try again: \n")
            continue
                                
            
    # while ("LEC" not in str(titleLst[userChoice - 1][0]) or userChoice = -1):
    #     print("This course does not have downloadable lecture videos, please try another one: ")
    #     userChoice = int(input("Please enter the course number: "))
    
  
    element = driver.find_element_by_link_text(str(titleLst[userChoiceInt - 1][0]))
    driver.execute_script("arguments[0].click();", element)

    element = driver.find_element_by_partial_link_text("Recorded Lectures")
    driver.execute_script("arguments[0].click();", element)
    time.sleep(0.3)

    soup = BeautifulSoup(driver.page_source,features="lxml")
    containerHTML = soup.findAll("ul", {"class": "contentList"})[0]
    anonymous_elements = re.findall("anonymous_element_\d+",str(containerHTML))
    print("\n")
    print("      List of Lectures      ")
    print("=============================\n")
    lectureNames = BeautifulSoup(str(containerHTML),features="lxml").findAll("li")
    lectureNamesList = []
    for (index,lectureName) in enumerate(lectureNames):
        name = BeautifulSoup(str(lectureName),features="lxml").findAll("a")
        name = [(name[0].get_text())]
        # name = re.findall(";\">(.*)\<",str(name))
        # name = [name[0][:-7]]
        print(str(index + 1) + ") " + name[0])
        lectureNamesList.append(name[0])

                                                                                                                                                                                                                                                            
    print(str(len(lectureNamesList) + 1) + ") --- Download All")
    print(str(len(lectureNamesList) + 2) + ") --- Download subset: Download From start number to end number")
    print(str(len(lectureNamesList) + 3) + ") --- Go back to previous page")
    print(str(len(lectureNamesList) + 4) + ") --- Exit")

    while True:
        print("\n\n")
        lectureIndexChoice = (input("Please select which lecture videos: "))
        try:
            lectureIndexChoice = int(lectureIndexChoice)
            if (lectureIndexChoice <= 0 or lectureIndexChoice > len(lectureNamesList) + 4):
                raise IndexError
            break
        except ValueError:
            print("Please input only digits, not any other character: \n")
            continue
        except IndexError:
            print("Invalid Input, the choice is not listed, please try again: \n")
            continue

    if (lectureIndexChoice == len(lectureNamesList) + 3):
        driver.switch_to.window(driver.window_handles[0])
        driver.get(mainCourseLink)
        continue

    skip = False
    if (lectureIndexChoice == len(lectureNamesList) + 4):
        print("Bye")
        break
        skip = True

    onlyOneVideo = True
    if (lectureIndexChoice == len(lectureNamesList) + 1):
        onlyOneVideo = False

    onlySubsetOfVideos = False
    if (lectureIndexChoice == len(lectureNamesList) + 2):
        onlyOneVideo = False
        onlySubsetOfVideos = True


    index = 0
    if (skip == False):

        startIndex = 0
        stopIndex = len(lectureNamesList)

        if (onlySubsetOfVideos):
            while True:
                startUserInput = input("Please input the start number: ")
                if (startUserInput.isdigit() and 0 < int(startUserInput) <= len(lectureNamesList)):
                    startIndex = int(startUserInput) - 1
                else:
                    print("Error input, please try again \n\n")
                    continue
                    
                endUserInput = input("Please input the end number: ")
                if (endUserInput.isdigit() and 0 < int(endUserInput) <= len(lectureNamesList)):
                    stopIndex = int(endUserInput) 
                else:
                    print("Error input, please try again \n\n")
                    continue

                break
                    
                


        for x in range(startIndex,stopIndex):
            print("\n\n")
            driver.switch_to.window(driver.window_handles[0])
            index = (lectureIndexChoice - 1 ) if (onlyOneVideo) else x
            currLectureName = str(lectureNamesList[index])
            element = driver.find_element_by_link_text(currLectureName)
            driver.execute_script("arguments[0].click();", element)

            if (onlyOneVideo == False):
                print("Downloading video " + str(index + 1) + ": " + currLectureName + "\n")
            # driver.implicitly_wait(10)
            # driver.find_element_by_id(str(anonymous_elements[lectureIndexChoice-1])).click()
            re.findall('http.*mp4', driver.page_source)


            driver.switch_to.window(driver.window_handles[1])
            html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            time.sleep(5)
            rls = re.findall('http.*mp4', driver.page_source)
            
            driver.close()

            ssl._create_default_https_context = ssl._create_unverified_context

            video_name = currLectureName + ".mp4"
            video_pth = os.path.join(CWD, userChoiceTitle, video_name)
            
            if pathlib.Path(video_pth).is_file():
                print(f"[!file-exist] {video_pth}")
                continue

            urllib.request.urlretrieve(rls[0], video_pth, show_progress)
            print("\nSuccessfully downloaded!")

            if (onlyOneVideo):
                break

    userContinueChoice = input("Do u want to download more videos? \nPress y to continue, press any other key to quit\n")
    if (userContinueChoice != "y" and userContinueChoice != "Y"):
        print("Bye")
        break

    driver.switch_to.window(driver.window_handles[0])
    driver.get(mainCourseLink)

# driver.close()
driver.quit()



# if (skip == False):
