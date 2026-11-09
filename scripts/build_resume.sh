#!/bin/bash
# Rebuild the downloadable resume from the canonical cv.md.
#
#   cv.md --sync_resume.py--> resume/resume.json --+--> Alberto_Nieto_Resume.docx
#                                                   +--> src/assets/Alberto_Nieto_Resume.pdf
#
# The PDF is rendered by a career-ops checkout with its ATS template. Run after
# every cv.md edit, then commit resume/resume.json and both files.
#
# Usage: scripts/build_resume.sh [CAREER_OPS_DIR]
#        (default /var/home/Alberto-Codes/Projects/career-ops; cv.md is read from it)

set -euo pipefail

SITE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CAREER_OPS="${1:-/var/home/Alberto-Codes/Projects/career-ops}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

cd "$SITE"
uv run python scripts/sync_resume.py --cv "$CAREER_OPS/cv.md"
uv run python scripts/generate_resume_docx.py

cd "$CAREER_OPS"
node ats-payload.mjs "$SITE/resume/resume.json" --summary > "$WORK/resume-ats.json"
TEMPLATE="$(node cv-templates.mjs resolve cv ats)"
# generate-pdf.mjs only reads and writes inside the career-ops workspace, so the
# HTML and PDF pass through its gitignored output/ directory.
HTML="output/site-resume-ats.html"
PDF="output/site-Alberto_Nieto_Resume.pdf"
node build-cv-html.mjs "$WORK/resume-ats.json" "$HTML" "$TEMPLATE"
node verify-cv-facts.mjs "$HTML"
# Without --report the render still appends an unkeyed row to data/pdf-index.tsv;
# put the index back so the site build leaves career-ops untouched.
INDEX="data/pdf-index.tsv"
[ -f "$INDEX" ] && cp "$INDEX" "$WORK/pdf-index.tsv"
node generate-pdf.mjs "$HTML" "$PDF" --format=letter
[ -f "$WORK/pdf-index.tsv" ] && cp "$WORK/pdf-index.tsv" "$INDEX"
node verify-ats.mjs "$HTML"
cp "$PDF" "$SITE/src/assets/Alberto_Nieto_Resume.pdf"
rm -f "$HTML" "$PDF"

echo "Resume rebuilt; commit resume/resume.json, Alberto_Nieto_Resume.docx and src/assets/Alberto_Nieto_Resume.pdf."
