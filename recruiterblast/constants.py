LINKEDIN_COMPANY_ENTITY_API_URL = (
    "https://www.linkedin.com/voyager/api/entities/companies/{company_id}"
)
LINKEDIN_COMPANY_API_URL = (
    "https://www.linkedin.com/voyager/api/graphql?variables=("
    "cardSectionTypes:List(COMPANY_CARD),"
    "jobPostingUrn:urn%3Ali%3Afsd_jobPosting%3A{job_id},"
    "includeSecondaryActionsV2:true)"
    "&queryId=voyagerJobsDashJobPostingDetailSections.0a2eefbfd33e3ff566b3fbe31312c8ed"
)
LINKEDIN_EMPLOYEE_API_URL = (
    "https://www.linkedin.com/voyager/api/graphql?variables=("
    "start:0,"
    "origin:FACETED_SEARCH,"
    "query:(keywords:{keyword},"
    "flagshipSearchIntent:ORGANIZATIONS_PEOPLE_ALUMNI,"
    "queryParameters:List("
    "(key:currentCompany,value:List({company_id})),"
    "(key:resultType,value:List(ORGANIZATION_ALUMNI))"
    "),"
    "includeFiltersInResponse:true),"
    "count:49"
    ")&queryId=voyagerSearchDashClusters.ff737c692102a8ce842be8f129f834ae"
)
LINKEDIN_API_HEADERS = {
    "authority": "www.linkedin.com",
    "accept": "application/vnd.linkedin.normalized+json+2.1",
    "accept-language": "en",
    "cache-control": "no-cache",
    "dnt": "1",
    "pragma": "no-cache",
    "referer": "https://www.linkedin.com/jobs/search/?currentJobId=3794646657&f_C=9783&start=75",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "x-li-lang": "en_US",
    "x-li-page-instance": "urn:li:page:d_flagship3_search_srp_jobs;rdRV1GfMQzODJa4C2BGm6w==",
    "x-li-pem-metadata": "Voyager - Organization - LCP_Member=job-about-company-card",
    "x-li-track": '{"clientVersion":"1.13.13931","mpVersion":"1.13.13931","osName":"web","timezoneOffset":-5,"timezone":"America/Chicago","deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":1,"displayWidth":2560,"displayHeight":1440}',
    "x-restli-protocol-version": "2.0.0",
}
