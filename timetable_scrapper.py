from datetime import datetime

from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import json
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

# Create a list to store extracted lesson data
lesson_data = []


def parse_lesson_info(raw_info):
    """Extract structured data from the raw info text"""
    info = {}

    # Extract basic info
    for line in raw_info.split('\n'):
        if "Nazwy przedmiotów:" in line:
            info["subjectName"] = line.split(":")[1].strip()
        elif "Kody przedmiotów:" in line:
            info["subjectCode"] = line.split(":")[1].strip()
        elif "Typ zajęć:" in line:
            info["type"] = line.split(":")[1].strip()
        elif "Data zajęć:" in line:
            date_str = line.split(":")[1].strip()
            try:
                date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                info["date"] = date_str
                info["dayOfWeek"] = date_obj.strftime("%A")
            except ValueError:
                info["date"] = date_str
        elif "Godz. rozpoczęcia:" in line:
            time_str = line.split(":", 1)[1].strip()
            try:
                info["startTime"] = datetime.strptime(time_str, "%H:%M:%S").strftime("%H:%M")
            except ValueError:
                info["startTime"] = time_str
        elif "Godz. zakończenia:" in line:
            time_str = line.split(":", 1)[1].strip()
            try:
                info["endTime"] = datetime.strptime(time_str, "%H:%M:%S").strftime("%H:%M")
            except ValueError:
                info["endTime"] = time_str
        elif "Sala:" in line:
            info["room"] = line.split(":")[1].strip()
        elif "Dydaktycy:" in line:
            info["lecturers"] = line.split(":")[1].strip()

    return info

# Loop through lesson buttons in the timetable
try:
    for i in range(25):
        idLesson = "ctl00_ContentPlaceHolder1_DedykowanyPlanStudenta_PlanZajecRadScheduler_" + str(i) + "_0"
        lessonElement = driver.find_element(By.ID, idLesson)

        # Lesson Name
        lessonDescElementText = "None"
        try:
            lessonDescElement = lessonElement.find_element(By.CLASS_NAME, "rsAptContent")
            lessonDescElementText = lessonDescElement.text
            # print(f"Lesson {i} text: {lessonDesc.text}") # Here we got lesson's description, e.g. "TPO wykład s. Y s. 500"
        except NoSuchElementException:
            print("Lesson description not found with lesson id: " + str(i))

        # Hover over lesson for getting tooltip with more info
        actions.move_to_element(lessonElement).perform()
        # Wait for the hover window to appear
        tooltipWindow = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_DedykowanyPlanStudenta_RadToolTipManager1RTMPanel"))
        )

        # Save tooltip's information to the table
        parsed_info = parse_lesson_info(tooltipWindow.text.strip())
        lesson_data.append({
            "id": i,
            "description": lessonDescElementText,
            "info": parsed_info,
            "raw_info": tooltipWindow.text.strip()
        })

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

# Save the extracted data to a JSON file
with open("lessons.json", "w", encoding="utf-8") as json_file:
    json.dump(lesson_data, json_file, ensure_ascii=False, indent=4)

print(f"Saved {len(lesson_data)} lessons to structured_lessons.json")

# Close the driver
driver.quit()