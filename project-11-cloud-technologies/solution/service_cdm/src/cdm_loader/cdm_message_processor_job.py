from datetime import datetime
from logging import Logger


class CdmMessageProcessor:
    def __init__(self,
                 consumer,
                 repository,
                 logger: Logger) -> None:

        self._consumer = consumer
        self._repository = repository
        self._logger = logger
        self._batch_size = 100

    def run(self) -> None:
        self._logger.info("=== CDM JOB STARTED ===")

        processed = 0

        for _ in range(self._batch_size):

            msg = self._consumer.consume()
            if msg is None:
                break

            try:
                status = msg.get("status")
                if status and status != "CLOSED":
                    continue

                user_id = msg.get("h_user_pk")
                if not user_id:
                    self._logger.warning(f"Skip message without h_user_pk: {msg}")
                    continue

                products = msg.get("products", [])
                if not products:
                    continue

                self._logger.info(f"Processing order for user={user_id}, products={len(products)}")

                for product in products:

                    product_business_id = product.get("product_id")
                    if not product_business_id:
                        continue

                    product_id = self._repository.get_h_product_pk(product_business_id)
                    if not product_id:
                        continue

                    product_name = self._repository.get_product_name(product_id)
                    category = self._repository.get_category(product_id)

                    if not category:
                        continue

                    category_id, category_name = category

                    self._repository.upsert_user_product(
                        user_id,
                        product_id,
                        product_name
                    )

                    self._repository.upsert_user_category(
                        user_id,
                        category_id,
                        category_name
                    )

                processed += 1

            except Exception as e:
                self._logger.error(f"CDM error: {e}")

        self._logger.info(
            f"{datetime.utcnow()}: CDM FINISH processed={processed}"
        )