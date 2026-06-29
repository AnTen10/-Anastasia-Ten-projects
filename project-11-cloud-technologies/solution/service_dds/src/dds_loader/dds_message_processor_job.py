from datetime import datetime
from logging import Logger

from lib.kafka_connect import KafkaConsumer, KafkaProducer
from dds_loader.repository.dds_repository import DdsRepository


class DdsMessageProcessor:
    def __init__(
        self,
        consumer: KafkaConsumer,
        producer: KafkaProducer,
        dds_repository: DdsRepository,
        batch_size: int,
        logger: Logger
    ) -> None:
        self._consumer = consumer
        self._producer = producer
        self._dds_repository = dds_repository
        self._batch_size = batch_size
        self._logger = logger

    def run(self) -> None:
        self._logger.info(f"{datetime.utcnow()}: DDS START")

        processed = 0

        for _ in range(self._batch_size):

            msg = self._consumer.consume()

            self._logger.info(f"RAW KAFKA MSG: {msg}")

            if msg is None:
                break

            try:
                order_id = msg["object_id"]
                payload = msg["payload"]

                # H

                h_order_pk = self._dds_repository.insert_h_order(
                    order_id,
                    payload["date"]
                )

                h_user_pk = self._dds_repository.insert_h_user(
                    payload["user"]["id"]
                )

                h_restaurant_pk = self._dds_repository.insert_h_restaurant(
                    payload["restaurant"]["id"]
                )

                # L

                self._dds_repository.insert_l_order_user(
                    h_order_pk,
                    h_user_pk
                )

                for item in payload.get("products", []):

                    h_product_pk = self._dds_repository.insert_h_product(
                        item["id"]
                    )

                    self._dds_repository.insert_s_product_names(
                        h_product_pk,
                        item["name"]
                    )

                    h_category_pk = self._dds_repository.insert_h_category(
                        item["category"]
                    )

                    self._dds_repository.insert_l_product_category(
                        h_product_pk,
                        h_category_pk
                    )

                    self._dds_repository.insert_l_order_product(
                        h_order_pk,
                        h_product_pk
                    )

                    self._dds_repository.insert_l_product_restaurant(
                        h_product_pk,
                        h_restaurant_pk
                    )

                # S

                self._dds_repository.insert_s_order_cost(
                    h_order_pk,
                    payload["cost"],
                    payload["payment"]
                )

                self._dds_repository.insert_s_order_status(
                    h_order_pk,
                    payload["status"]
                )

                self._dds_repository.insert_s_user_names(
                    h_user_pk,
                    payload["user"]["name"],
                    payload["user"]["id"]
                )

                self._dds_repository.insert_s_restaurant_names(
                    h_restaurant_pk,
                    payload["restaurant"]["name"]
                )

                enriched_msg = {
                    "h_order_pk": str(h_order_pk),
                    "h_user_pk": str(h_user_pk),
                    "h_restaurant_pk": str(h_restaurant_pk),
                    "cost": payload["cost"],
                    "payment": payload["payment"],
                    "status": payload["status"],
                    "products": [
                        {
                            "product_id": item["id"]
                        }
                        for item in payload.get("products", [])
                    ]
                }

                self._logger.info(f"ENRICHED MSG: {enriched_msg}")

                self._producer.produce(enriched_msg)

                self._logger.info(f"SENT TO KAFKA: {enriched_msg}")

                processed += 1

            except Exception as e:
                self._logger.error(f"DDS processing error: {e}")

        self._logger.info(f"{datetime.utcnow()}: DDS FINISH, processed={processed}")