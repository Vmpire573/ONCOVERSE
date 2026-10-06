# Data dictionary

The canonical CSV columns are listed below. The generator creates synthetic values only. Never include names, phone numbers, medical record numbers, addresses, or other direct identifiers.

| Field | Type | Accepted values / range | Meaning |
|---|---|---|---|
| `source_id` | string | non-empty, unique per source | Synthetic/source-local record key |
| `age` | integer | 18–110 | Age in years |
| `sex` | category | Female, Male, Other, Unknown; F/M variants mapped | Category supplied by dataset |
| `cancer_type` | string | non-empty | Broad display category; title-cased |
| `stage` | category | I, II, III, IV; 1–4 and `Stage ` prefixes mapped | Simplified stage label |
| `tumor_size_mm` | decimal | 0–500 | Tumor size in millimeters |
| `grade` | integer | 1–4 | Simplified grade value |
| `smoking_status` | category | Never, Former, Current, Unknown | Harmonized smoking category |
| `outcome_label` | category | Alive, Deceased | Synthetic binary label used only for the ML exercise |

The database adds a generated integer primary key, `source_name`, `created_at`, and optional `site_code` provenance fields. The ingestion-run table stores source name, row counts, JSON summary text, and run timestamp. `external_dataset_records` stores source-specific public metadata payloads and external IDs separately from the canonical cohort so unmapped fields are not misrepresented. The simplified schema does not encode diagnosis dates, censoring, treatment, multiple tumors, or clinical terminology codes.

| Database field | Type | Purpose |
|---|---|---|
| `source_name` | string | Origin label used for ingestion provenance |
| `site_code` | string, nullable | Optional contributing site value used for aggregate demonstration |
| `created_at` | timestamp | Local insertion time |
| `external_dataset_records.source_name` | string | External source identifier such as GDC |
| `external_dataset_records.external_id` | string | Source-specific record identifier |
| `external_dataset_records.payload_json` | JSON text | Original source-specific metadata, retained separately |

FHIR review outputs and external source payloads are not automatically converted into canonical cohort rows. Review their field mappings and data-use permissions before any approved research use.
