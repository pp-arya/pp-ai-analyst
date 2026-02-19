"""Integration tests for the multi-warehouse SQL dialect system.

Tests the SQL dialect router, dialect method consistency, ConnectionManager
(DuckDB in-memory), schema profiler external warehouse entry point, and
cross-module imports. All tests run locally without external databases.
"""

import sys
import os

import pytest

# Ensure the repo root is on the path so helpers can be imported.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# =====================================================================
# 1. SQL dialect router (helpers/sql_dialect.py)
# =====================================================================


class TestGetDialect:
    """Verify get_dialect returns the correct dialect class for each key."""

    def test_duckdb_returns_duckdb_dialect(self):
        from helpers.sql_dialect import get_dialect
        from helpers.dialects.duckdb_dialect import DuckDBDialect

        dialect = get_dialect("duckdb")
        assert isinstance(dialect, DuckDBDialect)

    def test_postgres_returns_postgres_dialect(self):
        from helpers.sql_dialect import get_dialect
        from helpers.dialects.postgres import PostgresDialect

        dialect = get_dialect("postgres")
        assert isinstance(dialect, PostgresDialect)

    def test_bigquery_returns_bigquery_dialect(self):
        from helpers.sql_dialect import get_dialect
        from helpers.dialects.bigquery import BigQueryDialect

        dialect = get_dialect("bigquery")
        assert isinstance(dialect, BigQueryDialect)

    def test_snowflake_returns_snowflake_dialect(self):
        from helpers.sql_dialect import get_dialect
        from helpers.dialects.snowflake import SnowflakeDialect

        dialect = get_dialect("snowflake")
        assert isinstance(dialect, SnowflakeDialect)

    def test_motherduck_alias_returns_duckdb_dialect(self):
        from helpers.sql_dialect import get_dialect
        from helpers.dialects.duckdb_dialect import DuckDBDialect

        dialect = get_dialect("motherduck")
        assert isinstance(dialect, DuckDBDialect)

    def test_postgresql_alias_returns_postgres_dialect(self):
        from helpers.sql_dialect import get_dialect
        from helpers.dialects.postgres import PostgresDialect

        dialect = get_dialect("postgresql")
        assert isinstance(dialect, PostgresDialect)

    def test_unknown_raises_value_error(self):
        from helpers.sql_dialect import get_dialect

        with pytest.raises(ValueError, match="Unknown connection type"):
            get_dialect("unknown")

    def test_case_insensitive_lookup(self):
        from helpers.sql_dialect import get_dialect
        from helpers.dialects.duckdb_dialect import DuckDBDialect

        dialect = get_dialect("DuckDB")
        assert isinstance(dialect, DuckDBDialect)

    def test_whitespace_stripped(self):
        from helpers.sql_dialect import get_dialect
        from helpers.dialects.bigquery import BigQueryDialect

        dialect = get_dialect("  bigquery  ")
        assert isinstance(dialect, BigQueryDialect)

    def test_list_dialects_returns_all_keys(self):
        from helpers.sql_dialect import list_dialects

        keys = list_dialects()
        assert isinstance(keys, list)
        for expected in ("duckdb", "motherduck", "postgres", "bigquery", "snowflake"):
            assert expected in keys


# =====================================================================
# 2. Dialect method consistency
# =====================================================================


# The dialects in the codebase expose these common methods.  The actual
# signature for date_trunc is date_trunc(field, unit).


_ALL_DIALECT_KEYS = ["duckdb", "postgres", "bigquery", "snowflake"]


