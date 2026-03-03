from app.models.schemas import SchemeStructuredData
from app.services.verifier import VerifierService


def test_verifier_nullifies_unverified_fields():
    verifier = VerifierService()
    data = SchemeStructuredData(
        scheme_name="Scholarship A",
        income_limit="Rs. 2,50,000",
        application_deadline="31-08-2026",
    )
    text = "Scholarship A is announced for students."
    verified, unverified = verifier.verify_against_source(data, text)

    assert verified.scheme_name == "Scholarship A"
    assert verified.income_limit is None
    assert verified.application_deadline is None
    assert "income_limit" in unverified

