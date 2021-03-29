FROM wurstmeister/kafka

RUN whoami

# Update apk
RUN apk update && \
# Install utils \
apk add --no-cache nano;

# Copy configs
COPY kafka_server_jaas.conf /etc/kafka/kafka_server_jaas.conf
RUN cd /etc/kafka && ls -la
