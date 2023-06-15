import requests
from bs4 import BeautifulSoup, ResultSet
import pprint
from datetime import date

MASTER_TERM_START = 7

class ProgramPlan:
    """
    ProgramPlan has useful features to webscrape LiU's courses for a given program. 
    This webscraping tool puts the scraped content into readable data structures for easier management of data.
    This includes: 
        * fetching profile names and their respective code
        * getting a profile's courses
        * getting the all the courses for a given program
        * getting urls to each admissions year
    """
    def __init__(self, program_code: str):
        self.url = f"https://studieinfo.liu.se/program/{program_code}"
        
        r = requests.get(self.url)
        if r.status_code == 200:
            self.soup = BeautifulSoup(r.content, "html.parser")
        else:
            raise requests.exceptions.HTTPError(f"Given program {program_code} does not exist.")
    

    def profile_courses(self, profile_code: str) -> list[dict[str, dict[str, any]]]:
        """Get all the courses for a given profile

        Args:
            profile_code (str): code of given profile

        Returns:
            list[dict[str, dict[str, any]]]: All the courses for the given profile
        """
        semesters = self.soup.find_all("div", {"data-specialization": profile_code})
        p_courses = []
        for index, semester in enumerate(semesters):
            periods = semester.find_all("tbody", {"class": "period"})
            for i, period in enumerate(periods, 1):
                courses = period.find_all("tr", {"class": "main-row"})
                p_courses.append(
                    {
                        f"Termin {MASTER_TERM_START + index}": 
                        {f"Period {i}" : self.format_course_scrape(courses)}
                    }
                )
                
        
        return p_courses

    def format_course_scrape(self, courses_raw: ResultSet[any]) -> list[dict[str, any]]:
        """Parses and formats a soup object containing "tr", {"class": "main-row"}.
        This tag will contain courses in raw format.

        Args:
            courses_raw (ResultSet[any]): the raw course format taken from bs4

        Returns:
            list[dict[str, any]]: All the scraped courses
        """
        courses = []
        for course in courses_raw:
            line = course.text.split()
            temp = [line[0], ' '.join(line[1:-4]) ]
            temp.extend(line[-4:])
            course_map = {
                "course_code": temp[0],
                "course_name": temp[1],
                "hp": temp[2],
                "level": temp[3],
                "block": temp[4],
                "vof": temp[5]
            }
            courses.append(course_map)

        return courses

    def program_plan(self): 
        semesters = self.soup.select('div.specialization[data-specialization=""]')
        
        program_courses = []
        for index, semester in enumerate(semesters, 1):
            if index >= MASTER_TERM_START:
                periods = semester.find_all("tbody", {"class": "period"})
                for i, period in enumerate(periods, 1):
                    courses = period.find_all("tr", {"class": "main-row"})
                    program_courses.append(
                        {
                            f"Termin {index}": 
                            {f"Period {i}" : self.format_course_scrape(courses)}
                        }
                    )
        
        return program_courses

                                
    def courses(self, profile_code=None) -> list[dict[str, any]]:
        """Get all the courses for the whole program or a profile.

        Args:
            profile_code (str): code of given profile

        Returns:
            list[dict[str, dict[str, any]]]: All the courses for the given profile
        """
        
        if profile_code is not None: 
            semesters = self.soup.find_all("div", {"data-specialization": {profile_code}})
        else:
            semesters = self.soup.select('div.specialization[data-specialization=""]')
        
        if not semesters:
            raise ValueError(f"Profile {profile_code} does not exist.")
        
        term_start = MASTER_TERM_START if profile_code is None else 0

        # FIX BUG WITH TERMIN WHEN PICKING PROFILE
        program_courses = []
        for index, semester in enumerate(semesters, 1):
            if index >= term_start:
                periods = semester.find_all("tbody", {"class": "period"})
                for i, period in enumerate(periods, 1):
                    courses = period.find_all("tr", {"class": "main-row"})
                    program_courses.append(
                        {
                            f"Termin {term_start + index}": 
                            {f"Period {i}" : self.format_course_scrape(courses)}
                        }
                    )
        
        return program_courses

    def fetch_admission_years(self) -> dict[int, str]:
        """Get url paths to admission years.

        Args:
            program_code (str): Code for the program to search for

        Returns:
            list[str]: A list of url paths to each admission year.
        """
        years_urls = {}
    
        options_parent = self.soup.find("select", {"id": "related_entity_navigation"})
        options = options_parent.find_all("option")
        for i, option in enumerate(options):
            years_urls[date.today().year - i] = option["value"]
        
        return years_urls
        
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

def main():
    plan = ProgramPlan("6CMJU")
    #plan.profile_courses("DAIM")
    pprint.pprint(plan.courses("DAIM"))
    #pprint.pprint(plan.profile_courses("DAIM"))
    #print(plan.fetch_admission_years())
    #pprint.pprint(plan.program_plan())

if __name__ == "__main__":
    main()