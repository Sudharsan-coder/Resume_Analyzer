import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth
import time

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def scrape_search_results(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    match_result={}
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('div', class_='tF2Cxc')
        # max_score=0
        
        for result in search_results:
            try:
                title = result.find('h3').text
            except AttributeError:
                title = ""

            try:
                link = result.find('a')['href']
            except TypeError:
                link = ""

            snippet = result.find('div', class_='VwiC3b').text
            
            similarity_score = similar(query, title)
            if similarity_score >= 0.2:
                match_result["Title"]=title
                match_result["link"]=link
                match_result["snippet"]=snippet
                break
    return match_result


employee_name = "Yokesh G"
position = "Product Engineering Intern"
company_name = "Codingmart"

query = f"{employee_name} - {position} at {company_name}"

# print("ans",scrape_search_results(query))


async def scrape_udemy_or_coursera_courses(link,selector,course):
    url = f"{link}{course}"

    browser = await launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
    page = await browser.newPage()
    
    await stealth(page)
    
    # Enable stealth mode (emulate human-like behavior)
    await page.evaluateOnNewDocument('() => { Object.defineProperty(navigator, "webdriver", { get: () => false }); }')
    
    await page.goto(url)
    time.sleep(5)
    # await page.screenshot({'path': 'sc.png', 'fullPage': True, 'quality': 100})
    # Wait for the page to load (you can adjust the delay as needed)
    await page.waitForSelector(selector, timeout=5000)

    # Extract course names and prices
    courses = await page.evaluate(f'''(selector) => {{
        const courseElements = document.querySelectorAll(selector);
        const courseData = [];
        for (const course of courseElements) {{
            const name = course.querySelector('h3').textContent.trim();
            const desc = (course.querySelectorAll('p')[1] ?? course.querySelector('p')).textContent.trim();
            const thumbnail = course.querySelector('img').getAttribute('src');
            const link ="www.coursera.com"+course.querySelector('a').getAttribute('href');
            courseData.push({{ name, desc, thumbnail, link }});
        }}
        return courseData;
    }}''', selector)
    
    await browser.close()
    # if(link.find("coursera")):
    #     course
    return courses


async def course_suggestion(courseName):
    udemy_cls_name='.course-card-module--large--AL3kI'
    udemyLink='https://www.udemy.com/courses/search/?src=ukw&q='
    coursera_cls_name = '.cds-ProductCard-gridCard'
    courseraLink = 'https://www.coursera.org/search?query='
    courses_data = await scrape_udemy_or_coursera_courses(courseraLink, coursera_cls_name, courseName)
    return courses_data



# main("java")
# asyncio.run(main("java"))
# print(arr[0])
