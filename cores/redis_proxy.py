class AuthRedis:
    def __init__(self, redis):
        self.redis = redis

    def token_exists(self, token):
        self.redis
