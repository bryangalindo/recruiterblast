JOB_DESCRIPTION_SKILLS_PARSE_PROMPT = (
    "Parse this job description for technology keywords. "
    "Return only a JSON dictionary string in the exact format shown below. "
    "No explanations, no extra text, no formatting (e.g., 'json\n...\n\n',), "
    ", no new line characters (e.g., '\n'), and no context beyond the JSON output. "
    "This is an example of what the output should be: "
    '"{"technologies": ["SQL", "Python", "Typescript", "Snowflake", "API", "dbt", "AWS", "GCP", "Snowflake",'
    '"QuickBase", "Google Analytics", "API", "data orchestration"]}"'
    "Another example:\n"
    "input:\n"
    "As part of our vision to create a smoother patient billing experience, we are in need of a Software Engineer "
    " candidate: Experience working on technical projects across the stack (we don’t have a hard requirement, "
    "but generally this comes with 2+ years of professional software development experience) "
    "Experience with at least one major coding language (we mostly use Python and Typescript, "
    "but knowing these is not a requirement) Excitement about our mission and a passion for solving problems to "
    "improve the healthcare financial experience Compensation Range and Benefits Salary/Hourly "
    "Rate Range*: $145,000 - $161,625\n"
    'output: "{"technologies": ["Python", "Typescript"]}"\n'
    "another example:\n"
    "intput:"
    "Piper Companies is seeking a Software Engineer to join an enterprise company located in Durham, NC. This role is a long term contract for a non profit firm."
    "Responsibilities of the Software Engineer"
    "Designing, developing, and maintaining applications using Python, Kubernetes and AWS"
    "Development experience (currently hands-on) in Python, Microservice development"
    "Hands-on experience with coding and test automation of front-end SPAs, web components, SSR architectures"
    "Advanced serverless AWS development experience"
    "Qualifications Of The Software Engineer"
    "6+ years of experience "
    "Preference coming from SWE and advanced Cloud native experience"
    "Bachelors Degree or Technical College Degree\n"
    'output: "{"technologies": ["Python", "Kubernetes", "AWS", "Microservice", "test automation"]}"'
    "given the constraints above and the examples, parse the technologies from this job description:\n"
)
