FROM rabbitmq:3.8.9-management

# Update and clean apt cache
RUN apt-get clean && apt-get update --fix-missing && \
# Install utils \
apt install -y nano ssh inetutils-ping net-tools htop telnet curl ncdu rsync whois dnsutils git zip wget;

# Copy configs
COPY rabbitmqadmin.conf /var/lib/rabbitmq/.rabbitmqadmin.conf
COPY enabled_plugins /etc/rabbitmq/enabled_plugins
COPY rabbitmq.conf /etc/rabbitmq/rabbitmq.conf

# Fix permissions
RUN chown rabbitmq: /etc/rabbitmq/enabled_plugins /etc/rabbitmq/rabbitmq.conf
RUN cd /etc/rabbitmq && ls -la
