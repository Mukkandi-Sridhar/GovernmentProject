import asyncio

from app.config import Settings
from app.services.intent_classifier import IntentClassifierService


async def _classify(query: str) -> str:
    service = IntentClassifierService(Settings(openai_api_key=None))
    result = await service.classify(query)
    return result.intent


def test_greeting_intent_detected():
    assert asyncio.run(_classify("hello")) == "greeting"


def test_collect_intent_detected():
    assert asyncio.run(_classify("please collect latest data")) == "collect_latest"


def test_scheme_intent_detected():
    assert asyncio.run(_classify("what is scholarship eligibility")) == "scheme_qa"


def test_out_of_scope_detected():
    assert asyncio.run(_classify("how to debug python api")) == "out_of_scope"


def test_intent_classification_is_stable():
    query = "please collect latest data for student welfare schemes"
    first = asyncio.run(_classify(query))
    second = asyncio.run(_classify(query))
    third = asyncio.run(_classify(query))
    assert first == second == third == "collect_latest"
