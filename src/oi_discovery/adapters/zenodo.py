"""Zenodo records search adapter for metadata-only discovery."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from oi_discovery.models import AssetRecord, DatasetRecord, DiscoveryQuery


class ZenodoAdapter:
    source_name = "zenodo"
    api_root = "https://zenodo.org/api/"

    def __init__(self, session: requests.Session | None = None, timeout: int = 60) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout

    def _get_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Zenodo response is not a JSON object")
        return payload

    @staticmethod
    def _record_asset(record: dict[str, Any]) -> AssetRecord:
        record_id = str(record.get("id") or record.get("doi") or "unknown")
        metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
        title = str(metadata.get("title") or record_id)
        links = record.get("links") if isinstance(record.get("links"), dict) else {}
        source_url = str(links.get("html") or links.get("self") or f"https://zenodo.org/records/{record_id}")
        license_value = metadata.get("license")
        if isinstance(license_value, dict):
            license_value = license_value.get("id") or license_value.get("name")
        files = record.get("files") if isinstance(record.get("files"), list) else []
        total_size = sum(int(item.get("size", 0)) for item in files if isinstance(item, dict) and item.get("size") is not None)
        return AssetRecord(
            source="zenodo",
            asset_id=record_id,
            path=title,
            size_bytes=total_size or None,
            format="record",
            modality=str((metadata.get("resource_type") or {}).get("type") or "dataset") if isinstance(metadata.get("resource_type"), dict) else "dataset",
            license=str(license_value) if license_value else None,
            source_url=source_url,
            content_url=source_url,
            checksum=None,
            modified_at=str(record.get("updated") or metadata.get("publication_date") or "") or None,
            raw_metadata=record,
        )

    def discover(self, query: DiscoveryQuery) -> DatasetRecord:
        if not query.dataset_id:
            raise ValueError("Zenodo discovery requires dataset_id as the search text")
        search_text = query.dataset_id
        payload = self._get_json(
            f"{self.api_root}records",
            {"q": search_text, "size": 25, "sort": "bestmatch"},
        )
        hits = payload.get("hits") if isinstance(payload.get("hits"), dict) else {}
        raw_results = hits.get("hits", [])
        if not isinstance(raw_results, list):
            raise ValueError("Zenodo response has no list-shaped hits")
        records = tuple(self._record_asset(item) for item in raw_results if isinstance(item, dict))
        source_url = f"https://zenodo.org/search?q={quote(search_text)}"
        return DatasetRecord(
            source="zenodo",
            dataset_id=f"search:{search_text}",
            version=query.version,
            name=f"Zenodo records search: {search_text}",
            status="live",
            description=f"Metadata-only search for {search_text}",
            source_url=source_url,
            asset_count=len(records),
            total_size_bytes=sum(asset.size_bytes or 0 for asset in records),
            assets=records,
            raw_metadata={"total": hits.get("total", 0), "search": search_text},
        )
