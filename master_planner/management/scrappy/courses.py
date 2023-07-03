import requests
from bs4 import BeautifulSoup



def fetch_course_info(code: str, en: bool=False) -> dict[str, any]:
    """
    


    return format -- {
                "examination": [{"code": 
                                 "name": 
                                 "scope":
                                 "grading"
                                 }],
                "level": str,
                "examinator": str,
                "location": str,
                "main_field": list[str]
                }

    arguments:
    code: str -- course code
    lang: str -- 'en' for english, leave empty for swedish
    """
    
    if en: url = f"https://studieinfo.liu.se/en/kurs/{code}"
    else: url = f"https://studieinfo.liu.se/kurs/{code}"
    
    r = requests.get(url)

    if r.status_code == 200:
        
        soup = BeautifulSoup(r.content, "html.parser")

        return {"examination": get_examination(soup),
                # "level": get_level(soup),
                "examinator": get_examinator(soup),
                "location": get_location(soup),
                "main_field": get_main_field(soup), 
                }
        
    raise ValueError(f'status_code {r.status_code}, probably wrong course code')

def get_examination(soup: BeautifulSoup) -> list[dict[str, str]]:
    examinations = []
    for row in soup.find("div", {"id": "examination"} ).find_all("tr")[1:]:
        temp = row.find_all("td") 
        examinations.append({"code": temp[0].text, 
                             "name": temp[1].text, 
                             "hp": temp[2].text.strip().replace('\r\n', '').split()[0], 
                             "grading": temp[3].text})
    return examinations

def get_level(soup: BeautifulSoup) -> str:
    return soup.find("section", {"class": "overview-content f-col"}).text.split('\r\n')[3].strip()

def get_examinator(soup: BeautifulSoup) -> str:
    return soup.find("section", {"class": "overview-content f-col"}).text.split('\r\n')[7].strip()

def get_location(soup: BeautifulSoup) -> str:
    return soup.find("table", {"class": "table table-striped study-guide-table"}).find_all("tr")[1].find_all("td")[-2].text

def get_main_field(soup: BeautifulSoup) -> list[str]:
    for tag in soup.find("section", {"class": "syllabus f-2col"}).find_all("h2"):
    
        if tag.text in ['Huvudområde', 'Main field of study']:
            return tag.next_sibling.strip().split(', ')
            

if __name__ == "__main__":
    
    fetch_course_info('TDDE01', en=False)
