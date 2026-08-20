# Security and data boundaries

TraceFoundry is a public metadata discovery core. It is not a data-ingestion service and it is not authorized to access private accounts or private datasets by default.

## Credentials

Never commit API keys, tokens, cookies, private URLs or credentials. Use environment variables locally. PatentsView live queries require `PATENTSVIEW_API_KEY`; the adapter must report a missing credential as an explicit condition.

## Scientific data

The public core does not download scientific datasets, execute notebooks or deserialize pickle, NWB or HDF5. If a contribution needs controlled acquisition or analysis, it belongs in a private research repository with a separate safety review.

## Reporting a vulnerability

For a security issue involving credentials, private data exposure or unsafe deserialization, do not open a public issue with sensitive details. Contact the repository owner through GitHub privately and include the affected path, reproduction conditions and the minimum safe disclosure needed to investigate.

## Epistemic safety

A provenance failure, source outage, rate limit or missing credential must not be represented as scientific absence. A metadata candidate must not be presented as proof of biological, technical, legal or commercial suitability.
