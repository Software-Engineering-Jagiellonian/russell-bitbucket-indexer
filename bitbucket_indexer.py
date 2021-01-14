
import requests

from fregeindexerlib import Indexer, CrawlResult, RabbitMQConnectionParameters, IndexerType, \
    DatabaseConnectionParameters, IndexerError

from bitbucket_indexer_config import BitBucketIndexerConfig


class BitBucketIndexer(Indexer):
    BASE_API_URL = 'https://api.bitbucket.org/2.0/repositories/'

    def __init__(self, indexer_type: IndexerType, rabbitmq_parameters: RabbitMQConnectionParameters,
                 database_parameters: DatabaseConnectionParameters, rejected_publish_delay: int,
                 config: BitBucketIndexerConfig):
        super().__init__(indexer_type, rabbitmq_parameters, database_parameters, rejected_publish_delay)
        self.after = config.after
        self.min_forks = config.min_forks
        self.next_page_url = config.next_page_url if config.next_page_url else self.BASE_API_URL

    def crawl_next_repository(self, prev_repository_id):
        params = {
            'pagelen': 1,
            'after': self.after
        }

        while True:
            self.log.debug('Start a new crawl')

            if not self.next_page_url:
                return None

            response = requests.get(self.next_page_url, params=params)
            self.handle_repositories_response(response)

            json_response = response.json()
            if len(json_response['values']) < 1:
                return None

            repository_data = json_response['values'][0]

            if self.min_forks:
                self.log.debug('Test repository forks')

                forks_url = repository_data['links']['forks']['href']
                forks_count = self.get_forks_count(forks_url)
                if forks_count < self.min_forks:
                    self.reject_repository('Repository rejected due to too small number of forks',
                                           json_response.get('next', None))
                    continue

            repository_id = repository_data['uuid']
            repo_url = repository_data['links']['html']['href']
            git_url = repository_data['links']['clone'][0]['href']
            self.log.info(f'Tested repository id: {repository_id} ({repo_url})')

            # Bitbucket API returns only main programming language in the repository
            crawled_repository = CrawlResult(
                id=str(repository_id),
                repo_url=repo_url,
                git_url=git_url,
                languages=None
            )

            self.log.info(f'Repository accepted: {crawled_repository}')

            # Get the next page url, if present
            self.next_page_url = json_response.get('next', None)

            return crawled_repository

    def get_forks_count(self, url):
        params = {
            'pagelen': self.min_forks,
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            return 0

        json_response = response.json()

        return json_response.get('size', 0)

    def reject_repository(self, message, next_url):
        self.log.info(message)
        self.next_page_url = next_url

    @staticmethod
    def handle_repositories_response(response):
        if response.status_code != 200:
            raise IndexerError('Response code other than 200!', 'Response: ' + response.text)



