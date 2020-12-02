"""
Wrapper for IBM Watson service.
"""

import json
import os
import random
import string
from typing import Any, Dict, List

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


Person = Dict[str, Any]


def get_matches(query: str) -> List[Person]:
    """
    Get reviews for dates given a query from Watson.

    Returns a list of (review text, name, [keywords], [categories])
    """
    reqd_fields = "name, text, enriched_text"
    count = 10
    reviews = []

    response = discovery.query(
        environment_id,
        collection_id,
        natural_language_query=query,
        count=count,
        return_=reqd_fields,
        x_watson_logging_opt_out=True,
    )
    results = response.get_result()

    def clean(raw_category: str) -> str:
        if "/" in raw_category:
            return raw_category.split("/")[-2]

        return raw_category

    for result in results["results"]:
        raw_categories = []
        for category in result["enriched_text"]["categories"]:
            raw_categories.append((category["score"], category["label"]))

        # cleans categories
        clean_categories = [
            clean(cats) for _, cats in sorted(raw_categories, reverse=True)
        ]

        # remove categories in dating
        filtered_categories = [
            cat for cat in clean_categories if cat.lower() not in ["dating", "society"]
        ]

        keywords = []
        for keyword in result["enriched_text"]["keywords"]:
            keywords.append((keyword["relevance"], keyword["text"]))
        keywords = [words for _, words in sorted(keywords, reverse=True)]

        review = {
            "review": result["text"],
            "name": result["name"],
            "keywords": keywords,
            "categories": filtered_categories,
        }
        reviews.append(review)

    return reviews


def add_document(doc: Dict[str, Any]) -> None:
    tmp_name = f"tmp-{''.join(random.sample(string.ascii_letters,10))}.json"

    with open(tmp_name, "w+") as fp:
        json.dump(doc, fp)
        fp.seek(0)
        added = discovery.add_document(
            environment_id, collection_id, file=fp
        ).get_result()
        assert added is not None
        assert not isinstance(added, Exception)

        os.remove(tmp_name)


def add_date_review(review: str, person_reviewed: Person) -> None:
    """
    Given a review and a person being reviewed, this function adds the review to the database.
    Example:
        add_review("He beat me up on my date", {name:"Rude man"})
    """

    person_reviewed["text"] = review
    assert set(person_reviewed.keys()) == set(
        ["name", "text"]
    ), "only 'name' is allowed in person."
    add_document(person_reviewed)
