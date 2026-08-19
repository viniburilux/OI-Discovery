"""DANDI public API adapter for metadata-only discovery."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import requests

from oi_discovery.models import AssetRecord, DatasetRecord, DiscoveryQuery


class DandiAdapter:
    source_name = "dandi"
    api_root = "https://api.dandiarchive.org/api/"

    def __init__(self, session: requests.Session | None = None, timeout: int = 60) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout

    def _get_json(self, url: str) -> dict[str, Any]:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"Expected JSON object from {url}")
        return payload

    def _all_assets(self, dataset_id: str, version: str) -> list[dict[str, Any]]:
        url = urljoin(
            self.api_root,
            f"dandisets/{dataset_id}/versions/{version}/assets/?page_size=100",
        )
        assets: list[dict[str, Any]] = []
        while url:
            payload = self._get_json(url)
            page = payload.get("results", [])
            if not isinstance(page, list):
                raise ValueError("DANDI assets response has no list-shaped results")
            assets.extend(item for item in page if isinstance(item, dict))
            next_url = payload.get("next")
            url = str(next_url) if next_url else ""
        return assets

    @staticmethod
    def _format_from_path(path: str) -> str | None:
        if "." not in path:
            return None
        return path.rsplit(".", 1)[-1].lower()

    @staticmethod
    def _asset_record(raw: dict[str, Any], dataset_id: str, version: str) -> AssetRecord:
        path = str(raw.get("path", ""))
        asset_id = str(raw.get("identifier") or raw.get("id") or path)
        content_url = raw.get("contentUrl") or raw.get("content_url")
        source_url = raw.get("url") or urljoin(
            DandiAdapter.api_root,
            f"dandisets/{dataset_id}/versions/{version}/assets/{asset_id}/",
        )
        return AssetRecord(
            source="dandi",
            asset_id=asset_id,
            path=path,
            size_bytes=int(raw["size"]) if raw.get("size") is not None else None,
            format=DandiAdapter._format_from_path(path),
            modality=None,
            license=None,
            source_url=source_url,
            content_url=content_url,
            checksum=(raw.get("checksum") or {}).get("value") if isinstance(raw.get("checksum"), dict) else raw.get("checksum"),
            modified_at=raw.get("modified"),
            raw_metadata=raw,
        )

    def discover(self, query: DiscoveryQuery) -> DatasetRecord:
        if not query.dataset_id:
            raise ValueError("DANDI discovery requires query.dataset_id")
        dataset_url = urljoin(self.api_root, f"dandisets/{query.dataset_id}/")
        dataset_raw = self._get_json(dataset_url)
        raw_assets = self._all_assets(query.dataset_id, query.version)
        assets = tuple(self._asset_record(raw, query.dataset_id, query.version) for raw in raw_assets)
        total_size = sum(asset.size_bytes or 0 for asset in assets)
        name = str(dataset_raw.get("name") or dataset_raw.get("identifier") or query.dataset_id)
        description = dataset_raw.get("description") or dataset_raw.get("metadata", {}).get("description")
        license_value = dataset_raw.get("license") or dataset_raw.get("metadata", {}).get("license")
        return DatasetRecord(
            source="dandi",
            dataset_id=query.dataset_id,
            version=query.version,
            name=name,
            status=dataset_raw.get("status"),
            description=description,
            license=license_value,
            source_url=dataset_url,
            asset_count=len(assets),
            total_size_bytes=total_size,
            assets=assets,
            raw_metadata={"dataset": dataset_raw, "asset_count_from_api": len(assets)},
        )