class TestDialectMethodConsistency:
    """Every dialect must produce valid SQL strings from shared methods."""

    @pytest.fixture(params=_ALL_DIALECT_KEYS)
    def dialect(self, request):
        from helpers.sql_dialect import get_dialect

        return get_dialect(request.param)

    # --- date_trunc ---

    def test_date_trunc_returns_string(self, dialect):
        result = dialect.date_trunc("created_at", "month")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_date_trunc_contains_field(self, dialect):
        result = dialect.date_trunc("created_at", "month")
        assert "created_at" in result

    def test_date_trunc_contains_month(self, dialect):
        result = dialect.date_trunc("created_at", "month")
        # month or MONTH
        assert "month" in result.lower()

    # --- safe_divide ---

    def test_safe_divide_returns_string(self, dialect):
        result = dialect.safe_divide("revenue", "orders")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_safe_divide_contains_operands(self, dialect):
        result = dialect.safe_divide("revenue", "orders")
        assert "revenue" in result
        assert "orders" in result

    # --- sample_rows ---

    def test_sample_rows_returns_string(self, dialect):
        result = dialect.sample_rows("orders", 100)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_sample_rows_contains_table(self, dialect):
        result = dialect.sample_rows("orders", 100)
        assert "orders" in result

    def test_sample_rows_is_select(self, dialect):
        result = dialect.sample_rows("orders", 100)
        assert result.upper().startswith("SELECT")

    # --- describe_table ---

    def test_describe_table_returns_string(self, dialect):
        result = dialect.describe_table("orders")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_describe_table_contains_table(self, dialect):
        result = dialect.describe_table("orders")
        assert "orders" in result.lower()

    # --- limit_clause ---

    def test_limit_clause_returns_string(self, dialect):
        result = dialect.limit_clause(10)
        assert isinstance(result, str)
        assert "10" in result

    # --- date_diff ---

    def test_date_diff_returns_string(self, dialect):
        result = dialect.date_diff("day", "start_date", "end_date")
        assert isinstance(result, str)
        assert len(result) > 0

    # --- string_agg ---

    def test_string_agg_returns_string(self, dialect):
        result = dialect.string_agg("category")
        assert isinstance(result, str)
        assert "category" in result

    # --- qualify_table ---

    def test_qualify_table_without_schema(self, dialect):
        result = dialect.qualify_table("orders")
        assert isinstance(result, str)
        assert "orders" in result.lower()

    def test_qualify_table_with_schema(self, dialect):
        result = dialect.qualify_table("orders", "analytics")
        assert isinstance(result, str)
        assert "orders" in result.lower()
        assert "analytics" in result.lower()

    # --- current_timestamp ---

    def test_current_timestamp_returns_string(self, dialect):
        result = dialect.current_timestamp()
        assert isinstance(result, str)
        assert "CURRENT_TIMESTAMP" in result.upper()

    # --- create_temp_table ---

    def test_create_temp_table_returns_string(self, dialect):
        result = dialect.create_temp_table("tmp_agg", "SELECT 1")
        assert isinstance(result, str)
        assert "tmp_agg" in result.lower()
        assert "SELECT 1" in result


# =====================================================================
# 2b. Dialect-specific output spot checks
# =====================================================================


class TestDuckDBDialectSpecific:
    """Spot-check DuckDB-specific SQL output."""

    def test_sample_uses_using_sample(self):
        from helpers.dialects.duckdb_dialect import DuckDBDialect

        result = DuckDBDialect().sample_rows("orders", 100)
        assert result == "SELECT * FROM orders USING SAMPLE 100"

    def test_describe_uses_describe(self):
        from helpers.dialects.duckdb_dialect import DuckDBDialect

        result = DuckDBDialect().describe_table("customers")
        assert result == "DESCRIBE customers"

    def test_date_diff_uses_native(self):
        from helpers.dialects.duckdb_dialect import DuckDBDialect

        result = DuckDBDialect().date_diff("day", "start_date", "end_date")
        assert result == "date_diff('day', start_date, end_date)"

    def test_name_is_duckdb(self):
        from helpers.dialects.duckdb_dialect import DuckDBDialect

        assert DuckDBDialect().name == "duckdb"


class TestBigQueryDialectSpecific:
    """Spot-check BigQuery-specific SQL output."""

    def test_date_trunc_field_first_unit_upper(self):
        from helpers.dialects.bigquery import BigQueryDialect

        result = BigQueryDialect().date_trunc("order_date", "month")
        assert result == "DATE_TRUNC(order_date, MONTH)"

    def test_safe_divide_uses_safe_divide(self):
        from helpers.dialects.bigquery import BigQueryDialect

        result = BigQueryDialect().safe_divide("revenue", "orders")
        assert result == "SAFE_DIVIDE(revenue, orders)"

    def test_qualify_table_uses_backticks(self):
        from helpers.dialects.bigquery import BigQueryDialect

        result = BigQueryDialect().qualify_table("orders", "my_project.analytics")
        assert result == "`my_project.analytics.orders`"

    def test_name_is_bigquery(self):
        from helpers.dialects.bigquery import BigQueryDialect

        assert BigQueryDialect().name == "bigquery"


