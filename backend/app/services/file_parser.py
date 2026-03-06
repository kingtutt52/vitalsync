"""
Parses uploaded health files.

Bloodwork PDFs/images: we store the file and flag it for manual/OCR review in a
future release. MVP just confirms the upload succeeded.

Genetics (.txt 23andMe): we scan for known SNP rsIDs and return a lightweight
summary of found variants. We don't claim clinical accuracy — this is informational.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Optional

# A small representative set of wellness-relevant SNPs.
# Format: rsID -> {gene, trait, risk_allele, protective_allele, note}
KNOWN_SNPS: Dict[str, Dict] = {
    "rs9939609": {
        "gene": "FTO",
        "trait": "Obesity risk",
        "risk_allele": "A",
        "note": "A/A associated with higher BMI tendency",
    },
    "rs1801133": {
        "gene": "MTHFR",
        "trait": "Folate metabolism",
        "risk_allele": "T",
        "note": "C677T variant; T/T may impair folate conversion",
    },
    "rs4988235": {
        "gene": "MCM6/LCT",
        "trait": "Lactase persistence",
        "risk_allele": "G",
        "note": "G/G associated with lactose intolerance",
    },
    "rs1815739": {
        "gene": "ACTN3",
        "trait": "Power vs endurance muscle",
        "risk_allele": "T",
        "note": "R577X; T/T (XX) associated with endurance-type muscle fiber",
    },
    "rs662799": {
        "gene": "APOA5",
        "trait": "Triglyceride levels",
        "risk_allele": "G",
        "note": "G allele associated with elevated triglycerides",
    },
    "rs7903146": {
        "gene": "TCF7L2",
        "trait": "Type 2 diabetes risk",
        "risk_allele": "T",
        "note": "T/T increases T2D risk; lifestyle modifications are effective",
    },
    "rs1800795": {
        "gene": "IL6",
        "trait": "Inflammation",
        "risk_allele": "G",
        "note": "G allele associated with higher IL-6 / inflammatory baseline",
    },
}


def parse_genetics_file(file_path: str) -> Optional[str]:
    """
    Read a 23andMe-format text file and extract known SNP variants.
    Returns a JSON string of found variants, or None if the file can't be parsed.

    23andMe format lines look like:
      rsid  chromosome  position  genotype
      rs9939609  16  53786615  AT
    Lines starting with # are comments.
    """
    path = Path(file_path)
    if not path.exists():
        return None

    found_variants: List[Dict] = []

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = re.split(r"\s+", line)
                if len(parts) < 4:
                    continue

                rsid, _chrom, _pos, genotype = parts[0], parts[1], parts[2], parts[3]

                if rsid in KNOWN_SNPS:
                    meta = KNOWN_SNPS[rsid]
                    found_variants.append(
                        {
                            "rsid": rsid,
                            "gene": meta["gene"],
                            "trait": meta["trait"],
                            "genotype": genotype,
                            "note": meta["note"],
                        }
                    )

    except Exception:
        # Malformed file — return whatever we found so far
        pass

    if not found_variants:
        return json.dumps(
            {"status": "parsed", "variants_found": 0, "note": "No known SNPs detected in file"}
        )

    return json.dumps(
        {"status": "parsed", "variants_found": len(found_variants), "variants": found_variants}
    )
