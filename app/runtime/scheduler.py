from app.logging import logger


class RuntimeScheduler:

    @classmethod
    def initialize(cls):
        logger.info("[*] initialized Runtime Scheduler")

    @classmethod
    def consume_scheduled_query(cls):
        pass

    @classmethod
    def abstract_relational_query(cls):
        pass

    @classmethod
    def publish_to_execution_engine(cls):
        pass
