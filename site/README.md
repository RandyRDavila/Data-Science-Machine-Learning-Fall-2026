# Course site source

This directory contains the reviewed static source for the public course landing
page. The deployment workflow does not publish the repository root. Instead,
`scripts/build_course_site.py` creates a bounded artifact under
`build/course-site/`, substitutes version and revision metadata, copies the
compiled textbook and instructor CV, includes a course map connecting both
textbook parts to their lecture laboratories, and writes a cryptographic
deployment manifest for both PDFs.

Build locally with:

```bash
uv run python scripts/build_course_site.py \
  --revision local-preview \
  --textbook output/pdf/data-science-machine-learning-textbook.pdf \
  --cv output/pdf/randy-davila-cv.pdf
```

Serve the generated directory for local review:

```bash
uv run python -m http.server 8000 --directory build/course-site
```

The site contains no client-side JavaScript, tracking, forms, cookies, or
credentials. The public instructor profile intentionally omits the street
address and telephone number present in the supplied CV. Public issues remain
on GitHub; private security and student matters follow the repository security
and course communication policies.
