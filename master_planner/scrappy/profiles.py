import requests
from bs4 import BeautifulSoup

def program_plan(program_code: str):
    url = f"https://studieinfo.liu.se/program/{program_code}"
    r = requests.get(url)
    
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
        semesters = soup.find_all("header", {"class": "accordion__head js-accordion-head"})
        periods = soup.find_all("tbody", {"class": "period"})
        for i in periods:
            print(i.text.split())
            
        print(len(semesters))
        
        for term in range(1, len(semesters)+1):
            if term > 6:
                courses = soup.find_all("tr", {"class": "main-row"})
                for course in courses:
                    line = course.text.split()
                    temp = [ line[0], ' '.join(line[1:-4]) ]
                    temp.extend(line[-4:])
                    #print(temp)
                            
        

def fetch_admission_years(program_code: str) -> list[str]:
    """Get url paths to admission years.

    Args:
        program_code (str): Code for the program to search for

    Returns:
        list[str]: A list of url paths to each admission year.
    """
    url = f"https://studieinfo.liu.se/program/{program_code}"
    r = requests.get(url)
    years_urls = []
    
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
        options_parent = soup.find("select", {"id": "related_entity_navigation"})
        options = options_parent.find_all("option")
        for option in options:
            years_urls.append(option["value"])
        
        return years_urls
    return []
    
def fetch_profiles(program_code: str) -> tuple[str]:
    """Get profiles for specific program.

    Args:
        program_code (str): Code for the program to search for

    Returns:
        tuple[str]: A tuple containing the profile name and its 
                    corresponding profile code
    """
    url = f"https://studieinfo.liu.se/program/{program_code}"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
        option_parent = soup.find("select", {"id": "specializations-filter"})
        values = option_parent.find_all("option")
        profile_id = []
        profile_names = []
        for option in values:
            profile_id.append(option["value"])
            
        for option in option_parent.children:
            profile_names.append(option.get_text(strip=True))
        
        profile_names = list(filter(lambda a: a != "", profile_names))
        profiles = list(zip(profile_names[1:], profile_id[1:]))
        return profiles

    return tuple()

print(program_plan("6CMJU"))