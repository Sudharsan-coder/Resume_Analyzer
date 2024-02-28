import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

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
                # if similarity_score>max_score:
                match_result["Title"]=title
                match_result["link"]=link
                match_result["snippet"]=snippet
                # max_score=similarity_score
                # print("Title:", title)
                # print("Link:", link)
                # print("snippet", snippet)
                # print("Similarity Score:", similarity_score)
                # print("------")
                break
    return match_result


employee_name = "Yokesh G"
position = "Product Engineering Intern"
company_name = "Codingmart"

query = f"{employee_name} - {position} at {company_name}"

# print("ans",scrape_search_results(query))
