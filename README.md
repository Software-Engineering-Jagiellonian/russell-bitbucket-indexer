# russell-bitbucket-indexer
Indexer of public repositories from Bitbucket.

Docker image available as `jagiellonian/russell-bitbucket-indexer`.

## Docker environment variables

   * `RMQ_HOST` - RabbitMQ host
   
   * `RMQ_PORT` - RabbitMQ port (optional - default 5672)

   * `DB_HOST` - PostgreSQL server host

   * `DB_PORT` - PostgreSQL server host (optional - default 5432)

   *  `DB_DATABASE` - Database name

   *  `DB_USERNAME` - Database username

   *  `DB_PASSWORD` - Database password
   
   *  `NEXT_PAGE_URL` - Endpoint returning the next repository page (optional)
   *  `AFTER` - Creation date of the repository (`YYYY-MM-DD`) from which the indexer crawl the repositories (optional)
   *  `MIN_FORKS` - Minimal number of stars that repository should have (optional)

When NEXT_PAGE_URL, AFTER and MIN_FORKS are not passed, then given criteria are not taken into consideration during a crawl. More conditions will be added soon.
