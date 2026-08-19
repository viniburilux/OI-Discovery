"""OpenAlex works search adapter for metadata-only discovery."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote, urljoin

import requests

from oi_discovery.models import AssetRecord, DatasetRecord, DiscoveryQuery


class OpenAlexAdapter:
    source_name = "openalex"
    api_root = "https://api.openalex.org/"

    def __init__(self, session: requests.Session | None = None, timeout: int = 60) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout

    def _get_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("OpenAlex response is not a JSON object")
        return payload

    @staticmethod
    def _landing_url(raw: dict[str, Any]) -> str | None:
        location = raw.get("primary_location") or {}
        if isinstance(location, dict):
            for key in ("landing_page_url", "pdf_url"):
                value = location.get(key)
                if value:
                    return str(value)
        for key in ("doi", "id"):
            value = raw.get(key)
            if value:
                return str(value)
        return None

    @staticmethod
    def _record(raw: dict[str, Any]) -> AssetRecord:
        work_id = str(raw.get("id") or raw.get("doi") or raw.get("title") or "unknown")
        title = str(raw.get("title") or work_id)
        source_url = OpenAlexAdapter._landing_url(raw)
        return AssetRecord(
            source="openalex",
            asset_id=work_id,
            path=title,
            size_bytes=None,
            format="paper",
            modality=str(raw.get("type") or "work"),
            license=None,
            source_url=source_url,
            content_url=source_url,
            checksum=None,
            modified_at=str(raw.get("publication_date") or raw.get("publication_year") or "") or None,
            raw_metadata=raw,
        )

    def discover(self, query: DiscoveryQuery) -> DatasetRecord:
        if not query.dataset_id:
            raise ValueError("OpenAlex discovery requires dataset_id as the search text")
        search_text = query.dataset_id
        payload = self._get_json(
            urljoin(self.api_root, "works"),
            {"search": search_text, "per-page": 25},
        )
        raw_results = payload.get("results", [])
        if not isinstance(raw_results, list):
            raise ValueError("OpenAlex response has no list-shaped results")
        records = tuple(self._record(item) for item in raw_results if isinstance(item, dict))
        source_url = f"{urljoin(self.api_root, 'works')}?search={quote(search_text)}"
        return DatasetRecord(
            source="openalex",
            dataset_id=f"search:{search_text}",
            version=query.version,
            name=f"OpenAlex works search: {search_text}",
            status="live",
            description=f"Metadata-only search for {search_text}",
            source_url=source_url,
            asset_count=len(records),
            total_size_bytes=None,
            assets=records,
            raw_metadata={"meta": payload.get("meta", {}), "search": search_text},
        )
