LLM_JOB_DESCRIPTION_SKILLS_PARSER_PROMPT = """
    Parse this job description to extract keywords related to technologies, tools, frameworks, and methodologies used in software development, data engineering, and analytics engineering. Return only a JSON dictionary string in the exact format shown below. No explanations, no extra text, no formatting (e.g., 'json\n...\n\n'), no new line characters (e.g., '\n'), and no context beyond the JSON output.

    Categories to be parsed:
    - technologies (programming languages, cloud platforms)
    - tools (software development environments, analytics tools)
    - frameworks (software and web development frameworks)
    - methodologies (development practices or paradigms)

    Example 1:
    Input:
    We are looking for a Software Engineer skilled in backend and frontend development, with experience in Python, Django, AWS, and microservice architecture. Familiarity with agile development and unit testing is required.
    Output:
    {
      "technologies": ["Python", "AWS"],
      "tools": [],
      "frameworks": ["Django"],
      "methodologies": ["microservice architecture", "agile development", "unit testing"]
    }

    Example 2:
    Input:
    Seeking a data engineer with proficiency in SQL, dbt, Snowflake, and experience with data pipeline design. Candidates should know CI/CD pipelines and cloud computing with GCP.
    Output:
    {
      "technologies": ["SQL", "GCP"],
      "tools": [],
      "frameworks": ["dbt", "Snowflake"],
      "methodologies": ["data pipeline design", "CI/CD pipelines"]
    }

    Example 3:
    Input:
    Seeking full-stack engineer with demonstrated design and UX sensibilities, knowledge of API, and able to build UI components, and knows Python, SQL and dbt.
    Output:
    {
      "technologies": ["Python", "SQL"],
      "tools": [],
      "frameworks": ["dbt"],
      "methodologies": ["API", "UI", "UX", "full-stack"]
    }

    Now parse the technologies, tools, frameworks, and methodologies from this job description:
    """
