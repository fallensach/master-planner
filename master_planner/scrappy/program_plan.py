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
        
        self.program_code = program_code
        self.program_name = self.program_n()
        
    def format_course_scrape(self, courses_raw: ResultSet[any]) -> list[dict[str, any]]:
        """Parses and formats a soup object containing the tags "tr", {"class": "main-row"}.
        This tag will contain courses in raw soup format.

        Args:
            courses_raw (ResultSet[any]): the raw course format taken from bs4

        Returns:
            list[dict[str, any]]: All the scraped courses
        """
        courses = []
        for course in courses_raw:
            line = course.text.split()
            temp = [line[0], ' '.join(line[1:-4])]
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
           
    def planned_courses(self, profile_code: str = None) -> list[dict[str, list[dict[str, any]]]]:
        """Get all the courses for the whole program or a profile sorted by their semester and period.
        This function is used whenever you need the ordered program plan.

        Args:
            profile_code (str): code of given profile

        Returns:
            list[dict[str, list[dict[str, any]]]]: All the courses for the given profile
        """
        
        if profile_code is not None: 
            semesters = self.soup.find_all("div", {"data-specialization": {profile_code}})
        else:
            semesters = self.soup.select('div.specialization[data-specialization=""]')
        
        if profile_code is None:
            term_start = MASTER_TERM_START
            profile_start = 0
        else:
            term_start = 0
            profile_start = MASTER_TERM_START - 1

        program_courses = []
        for index, semester in enumerate(semesters, 1):
            if index >= term_start:
                periods = semester.find_all("tbody", {"class": "period"})
                s_string = f"Termin {profile_start + index}"
                semester_courses = {s_string: []}
                
                for i, period in enumerate(periods, 1):
                    courses = period.find_all("tr", {"class": "main-row"})
                    semester_courses[s_string].append({f"Period {i}" : self.format_course_scrape(courses)})
                program_courses.append(semester_courses)
        
        return program_courses

    def courses(self, profile_code: str = None) -> list[dict[str, any]]:
        """Get all courses of a program or profile in a list that is unordered.
        Does not specify any semester or peroid just the courses.

        Args:
            profile_code (str, optional): _description_. Defaults to None.

        Returns:
            list[dict[str, any]]: _description_
        """
        if profile_code is not None: 
            semesters = self.soup.find_all("div", {"data-specialization": {profile_code}})
        else:
            semesters = self.soup.select('div.specialization[data-specialization=""]')
        
        if profile_code is None:
            term_start = MASTER_TERM_START
        else:
            term_start = 0
            
        program_courses = []
        for index, semester in enumerate(semesters, 1):
            if index >= term_start:
                courses = semester.find_all("tr", {"class": "main-row"})
                program_courses.append(self.format_course_scrape(courses))
            
        return sum(program_courses, [])

    def admission_years(self) -> dict[int, str]:
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
        
    def profiles(self) -> tuple[str]:
        """Get profiles for specific program.

        Args:
            program_code (str): Code for the program to search for

        Returns:
            tuple[str]: A tuple containing the profile name and its 
                        corresponding profile code
        """
        option_parent = self.soup.find("select", {"id": "specializations-filter"})
        values = option_parent.find_all("option")
        profile_id = []
        profile_names = []
        for option in values:
            profile_id.append(option["value"])
            
        for option in option_parent.children:
            profile_names.append(option.get_text(strip=True))
        
        profile_names = list(filter(lambda a: a != "", profile_names))
        profiles = list(zip(profile_names[1:], profile_id[1:]))
        return dict(profiles)

    def program_n(self) -> str:
        headers = self.soup.find_all("header", {"class": ""})
        for header in headers:
            title = header.find("h1")
            return title.text.split(",")[0]


def main():
    plan = ProgramPlan("6CMJU")
    pprint.pprint(plan.courses())
    #plan.program_name()

if __name__ == "__main__":
    main()