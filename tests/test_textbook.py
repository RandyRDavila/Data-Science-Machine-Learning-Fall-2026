"""Contract tests for the course textbook source and compiled artifact."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[1]
TEXTBOOK_ROOT = PROJECT_ROOT / "textbook"
MAIN_SOURCE = TEXTBOOK_ROOT / "textbook.tex"
CHAPTER_ROOT = TEXTBOOK_ROOT / "chapters"
OUTPUT_PDF = (
    PROJECT_ROOT / "output" / "pdf" / "data-science-machine-learning-textbook.pdf"
)

PART_I_CHAPTERS = [
    CHAPTER_ROOT / "01-computational-workshop.tex",
    CHAPTER_ROOT / "02-python-data-model.tex",
    CHAPTER_ROOT / "03-functions-classes-native-data.tex",
    CHAPTER_ROOT / "04-projects-packages-testing.tex",
    CHAPTER_ROOT / "05-arrays-tables-visual-evidence.tex",
    CHAPTER_ROOT / "06-databases-data-systems.tex",
    CHAPTER_ROOT / "07-llm-tools-agents.tex",
    CHAPTER_ROOT / "08-end-to-end-data-products.tex",
]

PART_II_CHAPTERS = [
    CHAPTER_ROOT / "09-supervised-learning-systems.tex",
    CHAPTER_ROOT / "10-linear-regression.tex",
    CHAPTER_ROOT / "11-classification-decisions.tex",
    CHAPTER_ROOT / "12-geometric-learning.tex",
    CHAPTER_ROOT / "13-decision-trees.tex",
    CHAPTER_ROOT / "14-ensemble-learning.tex",
    CHAPTER_ROOT / "15-model-selection.tex",
    CHAPTER_ROOT / "16-neural-networks.tex",
    CHAPTER_ROOT / "17-reliable-supervised-systems.tex",
]

CONTENT_CHAPTERS = PART_I_CHAPTERS + PART_II_CHAPTERS


def test_main_source_includes_both_parts_in_order() -> None:
    """The book should include every content chapter in numerical order."""

    source = MAIN_SOURCE.read_text()
    chapter_inputs = [
        f"\\input{{chapters/{chapter.stem}}}" for chapter in CONTENT_CHAPTERS
    ]
    positions = [source.index(chapter_input) for chapter_input in chapter_inputs]

    assert positions == sorted(positions)
    assert source.index(r"\part{Foundations for Data-Driven Software Systems}") < (
        positions[0]
    )
    assert source.index(r"\part{Supervised Learning Systems}") < positions[8]


def test_textbook_companions_follow_the_lecture_unit_sequence() -> None:
    """Each chapter should direct students to the current executable unit."""

    expected_links = {
        "01-computational-workshop.tex": ("Lecture 1 notebook 00",),
        "02-python-data-model.tex": ("Lecture 1 notebooks 01 through 05",),
        "03-functions-classes-native-data.tex": ("Lecture 2 develops",),
        "04-projects-packages-testing.tex": ("Lecture 3 notebooks 00 through 02",),
        "05-arrays-tables-visual-evidence.tex": (
            "Lecture 4 notebook 00",
            "Lecture 5 notebook 00",
        ),
        "06-databases-data-systems.tex": ("Lecture 6 notebook 00",),
        "07-llm-tools-agents.tex": ("Lecture 7 notebook 00",),
        "08-end-to-end-data-products.tex": ("Lecture 8 notebook 00",),
        "09-supervised-learning-systems.tex": ("Lecture 9 notebook 00",),
        "10-linear-regression.tex": ("Lecture 10 notebook 00",),
        "11-classification-decisions.tex": ("Lecture 11 notebook 00",),
        "12-geometric-learning.tex": ("Lecture 12 notebook 00",),
        "13-decision-trees.tex": ("Lecture 13 notebook 00",),
        "14-ensemble-learning.tex": ("Lecture 14 notebook 00",),
        "15-model-selection.tex": ("Lecture 15 notebook 00",),
        "16-neural-networks.tex": ("Lecture 16 notebook 00",),
        "17-reliable-supervised-systems.tex": ("Lecture 17 notebook 00",),
    }

    for filename, required_links in expected_links.items():
        source = (CHAPTER_ROOT / filename).read_text()
        for required_link in required_links:
            assert required_link in source


@pytest.mark.parametrize("chapter", CONTENT_CHAPTERS, ids=lambda path: path.stem)
def test_each_content_chapter_has_textbook_teaching_elements(chapter: Path) -> None:
    """A chapter should teach through explanation, practice, and reflection."""

    source = chapter.read_text()

    for required_element in (
        r"\begin{learningobjectives}",
        r"\begin{chapterconnection}",
        r"\begin{workedexample}",
        r"\begin{misconceptionbox}",
        r"\conceptcheck",
        r"\section{Exercises}",
        r"\begin{chapterreview}",
        r"\begin{notebooklink}",
    ):
        assert required_element in source, (
            f"{chapter.name} is missing teaching element: {required_element}"
        )

    assert source.index(r"\begin{chapterreview}") < source.index(
        r"\begin{notebooklink}"
    ), f"{chapter.name} should review the chapter before sending readers onward"


def test_overview_explains_how_to_use_the_book() -> None:
    overview = (CHAPTER_ROOT / "00-part-i-overview.tex").read_text()

    assert r"\section{How to read and use this book}" in overview
    assert r"\section{A running case study}" in overview
    assert r"\begin{chapterreview}" in overview


def test_git_appendix_teaches_version_control_as_professional_practice() -> None:
    """The Git appendix should provide complete mental models and worked lessons."""

    appendix_path = TEXTBOOK_ROOT / "appendices" / "git-github.tex"
    appendix = appendix_path.read_text()

    assert r"\input{appendices/git-github}" in MAIN_SOURCE.read_text()
    for required_idea in (
        "Why version control matters in data science",
        "Git and GitHub are different systems",
        "The four-state mental model",
        "Commits, branches, and HEAD",
        "First-time setup",
        "Worked lesson 1: build a local history",
        "Design coherent commits",
        "Ignore local and generated state deliberately",
        "Worked lesson 2: branches isolate change",
        "The daily branch and pull-request workflow",
        "Review is a technical skill",
        "Synchronize without guessing",
        "Worked lesson 3: create and resolve a conflict",
        "Recover conservatively",
        "Notebooks, data, and generated artifacts",
        "GitHub Actions turns history into automated evidence",
        "A command map by intention",
        "Principles to carry into professional work",
        "Official references",
        r"git diff --staged",
        r"git pull --ff-only",
        r"git merge --abort",
        r"git revert COMMIT",
        r"\begin{learningobjectives}",
        r"\begin{workedexample}",
        r"\begin{chapterreview}",
        r"\conceptcheck",
    ):
        assert required_idea in appendix

    assert len(appendix) >= 35_000


def test_opening_section_defines_the_books_systems_thesis_concisely() -> None:
    """The opening should establish the systems thesis without repetition."""

    overview = (CHAPTER_ROOT / "00-part-i-overview.tex").read_text()
    opening = overview.split(r"\section{The chapter map}", maxsplit=1)[0]

    for required_idea in (
        "Data-driven software system",
        "Three views of the same work",
        "The evidence loop",
        "Why learned components require additional controls",
        "Engineering boundary",
        "Data product",
        r"\begin{workedexample}",
        r"\begin{misconceptionbox}",
        r"\conceptcheck",
    ):
        assert required_idea in opening

    assert 7_000 <= len(opening) <= 13_000


def test_chapter_map_is_a_compact_capability_roadmap() -> None:
    """The roadmap should identify dependencies, results, and evidence."""

    overview = (CHAPTER_ROOT / "00-part-i-overview.tex").read_text()
    roadmap = overview.split(r"\section{The chapter map}", maxsplit=1)[1].split(
        r"\section{Correctness has layers}", maxsplit=1
    )[0]

    for required_idea in (
        "Chapter-by-chapter capabilities",
        "Milestones",
        "Computing environment",
        "Native objects",
        "Operated product",
        r"\conceptcheck",
    ):
        assert required_idea in roadmap

    assert 3_500 <= len(roadmap) <= 8_000


def test_correctness_section_connects_claims_to_scoped_evidence() -> None:
    """Correctness should distinguish claims, evidence, and evidence limits."""

    overview = (CHAPTER_ROOT / "00-part-i-overview.tex").read_text()
    correctness = overview.split(
        r"\section{Correctness has layers}", maxsplit=1
    )[1].split(r"\section{A professional-practice spine}", maxsplit=1)[0]

    for required_idea in (
        "Correctness claim",
        "Verification, validation, and reproducibility",
        "Six lenses for evaluating a result",
        "Composition and numerical judgment",
        "High accuracy, invalid scientific evidence",
        "Failure investigation",
        r"\begin{workedexample}",
        r"\conceptcheck",
    ):
        assert required_idea in correctness

    assert 5_000 <= len(correctness) <= 10_000


def test_professional_practice_section_is_an_operating_discipline() -> None:
    """Professional practice should remain operational and compact."""

    overview = (CHAPTER_ROOT / "00-part-i-overview.tex").read_text()
    practice = overview.split(
        r"\section{A professional-practice spine}", maxsplit=1
    )[1].split(r"\section{How to read and use this book}", maxsplit=1)[0]

    for required_idea in (
        "Professional practice",
        "Name the boundary",
        "Preserve provenance",
        "Make contracts executable",
        "Fail recoverably",
        "Version behavior",
        "Bound resources and authority",
        "Observe outcomes",
        "Design for review",
        "Scale rigor with consequence",
        r"\begin{misconceptionbox}",
        r"\conceptcheck",
    ):
        assert required_idea in practice

    assert 5_000 <= len(practice) <= 10_000


def test_how_to_use_the_book_teaches_active_computational_learning() -> None:
    """The study method should be rigorous without becoming an orientation essay."""

    overview = (CHAPTER_ROOT / "00-part-i-overview.tex").read_text()
    study = overview.split(
        r"\section{How to read and use this book}", maxsplit=1
    )[1].split(r"\section{A running case study}", maxsplit=1)[0]

    for required_idea in (
        "Active computational reading",
        "The predict-execute-explain loop",
        "Read code as a contract",
        "Interrogating a probability function",
        "Use notebooks as laboratories",
        "Notebook state",
        "experimental laboratory, not an operational boundary",
        "must not be the only source of truth",
        "Move reusable work into durable artifacts",
        "broader graduation rule",
        r"\begin{workedexample}",
        r"\conceptcheck",
    ):
        assert required_idea in study

    assert 3_000 <= len(study) <= 8_000


def test_end_to_end_chapter_keeps_the_notebook_as_a_laboratory() -> None:
    """A vertical-slice notebook must not be presented as production itself."""

    chapter = (CHAPTER_ROOT / "08-end-to-end-data-products.tex").read_text()

    for required_idea in (
        "laboratory representation of a system",
        "not the production",
        "independently reconstructible",
        "independently testable modules",
    ):
        assert required_idea in chapter


def test_overview_has_graduate_monograph_density() -> None:
    """Chapter 1 should be substantial but bounded against explanatory padding."""

    overview = (CHAPTER_ROOT / "00-part-i-overview.tex").read_text()
    word_count = len(overview.split())

    assert 3_000 <= word_count <= 5_500
    assert 24_000 <= len(overview) <= 45_000


def test_cover_identifies_the_book_course_and_part() -> None:
    cover = (TEXTBOOK_ROOT / "frontmatter" / "title.tex").read_text()

    for required_text in (
        "Data Science",
        "and Machine Learning",
        "A Systems Approach",
        "GRADUATE TEXT",
        "CMOR 438 / INDE 577",
        "PARTS I--II",
        "Randy Davila",
        "Rice University",
    ):
        assert required_text in cover


def test_repository_is_framed_as_a_graduate_text_with_executable_companions() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text()
    textbook_readme = (TEXTBOOK_ROOT / "README.md").read_text()
    preface = (TEXTBOOK_ROOT / "frontmatter" / "preface.tex").read_text()

    assert readme.startswith("# Data Science and Machine Learning")
    assert "source and executable companion for a developing\ngraduate text" in readme
    assert "The graduate text is the organizing artifact" in preface
    assert "developing graduate text" in textbook_readme
    assert "A Systems Approach" in readme


def test_glossary_defines_neighboring_concepts_students_may_confuse() -> None:
    glossary = (TEXTBOOK_ROOT / "appendices" / "glossary.tex").read_text()

    for term in (
        "agent &",
        "API &",
        "authentication &",
        "authorization &",
        "DataFrame &",
        "database &",
        "dtype &",
        "NumPy &",
        "pandas &",
        "shape &",
        "tool &",
        "vectorization &",
        "workflow &",
        "calibration &",
        "cross-validation &",
        "ensemble &",
        "leakage &",
        "loss function &",
        "model artifact &",
        "supervised learning &",
        "target &",
    ):
        assert term in glossary, f"Glossary is missing {term.removesuffix(' &')}"


@pytest.mark.parametrize("chapter", PART_II_CHAPTERS, ids=lambda path: path.stem)
def test_part_ii_chapters_are_substantive_connected_drafts(chapter: Path) -> None:
    """Part II should contain real exposition rather than topic placeholders."""

    source = chapter.read_text()

    assert len(source) >= 6_000
    assert source.count(r"\section{") >= 5
    assert "Lecture " in source


def test_latex_source_uses_portable_ascii_hyphens() -> None:
    """Unicode dash lookalikes can render inconsistently across TeX systems."""

    disallowed = {"\N{EN DASH}", "\N{EM DASH}", "\N{NON-BREAKING HYPHEN}"}

    for source_file in TEXTBOOK_ROOT.rglob("*.tex"):
        assert disallowed.isdisjoint(source_file.read_text()), source_file


def test_makefile_publishes_a_stable_pdf_path() -> None:
    makefile = (TEXTBOOK_ROOT / "Makefile").read_text()

    assert "data-science-machine-learning-textbook.pdf" in makefile
    assert "latexmk" in makefile.lower()


def test_compiled_textbook_is_present_and_nonempty() -> None:
    """The repository publishes a ready-to-read artifact for students."""

    assert OUTPUT_PDF.is_file()
    assert OUTPUT_PDF.stat().st_size > 100_000
