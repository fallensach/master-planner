import requests
from bs4 import BeautifulSoup, ResultSet
import pprint
from datetime import date
# from .courses import fetch_course_info

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

        year = self.admission_years()[2020]
        self.url = f"https://studieinfo.liu.se/program/{year}"
        self.program_code = program_code
        self.program_name = self.program_n()
        
    def format_course_scrape(self, course_raw: ResultSet[any]) -> list[dict[str, any]]:
        """Parses and formats a soup object containing the tags "tr", {"class": "main-row"}.
        This tag will contain courses in raw soup format.

        Args:
            courses_raw (ResultSet[any]): the raw course format taken from bs4

        Returns:
            list[dict[str, any]]: All the scraped courses
        """
        
        
        line = course_raw.text.split()
        temp = [line[0], ' '.join(line[1:-4])]
        temp.extend(line[-4:])
        if len(temp[2]) > 3:
            temp[1:2] = [" ".join(temp[1:3])]
            temp.pop(2)      
            temp.insert(4, "-") 
            
        course_map = {
            "course_code": temp[0],
            "course_name": temp[1],
            "hp": temp[2],
            "level": temp[3],
            "block": temp[4],
            "vof": temp[5]
        }

        return course_map
           
    # def planned_courses(self, profile_code: str = None) -> list[dict[str, list[dict[str, any]]]]:
    #     """Get all the courses for the whole program or a profile sorted by their semester and period.
    #     This function is used whenever you need the ordered program plan.
    #
    #     Args:
    #         profile_code (str): code of given profile
    #
    #     Returns:
    #         list[dict[str, list[dict[str, any]]]]: All the courses for the given profile
    #     """
    #     
    #     if profile_code is not None: 
    #         semesters = self.soup.find_all("div", {"data-specialization": {profile_code}})
    #     else:
    #         semesters = self.soup.select('div.specialization[data-specialization=""]')
    #     
    #     if profile_code is None:
    #         term_start = MASTER_TERM_START
    #         profile_start = 0
    #     else:
    #         term_start = 0
    #         profile_start = MASTER_TERM_START - 1
    #
    #     program_courses = []
    #     for index, semester in enumerate(semesters, 1):
    #         if index >= term_start:
    #             periods = semester.find_all("tbody", {"class": "period"})
    #             s_string = f"Termin {profile_start + index}"
    #             semester_courses = {s_string: []}
    #             
    #             for i, period in enumerate(periods, 1):
    #                 courses = period.find_all("tr", {"class": "main-row"})
    #                 semester_courses[s_string].append({f"Period {i}" : self.format_course_scrape(courses)})
    #             program_courses.append(semester_courses)
    #     
    #     return program_courses

    def courses(self):
        """return all courses sorte in a dict after profiles and program"""
        
        # extracting code and adding an empty string for easier scraping
        temp, profile_codes, program_code = zip(*self.profiles())
        profile_codes = [*profile_codes, ""]        
        courses = []
        profile_codes.remove("free")
        for semester_section in self.soup.find_all("section", {"class": "accordion semester js-semester show-focus is-toggled"}):
            semester = semester_section.find("h3").text[:8]
            semester = int(semester[-1:])
            # ignore semesters outside of master
            if semester not in [7, 8, 9, None]:
                continue
            # add all non profile specific courses
            for profile_code in profile_codes:
                if not semester_section.find("div", {"data-specialization": profile_code}):
                    continue

                for count, period_sections in enumerate(semester_section.find("div", {"data-specialization": profile_code}).find_all("tbody", {"class": "period"})):
                    # when searching for data specialization="" all specializations are found -_- 
                    if count > 1:
                        continue
                    period = None
                    for row in period_sections.find_all("tr"):
                        if row.find("th"):
                            period = row.find("th").text[-1:]
                            continue
                        if "main-row" in row["class"] and "inactive" not in row["class"]:
                            course = self.format_course_scrape(row)
                            if profile_code == "":
                                course["profile_code"] = "free"
                            else:
                                course["profile_code"] = profile_code
                            course["program_code"] = self.program_code
                            course["period"] = period
                            course["semester"] = semester
                            courses.append(course)
        return courses
                         



    # def course_helper(self, semester_section, profile=None):
    #     courses = []
    #     if profile == None:



    # def courses(self, profile_code: str = None) -> list[dict[str, any]]:
    #     """Get all courses of a program or profile in a list that is unordered.
    #     Does not specify any semester or peroid just the courses.
    #
    #     Args:
    #         profile_code (str, optional): _description_. Defaults to None.
    #
    #     Returns:
    #         list[dict[str, any]]: _description_
    #     """
    #     if profile_code is not None: 
    #         semesters = self.soup.find_all("div", {"data-specialization": {profile_code}})
    #     else:
    #         semesters = self.soup.select('div.specialization[data-specialization=""]')
    #     
    #     if profile_code is None:
    #         term_start = MASTER_TERM_START
    #     else:
    #         term_start = 0
    #         
    #     program_courses = []
    #     for index, semester in enumerate(semesters, 1):
    #         if index >= term_start:
    #             courses = semester.find_all("tr", {"class": "main-row"})
    #             program_courses.append(self.format_course_scrape(courses))
    #
    #         
    #     return sum(program_courses, [])

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
            list[tuple[str, str]]: A tuple containing the profile name and its 
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
        profiles = [*zip(profile_names[1:], 
                         profile_id[1:], 
                         [self.program_code]*len(profile_id))]
        
        profiles.append(("Ingen inriktning", "free", self.program_code))
        
        return profiles

    def program_n(self) -> str:
        headers = self.soup.find_all("header", {"class": ""})
        for header in headers:
            title = header.find("h1")
            return title.text.split(",")[0]


def main():
    plan = ProgramPlan("6CDDD")
    plan.courses()
    
if __name__ == "__main__":
    main()
