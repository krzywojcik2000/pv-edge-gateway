from queue import Queue


from edge_gateway.input.modbus_client import ModbusClient
from edge_gateway.input.modbus_manager import ModbusManager


from edge_gateway.processing.processing_pipeline import ProcessingPipeline


from edge_gateway.distribution.fanout_manager import FanoutManager


from edge_gateway.output.database.db_runtime import DBRuntime
from edge_gateway.output.database.database_writer import DatabaseWriter

from edge_gateway.output.database.raw_manager import RawDataManager
from edge_gateway.output.database.aggregation_manager import AggregationManager
from edge_gateway.output.database.business_manager import BusinessManager
from edge_gateway.output.database.alarm_manager import AlarmManager


from edge_gateway.output.mqtt.mqtt_manager import MQTTManager
from edge_gateway.output.mqtt.mqtt_publisher import MQTTPublisher


from edge_gateway.output.opcua.opcua_manager import OPCUAManager
from edge_gateway.output.opcua.opcua_server import OPCUAServer


from edge_gateway.resilience.retry_manager import RetryManager
from edge_gateway.resilience.persistent_store import PersistentStore
from edge_gateway.resilience.error_store import ErrorStore


from edge_gateway.runtime.cycle_executor import CycleExecutor
from edge_gateway.runtime.lifecycle import Lifecycle



class Application:


    def __init__(self, config):

        self.config = config

        self.runtime = None



    def build(self):


        # =====================================================
        # RESILIENCE
        # =====================================================

        error_store = ErrorStore()

        persistent_store = PersistentStore()


        retry_manager = RetryManager(
            error_store=error_store
        )



        # =====================================================
        # INPUT
        # =====================================================

        modbus_client = ModbusClient(
            self.config["modbus"]
        )


        modbus_manager = ModbusManager(
            modbus_client,
            retry_manager
        )



        # =====================================================
        # PROCESSING
        # =====================================================

        processing = ProcessingPipeline()



        # =====================================================
        # QUEUES
        # =====================================================

        db_queue = Queue(500)

        mqtt_queue = Queue(500)

        opcua_queue = Queue(500)



        # =====================================================
        # DATABASE
        # =====================================================


        db_writer = DatabaseWriter(
            self.config["database"]
        )


        raw_manager = RawDataManager(
            db_writer
        )


        aggregation_manager = AggregationManager(
            db_writer
        )


        business_manager = BusinessManager(
            db_writer
        )


        alarm_manager = AlarmManager(
            db_writer
        )



        db_runtime = DBRuntime(

            db_writer=db_writer,

            raw_manager=raw_manager,

            aggregation_manager=aggregation_manager,

            business_manager=business_manager,

            alarm_manager=alarm_manager,

            retry_manager=retry_manager,

            persistent_store=persistent_store,

            error_store=error_store
        )



        # =====================================================
        # MQTT
        # =====================================================


        mqtt_publisher = MQTTPublisher(

            host=self.config["mqtt"]["host"],

            port=self.config["mqtt"]["port"]
        )


        mqtt_manager = MQTTManager(

            queue=mqtt_queue,

            publisher=mqtt_publisher,

            farm_id=self.config["farm_id"],

            retry_manager=retry_manager
        )



        # =====================================================
        # OPC UA
        # =====================================================


        opcua_server = OPCUAServer(

            endpoint=self.config["opcua"]["endpoint"]
        )


        opcua_manager = OPCUAManager(

            queue=opcua_queue,

            opcua_server=opcua_server,

            retry_manager=retry_manager
        )



        # =====================================================
        # FANOUT
        # =====================================================


        fanout = FanoutManager(

            db_queue=db_queue,

            mqtt_queue=mqtt_queue,

            opcua_queue=opcua_queue,

            persistent_store=persistent_store,

            error_store=error_store
        )



        # =====================================================
        # CYCLE EXECUTOR
        # =====================================================


        cycle_executor = CycleExecutor(

            modbus_manager=modbus_manager,

            processing=processing,

            fanout=fanout,

            error_store=error_store,

            interval=1.0
        )



        # =====================================================
        # LIFECYCLE
        # =====================================================


        self.runtime = Lifecycle(

            cycle_executor,

            db_runtime,

            mqtt_manager,

            opcua_manager
        )


        return self



    def run(self):

        if self.runtime is None:

            raise RuntimeError(
                "Application not built"
            )


        self.runtime.start()