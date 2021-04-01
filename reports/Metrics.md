# Отчет по заданию 12 (Метрики)

## Prometheus

На стороне приложения реализуем эндпоинт для сбора метрик. Воспользуемся библиотекой `starlette-exporter`, которая
позволяет обернуть метриками все приложение fastapi из коробки:

```python
from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics

app = FastAPI()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)
```

Проверим работоспособность эндпоинта:
![](./images/metrics/raw_metrics.png)

Запустим сервис prometheus с помощью docker:

#### docker-compose

```
  prometheus:
    network_mode: host
    build:
      context: prometheus
      dockerfile: Dockerfile
    container_name: prometheus
    ports:
      - 9090:9090
    command:
      - --config.file=/etc/prometheus/prometheus.yml
```

#### dockerfile

```
FROM prom/prometheus:latest

COPY prometheus.yml /etc/prometheus/prometheus.yml
RUN cd /etc/prometheus && ls -la
```

#### config

```
scrape_configs:
- job_name: messages
  scrape_interval: 5s
  static_configs:
  - targets:
    - localhost:10000
```

(Приложение запускается локально, а не в отдельном контейнере, поэтому используем `network_mode: host`)

Проверим работоспособность:
![](./images/metrics/prometheus.png)

## Grafana

Запустим grafana с помощью docker:

#### docker-compose

```
    grafana:
    network_mode: host
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - 3000:3000
```

Подключим источник данных:

![](./images/metrics/create_data_source.png)

Создадим панели для метрик:

#### Rate

![](./images/metrics/rate_panel.png)

#### Errors

![](./images/metrics/errors_panel.png)

#### Duration

![](./images/metrics/duration_panel.png)

С помощью `wrk` создадим нагрузку и протестируем работу дашборда:

![](./images/metrics/dashboard.png)


## Zabbix
