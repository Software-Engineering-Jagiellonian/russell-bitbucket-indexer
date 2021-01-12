import os
from utils import get_env_var, get_opt_env_var

from fregeindexerlib import RabbitMQConnectionParameters, DatabaseConnectionParameters, IndexerType

from bitbucket_indexer import BitBucketIndexer
from bitbucket_indexer_config import BitBucketIndexerConfig

if __name__ == '__main__':
    rabbit = RabbitMQConnectionParameters(host=get_env_var('RMQ_HOST'),
                                          port=int(get_env_var('RMQ_PORT', default=5672)))

    database = DatabaseConnectionParameters(host=get_env_var('DB_HOST'),
                                            port=int(get_env_var('DB_PORT', default=5432)),
                                            database=get_env_var('DB_DATABASE'),
                                            username=get_env_var('DB_USERNAME'),
                                            password=get_env_var('DB_PASSWORD'))

    bitbucket_config = BitBucketIndexerConfig(next_page_url=get_opt_env_var('NEXT_PAGE_URL'),
                                              after=get_opt_env_var('AFTER'))

    app = BitBucketIndexer(indexer_type=IndexerType.BITBUCKET,
                           rabbitmq_parameters=rabbit, database_parameters=database,
                           rejected_publish_delay=int(get_env_var('RMQ_REJECTED_PUBLISH_DELAY', 10)),
                           config=bitbucket_config)

    app.run()
