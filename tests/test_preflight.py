from decimal import Decimal

import pytest

from integration_evals.models import Mode, Provider
from integration_evals.preflight import provider_blocker


@pytest.mark.parametrize("mode", [Mode.SANDBOX, Mode.LIVE])
def test_provider_blocks_when_paid_authority_absent(mode: Mode) -> None:
    # Given credentials and a configured endpoint but no current paid authority.
    provider = Provider(
        id="jev",
        mode=mode,
        model="owner-selected",
        eligible=True,
        credential_env="FAKE_KEY",
        endpoint="https://provider.example",
        cap=Decimal(1),
        currency="USD",
        cleanup_supported=True,
        allowed_operations=("decide",),
    )
    # When preflighting a dispatch.
    blocker = provider_blocker(
        provider, ("decide",), {"FAKE_KEY": "fictional"}, authorize_paid=False
    )
    # Then credentials alone never grant spending authority.
    assert blocker is not None
    assert blocker.reason == "explicit current budget authority required"


def test_provider_blocks_when_credentials_missing() -> None:
    # Given owner approval and a permitted cap with absent credentials.
    provider = Provider(
        id="jev",
        mode=Mode.LIVE,
        model="owner-selected",
        eligible=True,
        credential_env="FAKE_KEY",
        endpoint="https://provider.example",
        authority_ref="owner-approved-reference",
        cap=Decimal(1),
        currency="USD",
        cleanup_supported=True,
        allowed_operations=("decide",),
    )
    # When preflighting an explicitly requested live operation.
    blocker = provider_blocker(provider, ("decide",), {}, authorize_paid=True)
    # Then missing credentials produce an explicit blocker.
    assert blocker is not None
    assert blocker.reason == "credential unavailable"


def test_provider_blocks_when_operation_exceeds_authority() -> None:
    # Given authority for decisions but no purchase authorization.
    provider = Provider(
        id="jev",
        mode=Mode.SANDBOX,
        model="owner-selected",
        eligible=True,
        credential_env="FAKE_KEY",
        endpoint="https://provider.example",
        authority_ref="owner-approved-reference",
        cap=Decimal(1),
        currency="USD",
        cleanup_supported=True,
        allowed_operations=("decide",),
    )
    # When attempting a purchase operation.
    blocker = provider_blocker(
        provider, ("purchase",), {"FAKE_KEY": "fictional"}, authorize_paid=True
    )
    # Then the unrelated operation is blocked.
    assert blocker is not None
    assert blocker.reason == "operation outside authorized allowlist"


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://",
        "https:///missing-host",
        "https://provider.example:invalid",
        "https://provider.example:65536",
        "https://[broken",
        "https://user:password@provider.example",
        "https://provider.example/#private-token",
        "https://provider.example/\nsecret",
    ],
)
def test_provider_blocks_malformed_or_sensitive_endpoint(endpoint: str) -> None:
    provider = Provider(
        id="jev",
        mode=Mode.LIVE,
        model="owner-selected",
        eligible=True,
        credential_env="FAKE_KEY",
        endpoint=endpoint,
        authority_ref="owner-approved-reference",
        cap=Decimal(1),
        currency="USD",
        cleanup_supported=True,
        allowed_operations=("decide",),
    )
    blocker = provider_blocker(
        provider, ("decide",), {"FAKE_KEY": "fictional"}, authorize_paid=True
    )
    assert blocker is not None
    assert blocker.reason == "owner-approved HTTPS endpoint required"
    assert endpoint not in blocker.reason


def test_provider_accepts_valid_https_endpoint_with_explicit_authority() -> None:
    provider = Provider(
        id="jev",
        mode=Mode.LIVE,
        model="owner-selected",
        eligible=True,
        credential_env="FAKE_KEY",
        endpoint="https://provider.example:8443/v1/decide?api-version=1",
        authority_ref="owner-approved-reference",
        cap=Decimal(1),
        currency="USD",
        cleanup_supported=True,
        allowed_operations=("decide",),
    )
    assert (
        provider_blocker(provider, ("decide",), {"FAKE_KEY": "fictional"}, authorize_paid=True)
        is None
    )
