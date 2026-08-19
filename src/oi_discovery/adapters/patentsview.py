"""Metadata-only adapter for the current PatentsView Search API."""

from __future__ import annotations

import json
import os
from typing import Any

import requests

from oi_discovery.models import AssetRecord, DatasetRecord, DiscoveryQuery


class PatentAdapter:
    """Search PatentsView without downloading patent documents or claims."""

    source_name = "patentsview"
    DEFAULT_BASE_URL = "https://search.patentsview.org/api/v1"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.getenv("PATENTSVIEW_API_KEY")
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout_seconds = timeout_seconds

    def discover(self, query: DiscoveryQuery) -> DatasetRecord:
        """Run a small title search and return normalized metadata only."""
        if not self.api_key:
            raise RuntimeError(
                "PATENTSVIEW_API_KEY is required for live PatentAdapter calls; "
                "use normalize_response() for offline fixtures."
            )
        search_text = query.dataset_id or ""
        if not search_text:
            raise ValueError("DiscoveryQuery.dataset_id must contain the patent search text")

        endpoint = f"{self.base_url}/patent/"
        fields = [
            "patent_id",
            "patent_title",
            "patent_date",
            "patent_type",
            "patent_kind",
            "patent_num_claims",
            "inventors",
            "assignees",
            "applicants",
            "cpc_current",
            "ipcs",
            "wipo",
            "family_id",
            "simple_family_id",
            "priority_date",
        ]
        params = {
            "q": json.dumps({"_text_phrase": {"patent_title": search_text}}),
            "f": json.dumps(fields),
            "o": json.dumps({"size": query.max_assets or 10}),
        }
        response = requests.get(
            endpoint,
            params=params,
            headers={"X-Api-Key": self.api_key, "Accept": "application/json"},
            timeout=self.timeout_seconds,
        )
        if response.status_code in {401, 403}:
            raise RuntimeError("patentsview_auth_required: API key rejected or missing permission")
        if response.status_code == 429:
            raise RuntimeError("patentsview_rate_limited: retry later")
        response.raise_for_status()
        return self.normalize_response(query, response.json(), endpoint=endpoint)

    def normalize_response(
        self,
        query: DiscoveryQuery,
        payload: dict[str, Any],
        *,
        endpoint: str | None = None,
    ) -> DatasetRecord:
        """Normalize an API response or fixture without touching document content."""
        records = payload.get("patents")
        if records is None and isinstance(payload.get("data"), dict):
            records = payload["data"].get("patents")
        if records is None:
            records = []
        if not isinstance(records, list):
            raise ValueError("PatentsView response did not contain a patents list")

        assets: list[AssetRecord] = []
        for record in records:
            if not isinstance(record, dict):
                continue
            patent_id = str(record.get("patent_id") or record.get("publication_number") or "")
            if not patent_id:
                continue
            title = str(record.get("patent_title") or "").strip()
            official_url = f"{self.base_url}/patent/{patent_id}/"
            assets.append(
                AssetRecord(
                    source=self.source_name,
                    asset_id=f"patent:{patent_id}",
                    path=title or patent_id,
                    size_bytes=None,
                    format="patent_metadata",
                    modality="patent",
                    license=None,
                    source_url=official_url,
                    content_url=None,
                    checksum=None,
                    modified_at=str(record.get("patent_date") or "") or None,
                    raw_metadata={
                        "patent_id": patent_id,
                        "patent_title": title,
                        "patent_date": record.get("patent_date"),
                        "patent_type": record.get("patent_type"),
                        "patent_kind": record.get("patent_kind"),
                        "patent_num_claims": record.get("patent_num_claims"),
                        "inventors": record.get("inventors"),
                        "assignees": record.get("assignees"),
                        "applicants": record.get("applicants"),
                        "cpc_current": record.get("cpc_current"),
                        "ipcs": record.get("ipcs"),
                        "wipo": record.get("wipo"),
                        "family_id": record.get("family_id"),
                        "simple_family_id": record.get("simple_family_id"),
                        "priority_date": record.get("priority_date"),
                    },
                )
            )

        dataset_id = f"search:{query.dataset_id or 'patentsview'}"
        return DatasetRecord(
            source=self.source_name,
            dataset_id=dataset_id,
            version=query.version,
            name=f"PatentsView search: {query.dataset_id or 'patents'}",
            status="metadata_only",
            description="Patent metadata search; no document or claim body downloaded.",
            license=None,
            source_url=endpoint or self.base_url,
            asset_count=len(assets),
            total_size_bytes=None,
            assets=tuple(assets),
            raw_metadata={
                "query_text": query.dataset_id,
                "endpoint": endpoint or self.base_url,
                "returned_count": len(assets),
                "total_hits": payload.get("query_results", {}).get("total_hits")
                if isinstance(payload.get("query_results"), dict)
                else None,
                "source_response_keys": sorted(payload.keys()),
            },
        )