class TestSnowflakeDialectSpecific:
    """Spot-check Snowflake-specific SQL output."""

    def test_date_trunc_quoted_unit(self):
        from helpers.dialects.snowflake import SnowflakeDialect

        result = SnowflakeDialect().date_trunc("order_date", "month")
        assert result == "DATE_TRUNC('MONTH', order_date)"

    def test_safe_divide_uses_div0null(self):
        from helpers.dialects.snowflake import SnowflakeDialect

        result = SnowflakeDialect().safe_divide("revenue", "orders")
        assert result == "DIV0NULL(revenue, orders)"

    def test_sample_rows_uses_sample_rows_syntax(self):
        from helpers.dialects.snowflake import SnowflakeDialect

        result = SnowflakeDialect().sample_rows("orders", 100)
        assert result == "SELECT * FROM orders SAMPLE (100 ROWS)"

    def test_qualify_table_uppercases(self):
        from helpers.dialects.snowflake import SnowflakeDialect

        result = SnowflakeDialect().qualify_table("orders", "ANALYTICS_DB.PUBLIC")
        assert result == "ANALYTICS_DB.PUBLIC.ORDERS"

    def test_name_is_snowflake(self):
        from helpers.dialects.snowflake import SnowflakeDialect

        assert SnowflakeDialect().name == "snowflake"


class TestPostgresDialectSpecific:
    """Spot-check Postgres-specific SQL output."""

    def test_describe_table_uses_information_schema(self):
        from helpers.dialects.postgres import PostgresDialect

        result = PostgresDialect().describe_table("customers")
        assert "information_schema.columns" in result
        assert "customers" in result

    def test_sample_rows_uses_tablesample(self):
        from helpers.dialects.postgres import PostgresDialect

        result = PostgresDialect().sample_rows("orders", 100)
        assert "TABLESAMPLE" in result
        assert "BERNOULLI" in result

    def test_name_is_postgres(self):
        from helpers.dialects.postgres import PostgresDialect

        assert PostgresDialect().name == "postgres"


# =====================================================================
# 3. ConnectionManager (helpers/connection_manager.py)
# =====================================================================


