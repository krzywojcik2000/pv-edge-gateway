# edge_gateway/output/database/database_writer.py

import psycopg2
from psycopg2.extras import execute_values


class DatabaseWriter:

    def __init__(self, config):

        self.conn = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            dbname=config["db_name"],
            user=config["db_user"],
            password=config["db_password"]
        )

        self.cursor = self.conn.cursor()

    # =====================================================
    # RAW
    # =====================================================

    def insert_raw_batch(self, measurements):

        rows = [
            (
                m.farm_id,
                m.temperature,
                m.dc_power,
                m.ac_power,
                m.energy,
                int(m.alarm.raw)
            )
            for m in measurements
        ]

        self._execute_values(
            """
            INSERT INTO scada.raw_measurements
            (
                farm_id,
                temperature,
                dc_power,
                ac_power,
                energy,
                alarm
            )
            VALUES %s
            """,
            rows
        )

    # =====================================================
    # AGGREGATION
    # =====================================================

    def insert_aggregate(self, aggregate):

        self._execute(
            """
            INSERT INTO scada.aggregate_1min
            (
                farm_id,
                avg_temperature,
                avg_dc_power,
                avg_ac_power,
                energy_sum,
                alarm_count
            )
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (
                aggregate["farm_id"],
                aggregate["avg_temperature"],
                aggregate["avg_dc_power"],
                aggregate["avg_ac_power"],
                aggregate["energy_sum"],
                aggregate["alarm_count"]
            )
        )

    # =====================================================
    # BUSINESS
    # =====================================================

    def insert_business(self, business):

        self._execute(
            """
            INSERT INTO scada.business_hourly
            (
                farm_id,
                energy_total,
                avg_temperature,
                alarm_events,
                availability
            )
            VALUES (%s,%s,%s,%s,%s)
            """,
            (
                business["farm_id"],
                business["energy_total"],
                business["avg_temperature"],
                business["alarm_events"],
                business["availability"]
            )
        )

    # =====================================================
    # ALARMS
    # =====================================================

    def insert_alarm_batch(self, alarms):

        rows = [
            (
                alarm["farm_id"],
                alarm["alarm_type"],
                alarm["message"],
                alarm["value"],
                alarm["severity"]
            )
            for alarm in alarms
        ]

        self._execute_values(
            """
            INSERT INTO scada.alarms
            (
                farm_id,
                alarm_type,
                message,
                value,
                severity
            )
            VALUES %s
            """,
            rows
        )

    # =====================================================
    # INTERNAL SQL HELPERS
    # =====================================================

    def _execute(self, query, params):

        try:
            self.cursor.execute(query, params)
            self.conn.commit()

        except Exception:
            self.conn.rollback()
            raise

    def _execute_values(self, query, rows):

        try:
            execute_values(
                self.cursor,
                query,
                rows
            )

            self.conn.commit()

        except Exception:
            self.conn.rollback()
            raise

    # =====================================================
    # CONNECTION
    # =====================================================

    def close(self):

        self.cursor.close()
        self.conn.close()