"""Explainable asset eligibility and ranking."""

from __future__ import annotations

from oi_discovery.models import AssetRecord, DatasetRecord, DiscoveryQuery, EligibilityDecision


def _contains_any(value: str | None, options: tuple[str, ...]) -> bool:
    if not options:
        return True
    normalized = (value or "").lower()
    return any(option.lower() in normalized for option in options)


def decide_asset(asset: AssetRecord, query: DiscoveryQuery) -> EligibilityDecision:
    reasons: list[str] = []
    rejected: list[str] = []
    score = 0.0

    if query.formats and not _contains_any(asset.format, query.formats):
        rejected.append(f"format_not_requested:{asset.format or 'unknown'}")
    else:
        reasons.append("format_matches")
        score += 1.0

    if query.modalities and not _contains_any(asset.modality, query.modalities):
        rejected.append(f"modality_not_requested:{asset.modality or 'unknown'}")
    elif query.modalities:
        reasons.append("modality_matches")
        score += 1.0

    if query.min_size_bytes is not None and (asset.size_bytes or 0) < query.min_size_bytes:
        rejected.append("below_min_size")
    elif query.min_size_bytes is not None:
        reasons.append("above_min_size")
        score += 0.5

    if query.max_size_bytes is not None and (asset.size_bytes or 0) > query.max_size_bytes:
        rejected.append("above_max_size")
    elif query.max_size_bytes is not None:
        reasons.append("below_max_size")
        score += 0.5

    if asset.source_url or asset.content_url:
        reasons.append("source_reference_available")
        score += 0.25
    else:
        rejected.append("missing_source_reference")

    return EligibilityDecision(
        asset_id=asset.asset_id,
        eligible=not rejected,
        score=score,
        reasons=tuple(reasons),
        rejected_reasons=tuple(rejected),
    )


def rank_assets(dataset: DatasetRecord, query: DiscoveryQuery) -> tuple[EligibilityDecision, ...]:
    decisions = [decide_asset(asset, query) for asset in dataset.assets]
    decisions.sort(key=lambda item: (item.eligible, item.score), reverse=True)
    if query.max_assets is not None:
        eligible = [item for item in decisions if item.eligible][: query.max_assets]
        ineligible = [item for item in decisions if not item.eligible]
        decisions = eligible + ineligible
    return tuple(decisions)
