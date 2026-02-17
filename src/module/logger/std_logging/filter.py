import logging


class ContextFilter(logging.Filter):
    UNACCEPTABLE_WORDS = ['password', 'token']

    def filter(self, record):
        return not any(word in record.getMessage().lower()
                       for word in self.UNACCEPTABLE_WORDS)
