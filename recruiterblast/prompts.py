LLM_JOB_DESCRIPTION_SUMMARY_PROMPT = """
    Summarize the following job posting in a structured format and return the results as a JSON string. Use the following categories:

    core_responsibilities: A concise list of the primary tasks and duties. Do not include generic/cliché phrases such as "Learn and adapt to new technologies," or "Contribute to the improvement of our software development processes."
    technical_requirements: Outline specific technologies, tools, or methodologies required (e.g., Python, REST APIs, Database Design, Unit Testing, etc.). Avoid including soft skills or qualifications that are not technical (e.g., fast-paced environment, degree requirements).
    soft_skills: Points detailing essential soft skills and personality traits.
    highlights: Unique aspects or benefits offered by the company.

    Ensure results return only a JSON dictionary string in the exact format shown below.
    No explanations, no extra text, no json formatting pre/post text (e.g., ```json\n or \n```),
    no new line characters (e.g., '\n'), and no context beyond the JSON output.

    {
      "core_responsibilities": [ ... ],
      "technical_requirements": [ ... ],
      "soft_skills": [ ... ],
      "highlights": [ ... ]
    }

    Here's the job post:
    """
