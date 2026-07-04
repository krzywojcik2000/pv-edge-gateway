import psycopg2

class DatabaseWriter:
    def __init__(self, config):
        self.conn = psycopg2.connect(
            dbname=config["db_name"],
            user=config["db_user"],
            password=config["db_password"],
            host=config["db_host"],
            port=config["db_port"]
        )
        self.cursor = self.conn.cursor()

        print("[DB] Connected to PostgreSQL")

    # -----------------------------
    # RAW DATA
    # -----------------------------
    def insert_raw(self, farm_id, data):
        self.cursor.execute("""
            INSERT INTO scada.raw_measurements
            (farm_id, temperature, dc_power, ac_power, energy, alarm)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            farm_id,
            data["temperature"],
            data["dc_power"],
            data["ac_power"],
            data["energy"],
            int(data["alarm"]["raw"])
        ))

        self.conn.commit()

    # -----------------------------
    # AGGREGATE DATA (placeholder)
    # -----------------------------
    def insert_aggregate(self, farm_id, data):
        self.cursor.execute("""
            INSERT INTO scada.agg_measurements
            (farm_id, avg_temp, avg_dc_power, avg_ac_power)
            VALUES (%s, %s, %s, %s)
        """, (
            farm_id,
            data["temperature"],
            data["dc_power"],
            data["ac_power"]
        ))

        self.conn.commit()

    # -----------------------------
    # BUSINESS KPI
    # -----------------------------
    def insert_business(self, farm_id, data):
        efficiency = (data["ac_power"] / data["dc_power"]) * 100

        self.cursor.execute("""
            INSERT INTO scada.business_kpi
            (farm_id, efficiency, energy)
            VALUES (%s, %s, %s)
        """, (
            farm_id,
            efficiency,
            data["energy"]
        ))

        self.conn.commit()

    # -----------------------------
    # ALARMS
    # -----------------------------
    def insert_alarm(self, farm_id, data):
        alarms = data["alarm"]

        if alarms["overtemperature"]:
            self.cursor.execute("""
                INSERT INTO scada.alarms (farm_id, type, message)
                VALUES (%s, %s, %s)
            """, (
                farm_id,
                "OVERTEMP",
                "Temperature above threshold"
            ))

        if alarms["overpower"]:
            self.cursor.execute("""
                INSERT INTO scada.alarms (farm_id, type, message)
                VALUES (%s, %s, %s)
            """, (
                farm_id,
                "OVERPOWER",
                "DC power above threshold"
            ))

        self.conn.commit()