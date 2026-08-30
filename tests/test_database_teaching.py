"""Contracts for Lecture 3's local and remote database lesson."""

import ast
import tomllib
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
NOTEBOOK_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "lecture-03-packages-numpy-pandas"
    / "05-databases-local-and-remote.ipynb"
)


def notebook() -> nbformat.NotebookNode:
    """Load the local and remote database notebook."""

    return nbformat.read(NOTEBOOK_PATH, as_version=4)


def notebook_trees() -> list[ast.Module]:
    """Parse every code cell independently."""

    return [
        ast.parse(cell.source)
        for cell in notebook().cells
        if cell.cell_type == "code"
    ]


def narrative() -> str:
    """Return normalized lowercase prose for conceptual assertions."""

    markdown = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    )
    return " ".join(markdown.lower().split())


def code_text() -> str:
    """Return all executable examples as one string."""

    return "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "code"
    )


def test_database_clients_are_declared_and_locked() -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)

    declared = project["project"]["dependencies"]
    for requirement_prefix in (
        "sqlalchemy>=",
        "duckdb>=",
        "psycopg[binary]>=",
        "boto3>=",
        "pyarrow>=",
        "polars>=",
    ):
        assert any(
            requirement.startswith(requirement_prefix) for requirement in declared
        )

    lock_text = (PROJECT_ROOT / "uv.lock").read_text(encoding="utf-8")
    for package in (
        "sqlalchemy",
        "duckdb",
        "psycopg",
        "psycopg-binary",
        "boto3",
        "pyarrow",
        "polars",
    ):
        assert f'name = "{package}"' in lock_text


def test_notebook_is_a_long_form_local_and_remote_database_reference() -> None:
    lesson = notebook()

    assert len(lesson.cells) >= 100
    assert sum(cell.cell_type == "markdown" for cell in lesson.cells) >= 70
    assert sum(cell.cell_type == "code" for cell in lesson.cells) >= 25
    assert lesson.metadata.rice_dsm.estimated_core_minutes >= 150
    assert lesson.metadata.rice_dsm.practice_minutes >= 100


def test_notebook_distinguishes_database_layers_and_deployments() -> None:
    lesson = narrative()

    for concept in (
        "database-management system",
        "driver",
        "connection",
        "cursor/result",
        "transaction",
        "schema",
        "sqlalchemy **engine**",
        "embedded file/serverless",
        "in-process analytical",
        "remote client/server",
        "managed warehouse/lakehouse",
    ):
        assert concept in lesson


def test_notebook_builds_a_constrained_relational_schema() -> None:
    source = code_text()

    for schema_feature in (
        "CREATE TABLE experiments",
        "CREATE TABLE sensors",
        "CREATE TABLE measurements",
        "PRIMARY KEY",
        "FOREIGN KEY",
        "UNIQUE (experiment_id, sensor_id, time_s)",
        "NOT NULL",
        "CHECK (",
        "PRAGMA foreign_keys = ON",
    ):
        assert schema_feature in source


def test_executed_sql_uses_parameters_instead_of_f_strings() -> None:
    execute_calls = [
        node
        for tree in notebook_trees()
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"execute", "executemany"}
        and node.args
    ]

    assert len(execute_calls) >= 20
    assert all(not isinstance(call.args[0], ast.JoinedStr) for call in execute_calls)

    source = code_text()
    assert "requested_material = \"copper' OR 1=1 --\"" in source
    assert "safe_rows = sqlite_connection.execute(safe_sql" in source
    assert "safe_rows == []" in source


def test_notebook_teaches_sql_semantics_and_database_correctness() -> None:
    lesson = narrative()

    for concept in (
        "three-valued logic",
        "count(*)",
        "joins encode cardinality assumptions",
        "atomicity",
        "rolls back",
        "common-table expressions",
        "window function",
        "following observation",
        "indexes trade write/storage cost",
        "query plans can change",
    ):
        assert concept in lesson


def test_notebook_integrates_sqlite_pandas_sqlalchemy_and_duckdb() -> None:
    source = code_text()

    for example in (
        "sqlite3.connect(database_path)",
        "pd.read_sql_query(",
        "chunksize=7",
        ".to_sql(",
        "create_engine(sqlite_url)",
        "sqlalchemy_engine.begin()",
        "autoload_with=sqlalchemy_engine",
        'duckdb.connect(\":memory:\")',
        'register(\"measurement_frame\"',
        ".write_parquet(",
        ".read_parquet(",
    ):
        assert example in source


