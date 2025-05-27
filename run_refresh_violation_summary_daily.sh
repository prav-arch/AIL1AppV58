#!/bin/bash
SQL_FILE="refresh_violation_summary_daily.sql"
CLICKHOUSE_HOST="localhost"
CLICKHOUSE_PORT="9000"
CLICKHOUSE_USER="default"

clickhouse-client --host $CLICKHOUSE_HOST --port $CLICKHOUSE_PORT --user $CLICKHOUSE_USER --multiquery < "$SQL_FILE"
