class BitBucketIndexerConfig:
    def __init__(self, next_page_url, after, min_forks):
        self.next_page_url = next_page_url
        self.after = after
        self.min_forks = min_forks
