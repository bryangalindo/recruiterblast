MOCK_COMPANY_API_RESPONSE = {
    "data": {},
    "included": [
        {
            "entityUrn": "urn:li:fsd_followingState:urn:li:fsd_company:69318116",
        },
        {
            "name": "Defense & Space",
            "entityUrn": "urn:li:fsd_industryV2:3187",
        },
        {
            "description": "Sphinx builds software",
            "*industryV2Taxonomy": ["urn:li:fsd_industryV2:3187"],
            "employeeCount": 19,
            "name": "Sphinx Defense",
        },
    ],
}
MOCK_COMPANY_ENTITY_API_RESPONSE = {
    "data": {
        "websiteUrl": "https://www.sphinxdefense.com",
    },
    "included": [],
}
MOCK_GOOGLE_SEARCH_API_RESPONSE = {
    "items": [
        {
            "snippet": "Reach out at foo@bar.com",
        }
    ]
}

MOCK_GOOGLE_SEARCH_API_LEADIQ_EMAIL_FORMAT_RESPONSE = {
    "items": [
        {
            "snippet": (
                "The FooBar's email format typically follows the pattern of First_Last@foobar.com; "
                "this email format is used 95% of the time. Other contacts within ..."
            ),
        }
    ]
}

MOCK_GOOGLE_SEARCH_API_ROCKETREACH_EMAIL_FORMAT_RESPONSE = {
    "items": [
        {
            "snippet": (
                "The most common ASRC Federal email format is [first].[last] (ex. jane.doe@foobar.com), "
                "which is being used by 89.8% of ASRC Federal work email addresses"
            ),
        }
    ]
}

MOCK_GOOGLE_GEMINI_API_RESPONSE = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {
                        "text": (
                            '{"core_responsibilities": ["foo"],"technical_requirements": ["bar"],'
                            '"soft_skills": ["baz"],"highlights": ["qux"]}'
                        )
                    }
                ],
            },
        }
    ]
}
