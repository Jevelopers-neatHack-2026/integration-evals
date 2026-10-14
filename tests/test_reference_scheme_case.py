import pytest

from integration_evals.artifacts import public_reference, reject_leaks
from integration_evals.errors import InvalidArtifactError
from tests.leak_matrix import carriers

SCHEMES = ["http", "HTTP", "HtTp", "https", "HTTPS", "hTtPs"]
CARRIERS = ["value", "key", "list", "embedded-object", "embedded-key", "embedded-scalar"]


@pytest.mark.parametrize("scheme", SCHEMES)
def test_scanner_reports_malformed_url_for_every_scheme_case(scheme: str) -> None:
    reference = f"{scheme}://[::1/fixture"
    with pytest.raises(InvalidArtifactError) as caught:
        reject_leaks(reference.encode(), "fixture")
    assert caught.value.code == "invalid_export_reference"
    assert str(caught.value) == "invalid_export_reference: fixture"


@pytest.mark.parametrize("scheme", SCHEMES)
def test_public_reference_normalizes_malformed_url_errors(scheme: str) -> None:
    reference = f"{scheme}://[::1/fixture"
    with pytest.raises(InvalidArtifactError) as caught:
        public_reference(reference)
    assert caught.value.code == "invalid_export_reference"
    assert str(caught.value) == "invalid_export_reference: reference"


@pytest.mark.parametrize("scheme", SCHEMES)
@pytest.mark.parametrize("carrier", CARRIERS)
def test_decoded_reference_syntax_uses_the_same_scheme_policy(scheme: str, carrier: str) -> None:
    payload = carriers(f"{scheme}://[::1/fixture")[carrier]
    with pytest.raises(InvalidArtifactError) as caught:
        reject_leaks(payload, "fixture")
    assert caught.value.code == "invalid_export_reference"
    assert str(caught.value) == "invalid_export_reference: fixture"


@pytest.mark.parametrize("scheme", SCHEMES)
def test_valid_reference_remains_accepted_for_every_scheme_case(scheme: str) -> None:
    reference = f"{scheme}://assets.example/report?page=2"
    reject_leaks(reference.encode(), "fixture")
    public_reference(reference)
    for payload in carriers(reference).values():
        reject_leaks(payload, "fixture")
