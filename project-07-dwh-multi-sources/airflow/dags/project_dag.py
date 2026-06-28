import logging
import pendulum
from datetime import timedelta

from airflow.decorators import dag, task
from airflow.models.variable import Variable
from airflow.operators.python import get_current_context

from lib import ConnectionBuilder

# STG
from examples.project.restaurants_reader import RestaurantsReader
from examples.project.restaurants_loader import RestaurantsLoader
from examples.project.courier_reader import CourierReader
from examples.project.delivery_reader import DeliveryReader
from examples.project.api_saver import ApiSaver
from examples.project.courier_loader import CourierLoader
from examples.project.delivery_loader import DeliveryLoader

# DDS
from examples.project.dm_couriers_reader import DmCouriersReader
from examples.project.dm_couriers_saver import DmCouriersSaver
from examples.project.dm_couriers_loader import DmCouriersLoader
from examples.project.fct_deliveries import FctDeliveries

# CDM
from examples.project.dm_courier_ledger_loader import DmCourierLedgerLoader


log = logging.getLogger(__name__)


@dag(
    schedule_interval='0 2 * * *',
    start_date=pendulum.datetime(2026, 2, 15, tz="UTC"),
    catchup=False,
    tags=['project', 'dag'],
    is_paused_upon_creation=True
)
def project_dag():

    dwh_pg_connect = ConnectionBuilder.pg_conn("PG_WAREHOUSE_CONNECTION")

    base_url = Variable.get("COURIER_API_BASE_URL")
    nickname = Variable.get("COURIER_API_NICKNAME")
    cohort = Variable.get("COURIER_API_COHORT")
    api_key = Variable.get("COURIER_API_KEY")

    @task
    def load_restaurants():
        saver = ApiSaver("stg.api_restaurants")
        reader = RestaurantsReader(base_url, nickname, cohort, api_key)
        loader = RestaurantsLoader(reader, dwh_pg_connect, saver, log)
        loader.load()

    @task
    def load_couriers():
        saver = ApiSaver("stg.api_couriers")

        reader = CourierReader(
            base_url=base_url,
            nickname=nickname,
            cohort=cohort,
            api_key=api_key,
            limit=50,
            sort_field="_id",
            sort_direction="asc"
        )

        loader = CourierLoader(reader, dwh_pg_connect, saver, log)
        loader.load()

    @task
    def load_deliveries():
        context = get_current_context()
        execution_date = context["logical_date"]

        date_to = execution_date
        date_from = date_to - timedelta(days=7)

        saver = ApiSaver("stg.api_deliveries")

        reader = DeliveryReader(
            base_url=base_url,
            nickname=nickname,
            cohort=cohort,
            api_key=api_key,
            date_from=date_from.strftime("%Y-%m-%d %H:%M:%S"),
            date_to=date_to.strftime("%Y-%m-%d %H:%M:%S"),
        )

        loader = DeliveryLoader(reader, dwh_pg_connect, saver, log)
        loader.load()

    @task
    def load_dm_couriers():
        reader = DmCouriersReader(dwh_pg_connect)
        saver = DmCouriersSaver()
        loader = DmCouriersLoader(reader, saver, dwh_pg_connect, log)
        loader.load()

    @task
    def load_fct_deliveries():
        saver = FctDeliveries()

        with dwh_pg_connect.connection() as conn:
            saver.deliveries(conn)

    @task
    def load_dm_courier_ledger():
        loader = DmCourierLedgerLoader(pg_dest=dwh_pg_connect, log=log)
        loader.load_courier_ledger()

    restaurants = load_restaurants()
    couriers = load_couriers()
    deliveries = load_deliveries()

    dm_couriers = load_dm_couriers()
    fct_deliveries = load_fct_deliveries()

    ledger = load_dm_courier_ledger()

    restaurants >> couriers >> deliveries >> dm_couriers >> fct_deliveries >> ledger


project_dag = project_dag()
