-- =====================================================
-- PV EDGE GATEWAY - DATABASE INITIALIZATION SCRIPT
-- =====================================================


CREATE SCHEMA IF NOT EXISTS scada;


-- =====================================================
-- RAW MEASUREMENTS
-- =====================================================

CREATE TABLE IF NOT EXISTS scada.raw_measurements (

    id SERIAL PRIMARY KEY,

    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    farm_id TEXT DEFAULT 'KRK-01',

    temperature FLOAT,

    dc_power FLOAT,

    ac_power FLOAT,

    energy FLOAT,

    alarm INT

);


CREATE INDEX IF NOT EXISTS idx_raw_ts
ON scada.raw_measurements(ts);



-- =====================================================
-- AGGREGATION 1 MIN
-- =====================================================

CREATE TABLE IF NOT EXISTS scada.aggregate_1min (

    id SERIAL PRIMARY KEY,

    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    farm_id TEXT DEFAULT 'KRK-01',

    avg_temperature FLOAT,

    avg_dc_power FLOAT,

    avg_ac_power FLOAT,

    energy_sum FLOAT,

    alarm_count INT

);


CREATE INDEX IF NOT EXISTS idx_agg_ts
ON scada.aggregate_1min(ts);



-- =====================================================
-- BUSINESS HOURLY KPI
-- =====================================================

CREATE TABLE IF NOT EXISTS scada.business_hourly (

    id SERIAL PRIMARY KEY,

    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    farm_id TEXT DEFAULT 'KRK-01',

    energy_total FLOAT,

    avg_temperature FLOAT,

    alarm_events INT,

    availability FLOAT DEFAULT 100.0

);


CREATE INDEX IF NOT EXISTS idx_business_ts
ON scada.business_hourly(ts);



-- =====================================================
-- ALARMS
-- =====================================================

CREATE TABLE IF NOT EXISTS scada.alarms (

    id SERIAL PRIMARY KEY,

    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    farm_id TEXT DEFAULT 'KRK-01',

    alarm_type TEXT,

    message TEXT,

    value FLOAT,

    severity TEXT DEFAULT 'MEDIUM'

);


CREATE INDEX IF NOT EXISTS idx_alarm_ts
ON scada.alarms(ts);



-- =====================================================
-- END
-- =====================================================