def test_notebook_teaches_larger_than_memory_access_patterns() -> None:
    lesson = narrative()
    source = code_text()

    for concept in (
        "working-set estimate",
        "projection pushdown",
        "predicate pushdown",
        "partition pruning",
        "bounded-state algorithm",
        "keyset pagination",
        "server-side cursor",
        "tiny files",
        "materialization boundary",
        "distributed execution is a systems exercise",
    ):
        assert concept in lesson

    for example in (
        "memory_usage(index=True, deep=True)",
        "pads.write_dataset(",
        "scientific_dataset.scanner(",
        "for record_batch in lake_scanner.to_batches()",
        "pl.scan_parquet(",
        '.collect(engine="streaming")',
        "duckdb_connection.read_parquet(",
        "def iter_measurement_pages(",
        "WHERE measurement_id > ?",
    ):
        assert example in source


def test_notebook_teaches_industry_lab_and_aws_workflows_offline() -> None:
    lesson = narrative()
    source = code_text()

    for concept in (
        "typical industry or laboratory data path",
        "landing/raw",
        "aws glue data catalog",
        "amazon athena",
        "amazon rds/aurora",
        "amazon redshift",
        "workload identity",
        "least-privilege iam",
        "2 tb training-data workflow",
        "hpc lab",
        "slurm",
    ):
        assert concept in lesson

    for example in (
        "Config(signature_version=UNSIGNED)",
        "with Stubber(s3_client)",
        "s3_client.list_objects_v2(**expected_list_parameters)",
        "def split_s3_uri(",
        "def build_athena_request(",
    ):
        assert example in source

    assert 'boto3.client("athena"' not in source
    assert ".start_query_execution(" not in source


def test_remote_configuration_is_realistic_but_offline_safe() -> None:
    lesson = narrative()
    source = code_text()

    assert 'host=\"database.example.invalid\"' in source
    assert "password=None" in source
    assert 'sslmode\": \"require\"' in source
    assert 'connect_timeout\": 5' in source
    assert "pool_pre_ping=True" in source
    assert "remote_engine.dispose()" in source
    assert "remote_engine.connect(" not in source

    for concept in (
        "secret manager",
        "pool exhaustion",
        "unknown commit state",
        "idempotency keys",
        "exponential backoff with jitter",
        "transaction isolation",
        "least-privilege",
        "schema migrations",
    ):
        assert concept in lesson


def test_notebook_teaches_reproducible_ml_extracts_and_governance() -> None:
    lesson = narrative()

    for concept in (
        "database query is part of the experiment",
        "schema/migration version",
        "snapshot identity",
        "ingestion watermark",
        "explicit column and row ordering",
        "checksum",
        "future information",
        "same patient/device/entity",
        "split policy follows the deployment question",
        "sensitive columns",
        "audit access",
    ):
        assert concept in lesson


def test_reusable_function_is_documented_annotated_and_parameterized() -> None:
    functions = {
        node.name: node
        for tree in notebook_trees()
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    function = functions["count_measurements_for_material"]
    docstring = ast.get_docstring(function)

    assert docstring is not None
    assert "Parameters\n----------" in docstring
    assert "Returns\n-------" in docstring
    assert all(argument.annotation is not None for argument in function.args.args)
    assert function.returns is not None

    function_source = ast.unparse(function)
    assert "WHERE e.material = ?" in function_source


def test_notebook_closes_connections_and_removes_temporary_files() -> None:
    source = code_text()

    for cleanup in (
        "duckdb_connection.close()",
        "sqlalchemy_engine.dispose()",
        "sqlite_connection.close()",
        "database_workspace.cleanup()",
        "assert not database_path.exists()",
        "assert not parquet_path.exists()",
    ):
        assert cleanup in source


def test_notebook_contains_no_real_hosts_credentials_or_personal_paths() -> None:
    complete_text = "\n".join(cell.source for cell in notebook().cells)

    assert "/Users/" not in complete_text
    assert "C:\\Users\\" not in complete_text
    assert "localhost" not in complete_text
    assert "127.0.0.1" not in complete_text
    sanitized_text = complete_text.replace("password=None", "").replace(
        "hide_password=True", ""
    )
    assert "password=" not in sanitized_text
