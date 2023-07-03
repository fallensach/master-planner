from scrappy.program_plan import ProgramPlan
from scrappy.courses import fetch_course_info

programs = ["6cmju", "6cyyy"]

plan = ProgramPlan("6cmju")
course = plan.planned_courses()[0]
print(course)