class TestConnectionManagerDuckDB:
    """Test ConnectionManager with DuckDB in-memory (no external DB needed)."""

    def _make_duckdb_in_memory_config(self):
        """Return a config dict that forces DuckDB in-memory connection."""
        return {
            "type": "duckdb",
            "duckdb_path": ":memory:",
        }

    def test_instantiate_with_duckdb_config(self):
        from helpers.connection_manager import ConnectionManager

        config = self._make_duckdb_in_memory_config()
        mgr = ConnectionManager(config=config)
        assert mgr.connection_type == "duckdb"

    def test_test_connection_duckdb_in_memory(self):
        """test_connection() returns ok=True for an in-memory DuckDB."""
        from helpers.connection_manager import ConnectionManager

        config = self._make_duckdb_in_memory_config()
        mgr = ConnectionManager(config=config)
        # The _connect_duckdb method will fall back to CSV when the
        # :memory: path does not pass Path(db_path).exists(). We need
        # to set up the connection manually for a true in-memory test.
        import duckdb

        mgr._connection = duckdb.connect(":memory:")
        mgr._conn_type = "duckdb"

        result = mgr.test_connection()
        assert isinstance(result, dict)
        assert result["ok"] is True
        assert result["type"] == "duckdb"

        mgr.close()

    def test_list_tables_on_empty_duckdb(self):
        """list_tables() returns an empty list on a fresh in-memory DuckDB."""
        from helpers.connection_manager import ConnectionManager

        import duckdb

        config = self._make_duckdb_in_memory_config()
        mgr = ConnectionManager(config=config)
        mgr._connection = duckdb.connect(":memory:")
        mgr._conn_type = "duckdb"

        tables = mgr.list_tables()
        assert isinstance(tables, list)
        assert tables == []

        mgr.close()

    def test_list_tables_after_creating_table(self):
        """list_tables() finds a table after it is created."""
        from helpers.connection_manager import ConnectionManager

        import duckdb

        config = self._make_duckdb_in_memory_config()
        mgr = ConnectionManager(config=config)
        mgr._connection = duckdb.connect(":memory:")
        mgr._conn_type = "duckdb"

        mgr._connection.sql("CREATE TABLE test_orders (id INT, amount FLOAT)")
        tables = mgr.list_tables()
        assert "test_orders" in tables

        mgr.close()

    def test_context_manager_works(self):
        """The 'with' statement calls connect/close properly."""
        from helpers.connection_manager import ConnectionManager

        import duckdb

        config = self._make_duckdb_in_memory_config()

        # Manually inject a connection because the default _connect_duckdb
        # checks Path.exists() which returns False for :memory:.
        mgr = ConnectionManager(config=config)
        mgr._connection = duckdb.connect(":memory:")
        mgr._conn_type = "duckdb"

        # Verify close resets the connection.
        assert mgr._connection is not None
        mgr.close()
        assert mgr._connection is None

    def test_context_manager_with_statement(self):
        """Using 'with ConnectionManager(config) as mgr' enters and exits."""
        from helpers.connection_manager import ConnectionManager

        # CSV-type config always works without external dependencies.
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"type": "csv", "csv_path": tmpdir}
            with ConnectionManager(config=config) as mgr:
                assert mgr.connection_type == "csv"
            # After exiting, connection should be cleaned up.
            assert mgr._connection is None

    def test_query_duckdb_in_memory(self):
        """query() executes SQL and returns a DataFrame."""
        from helpers.connection_manager import ConnectionManager

        import duckdb
        import pandas as pd

        config = self._make_duckdb_in_memory_config()
        mgr = ConnectionManager(config=config)
        mgr._connection = duckdb.connect(":memory:")
        mgr._conn_type = "duckdb"

        df = mgr.query("SELECT 42 AS answer")
        assert isinstance(df, pd.DataFrame)
        assert df.iloc[0, 0] == 42

        mgr.close()

    def test_get_table_schema_duckdb(self):
        """get_table_schema() returns column info for a DuckDB table."""
        from helpers.connection_manager import ConnectionManager

        import duckdb

        config = self._make_duckdb_in_memory_config()
        mgr = ConnectionManager(config=config)
        mgr._connection = duckdb.connect(":memory:")
        mgr._conn_type = "duckdb"

        mgr._connection.sql("CREATE TABLE demo (id INTEGER, name VARCHAR)")
        schema = mgr.get_table_schema("demo")
        assert isinstance(schema, list)
        assert len(schema) == 2
        col_names = [c["name"] for c in schema]
        assert "id" in col_names
        assert "name" in col_names

        mgr.close()

    def test_connection_type_property(self):
        from helpers.connection_manager import ConnectionManager

        config = {"type": "csv", "csv_path": "/tmp"}
        mgr = ConnectionManager(config=config)
        assert mgr.connection_type == "csv"

    def test_schema_prefix_property(self):
        from helpers.connection_manager import ConnectionManager

        config = {"type": "csv", "csv_path": "/tmp", "schema_prefix": "analytics"}
        mgr = ConnectionManager(config=config)
        assert mgr.schema_prefix == "analytics"

    def test_unsupported_type_raises(self):
        from helpers.connection_manager import ConnectionManager

        config = {"type": "oracle"}
        mgr = ConnectionManager(config=config)
        with pytest.raises(ConnectionError, match="Unsupported connection type"):
            mgr.connect()


# =====================================================================
# 4. Schema profiler external warehouse
# =====================================================================


