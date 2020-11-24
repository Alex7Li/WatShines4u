"""
Wrapper for IBM Watson service.
"""

import os
from typing import List, Tuple

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import DiscoveryV1

apikey = os.getenv("DISCOVERY_API_KEY")
environment_id = "26e276ef-e35e-4076-a190-bab90b5a4521"
collection_id = "d954d9f6-d52c-40af-b8d0-148fbdceb49e"
service_url = "https://api.us-south.discovery.watson.cloud.ibm.com/instances/230365e2-48ca-4b2f-8a9e-3dba5fbe20ed"
version = "2019-04-30"

authenticator = IAMAuthenticator(apikey)
discovery = DiscoveryV1(version=version, authenticator=authenticator)
discovery.set_service_url(service_url)


def get_reviews(query: str) -> List[Tuple[str, str, List[str], List[str]]]:
    """
    Get reviews for dates given a query from Watson.

    Returns a list of (review text, name, [keywords], [categories])
    """
    reqd_fields = "name, text, enriched_text"
    count = 10
    reviews = []
    error = None

    try:
        response = discovery.query(
            environment_id,
            collection_id,
            natural_language_query=query,
            count=count,
            return_=reqd_fields,
            x_watson_logging_opt_out=True,
        )
        results = response.get_result()

        def clean_categories(raw_category: str) -> str:
            if "/" in raw_category:
                return raw_category.split("/")[-2]

            return raw_category

        for result in results["results"]:
            categories = []
            for category in result["enriched_text"]["categories"]:
                categories.append((category["score"], category["label"]))

            # cleans categories
            categories = [
                clean_categories(cats) for _, cats in sorted(categories, reverse=True)
            ]

            # remove categories in dating
            categories = [cat for cat in categories if cat.lower() not in ["dating"]]

            keywords = []
            for keyword in result["enriched_text"]["keywords"]:
                keywords.append((keyword["relevance"], keyword["text"]))
            keywords = [words for _, words in sorted(keywords, reverse=True)]

            review = (result["text"], result["name"], keywords, categories)
            reviews.append(review)
    except Exception as e:
        error = e
    return reviews, error
