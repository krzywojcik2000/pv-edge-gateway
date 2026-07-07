# PV EDGE GATEWAY - SYSTEM ARCHITECTURE


                              +----------------+
                              |      MAIN      |
                              |  entry point   |
                              +-------+--------+
                                      |
                                      v
                              +----------------+
                              |  Application   |
                              | dependency     |
                              | composition    |
                              +-------+--------+
                                      |
                                      v
                              +----------------+
                              |   Lifecycle    |
                              | start / stop   |
                              | orchestration  |
                              +-------+--------+
                                      |
        ------------------------------------------------------------
        |                         |                     |           |
        v                         v                     v           v


+----------------+       +----------------+     +----------------+ 
| CycleExecutor  |       |  DBRuntime     |     | MQTTManager    |
|                |       | async runtime  |     | async runtime  |
| INPUT +        |       |                |     |                |
| PROCESSING     |       | database flow  |     | mqtt flow      |
+-------+--------+       +----------------+     +----------------+
        |
        |
        v


===============================================================
                    DATA ACQUISITION PIPELINE
===============================================================


        +----------------+
        | ModbusManager  |
        |                |
        | - TCP read     |
        | - connection   |
        | - modbus       |
        |   errors       |
        +-------+--------+
                |
                |
                v

        +----------------+
        | Processing     |
        | Pipeline       |
        |                |
        | 1. Decoder     |
        | 2. Normalizer  |
        | 3. Enricher    |
        +-------+--------+
                |
                |
                v

        +----------------+
        | Measurement    |
        | Domain Object  |
        |                |
        | temperature    |
        | power          |
        | energy         |
        | alarms         |
        | timestamp      |
        +-------+--------+
                |
                |
                v


===============================================================
                         FANOUT LAYER
===============================================================


                        +----------------+
                        | FanoutManager  |
                        |                |
                        | distributes   |
                        | measurements   |
                        +-------+--------+
                                |
          ----------------------+----------------------
          |                     |                     |
          v                     v                     v


+----------------+   +----------------+    +----------------+
| DB Queue       |   | MQTT Queue     |    | OPCUA Queue    |
+-------+--------+   +-------+--------+    +-------+--------+
        |                    |                     |
        v                    v                     v



===============================================================
                         OUTPUT LAYER
===============================================================



######################## DATABASE ############################


                +----------------+
                | DBRuntime      |
                |                |
                | async worker   |
                +-------+--------+
                        |
                        |
        ---------------------------------
        |              |        |        |
        v              v        v        v


 +-------------+ +-------------+ +-------------+ +-------------+
 | RawManager  | | Aggregation | | Business    | | Alarm       |
 |             | | Manager     | | Manager     | | Manager     |
 +------+------+ +------+------+ +------+------+ +------+------+
        |               |              |               |
        ------------------------------------------------
                        |
                        v

                +----------------+
                | DatabaseWriter |
                |                |
                | PostgreSQL I/O |
                +-------+--------+
                        |
                        v

                +----------------+
                |   PostgreSQL   |
                | SCADA database |
                +----------------+



DATABASE RESILIENCE:

                DatabaseWriter
                      |
                      v
                +-------------+
                | RetryManager|
                +------+------+
                       |
          failure ----+
                       |
                       v

              +----------------+
              | Persistent    |
              | Store          |
              |                |
              | SQLite buffer  |
              | offline data   |
              +----------------+



######################## MQTT #################################


                +----------------+
                | MQTTManager    |
                |                |
                | queue worker   |
                +-------+--------+
                        |
                        v

                +----------------+
                | MQTTPublisher  |
                |                |
                | MQTT transport |
                +-------+--------+
                        |
                        v

                +----------------+
                | MQTT Broker    |
                +----------------+



MQTT RESILIENCE:

MQTTPublisher
      |
      v
RetryManager
      |
      v

failure
  |
  +--> ErrorStore
  |
  +--> Drop telemetry
       (live data philosophy)



######################## OPC UA ################################


                +----------------+
                | OPCUAManager   |
                |                |
                | queue worker   |
                +-------+--------+
                        |
                        v

                +----------------+
                | OPCUAServer    |
                |                |
                | OPC UA nodes   |
                | tag updates    |
                +-------+--------+
                        |
                        v

                +----------------+
                | SCADA Client   |
                | Ignition       |
                +----------------+



OPC UA RESILIENCE:

OPCUAServer
      |
      v
RetryManager
      |
      v

failure
  |
  +--> ErrorStore



===============================================================
                     CROSS SYSTEM SERVICES
===============================================================



                     +----------------+
                     | RetryManager   |
                     |                |
                     | common retry   |
                     | policy         |
                     +----------------+

Used by:

        Modbus
          |
        Database
          |
        MQTT
          |
        OPC UA



                     +----------------+
                     | ErrorStore     |
                     |                |
                     | SQLite history |
                     | of failures    |
                     +----------------+

Stores:

- component
- operation
- timestamp
- exception type
- message
- context



                     +----------------+
                     | Watchdog       |
                     |                |
                     | monitoring     |
                     | only           |
                     +----------------+

Observes:

- last successful Modbus read
- database activity
- MQTT connectivity
- OPC UA activity

Does NOT control:

- retry
- recovery
- business logic



===============================================================
                    COMPLETE DATA FLOW
===============================================================


MODBUS DEVICE

      |
      v

ModbusManager

      |
      v

Decoder
      |
      v

Normalizer
      |
      v

Enricher

      |
      v

Measurement

      |
      v

FanoutManager

      |
      +----------------+
      |                |
      v                v

 PostgreSQL       MQTT Broker
      |
      |
      v

 Ignition SCADA
      |
      |
      v

 Operators / Monitoring



===============================================================
                 DESIGN PRINCIPLES
===============================================================


1. Input layer is responsible for data acquisition.

2. Processing layer transforms raw data into domain objects.

3. Fanout layer only distributes measurements.

4. Output managers handle communication channels.

5. RetryManager provides common resilience policy.

6. PersistentStore protects only critical historical data.

7. ErrorStore keeps technical failure history.

8. Watchdog observes system quality but does not control execution.

9. No global orchestrator controls recovery logic.

10. Each component owns its own failure handling.