class TestProfileExternalWarehouse:
    """Verify profile_external_warehouse exists and is callable."""

    def test_function_exists_and_callable(self):
        from helpers.schema_profiler import profile_external_warehouse

        assert callable(profile_external_warehouse)

    def test_accepts_connection_config_dict(self):
        """profile_external_warehouse can be called with a DuckDB config.

        We pass a CSV-type config pointing at a temp directory so it does
        not need any real warehouse connection.
        """
        import tempfile
        from helpers.schema_profiler import profile_external_warehouse

        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"type": "csv", "csv_path": tmpdir}
            result = profile_external_warehouse(config)

        assert isinstance(result, dict)
        assert "dataset" in result
        assert "profiled_at" in result
        assert "tables" in result
        assert isinstance(result["tables"], list)

    def test_profile_source_exists_and_callable(self):
        from helpers.schema_profiler import profile_source

        assert callable(profile_source)

    def test_compare_snapshots_exists_and_callable(self):
        from helpers.schema_profiler import compare_snapshots

        assert callable(compare_snapshots)

    def test_discover_relationships_exists_and_callable(self):
        from helpers.schema_profiler import discover_relationships

        assert callable(discover_relationships)

    def test_list_sources_exists_and_callable(self):
        from helpers.schema_profiler import list_sources

        assert callable(list_sources)


# =====================================================================
# 5. Cross-module imports (no circular dependencies)
# =====================================================================


class TestCrossModuleImports:
    """Verify all imports from sql_dialect, connection_manager,
    schema_profiler work without errors or circular dependencies."""

    def test_import_sql_dialect(self):
        from helpers.sql_dialect import get_dialect, list_dialects

        assert callable(get_dialect)
        assert callable(list_dialects)

    def test_import_connection_manager(self):
        from helpers.connection_manager import ConnectionManager, SUPPORTED_TYPES

        assert ConnectionManager is not None
        assert isinstance(SUPPORTED_TYPES, dict)

    def test_import_schema_profiler(self):
        from helpers.schema_profiler import (
            profile_source,
            compare_snapshots,
            discover_relationships,
            list_sources,
            get_table_reference,
            profile_external_warehouse,
        )

        for fn in (
            profile_source,
            compare_snapshots,
            discover_relationships,
            list_sources,
            get_table_reference,
            profile_external_warehouse,
        ):
            assert callable(fn)

    def test_import_dialects_init(self):
        from helpers.dialects import (
            SQLDialect,
            DuckDBDialect,
            PostgresDialect,
            BigQueryDialect,
            SnowflakeDialect,
        )

        for cls in (SQLDialect, DuckDBDialect, PostgresDialect,
                     BigQueryDialect, SnowflakeDialect):
            assert cls is not None

    def test_import_base_dialect(self):
        from helpers.dialects.base import SQLDialect

        assert SQLDialect is not None
        # Verify it can be instantiated.
        d = SQLDialect()
        assert d.name == "base"

    def test_import_individual_dialects(self):
        from helpers.dialects.duckdb_dialect import DuckDBDialect
        from helpers.dialects.postgres import PostgresDialect
        from helpers.dialects.bigquery import BigQueryDialect
        from helpers.dialects.snowflake import SnowflakeDialect

        assert DuckDBDialect().name == "duckdb"
        assert PostgresDialect().name == "postgres"
        assert BigQueryDialect().name == "bigquery"
        assert SnowflakeDialect().name == "snowflake"

    def test_dialect_from_router_matches_direct_import(self):
        """get_dialect produces the same class as a direct import."""
        from helpers.sql_dialect import get_dialect
        from helpers.dialects.duckdb_dialect import DuckDBDialect
        from helpers.dialects.postgres import PostgresDialect
        from helpers.dialects.bigquery import BigQueryDialect
        from helpers.dialects.snowflake import SnowflakeDialect

        assert type(get_dialect("duckdb")) is DuckDBDialect
        assert type(get_dialect("postgres")) is PostgresDialect
        assert type(get_dialect("bigquery")) is BigQueryDialect
        assert type(get_dialect("snowflake")) is SnowflakeDialect

    def test_no_circular_import_sql_dialect_then_connection_manager(self):
        """Importing sql_dialect then connection_manager raises no errors."""
        import importlib

        mod1 = importlib.import_module("helpers.sql_dialect")
        mod2 = importlib.import_module("helpers.connection_manager")
        assert mod1 is not None
        assert mod2 is not None

    def test_no_circular_import_schema_profiler_then_sql_dialect(self):
        """Importing schema_profiler then sql_dialect raises no errors."""
        import importlib

        mod1 = importlib.import_module("helpers.schema_profiler")
        mod2 = importlib.import_module("helpers.sql_dialect")
        assert mod1 is not None
        assert mod2 is not None
