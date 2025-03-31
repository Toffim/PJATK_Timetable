from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import time

driver = webdriver.Chrome()
driver.get("https://planzajec.pjwstk.edu.pl/Logowanie.aspx")

# For hover actions etc.
actions = ActionChains(driver)

# Use this:
with open("password.txt", "r") as f:
    password = f.read().strip()
# Or just:
# password = "ILoveJava"

# Use this:
with open("studentIndex.txt", "r") as f:
    studentIndex = f.read().strip()
# Or just:
# studentIndex = "s10101"

# Login
driver.find_element(By.ID, "ContentPlaceHolder1_Login1_UserName").send_keys(studentIndex)
driver.find_element(By.ID, "ContentPlaceHolder1_Login1_Password").send_keys(password)
driver.find_element(By.ID, "ContentPlaceHolder1_Login1_LoginButton").click()

# Wait for login to complete
WebDriverWait(driver, 10).until(
    EC.url_contains("TwojPlan.aspx")
)

# Loop through lesson buttons in the timetable
try:
    for i in range(25):
        idLesson = "ctl00_ContentPlaceHolder1_DedykowanyPlanStudenta_PlanZajecRadScheduler_" + str(i) + "_0"
        lessonElement = driver.find_element(By.ID, idLesson)

        # Lesson Name
        try:
            lessonDesc = lessonElement.find_element(By.CLASS_NAME, "rsAptContent")
            # print(f"Lesson {i} text: {lessonDesc.text}") # Here we got lesson's description, e.g. "TPO wykład s. Y s. 500"
        except NoSuchElementException:
            print("Lesson description not found with lesson id: " + str(i))

        # Hover over lesson for getting tooltip with more info
        actions.move_to_element(lessonElement).perform()
        # Wait for the hover window to appear
        hoverWindow = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_DedykowanyPlanStudenta_RadToolTipManager1RTMPanel"))
        )

        print(hoverWindow.text)
        print("\n")

        # Move cursor away to dismiss hover, I used a trick here, so I'm clicking "Today/Dziś" to refresh page
        # It's because PJATK's timetable has very badly coded tooltips...
        element = driver.find_element(By.CLASS_NAME, "rsToday")
        actions.move_to_element(element).perform()
        element.click()
        # Sleep required, the web driver wait, won't work here in that case
        # I only have theory that PJATK's API has some limiters and with this bad tooltips we have to wait
        time.sleep(1)
except NoSuchElementException:
    print("Lesson not found with id: " + str(i))