from aiokafka.helpers import create_ssl_context

from social_network.settings import KafkaSettings, KafkaSSLSettings


class SSLContextFactory:
    PREPARED = False

    def write_files(self, ssl: KafkaSSLSettings):
        mapping = {
            'ca.pem': ssl.CA, 'serv.cert': ssl.CERT, 'serv.key': ssl.KEY
        }

        for key, value in mapping.items():
            with open(key, 'w') as fp:
                fp.write(value.get_secret_value())

        self.PREPARED = True

    def __call__(self, conf: KafkaSettings):
        if not conf.USE_SSL:
            return None

        if not self.PREPARED:
            self.write_files(conf.SSL)

        return create_ssl_context(
            cafile="ca.pem",
            certfile="serv.cert",
            keyfile="serv.key"
        )


prepare_ssl_context = SSLContextFactory()
