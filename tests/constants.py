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
MOCK_BING_SEARCH_API_RESPONSE = {
    "webPages": {
        "value": [
            {
                "snippet": "Reach out at foo@bar.com",
            }
        ]
    }
}
MOCK_GOOGLE_SEARCH_API_RESPONSE = {
    "items": [
        {
            "snippet": "Reach out at foo@bar.com",
        }
    ]
}
