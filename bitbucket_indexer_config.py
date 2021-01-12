class BitBucketIndexerConfig:
    def __init__(self, next_page_url=None, after=None):
        self.next_page_url = next_page_url
        self.after = after
