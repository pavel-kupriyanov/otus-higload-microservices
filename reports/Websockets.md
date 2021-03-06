# Отчет по заданию 7 (Онлайн обновление ленты новостей)

Больше о новостях - в [предыдущем отчете](Queue.md).

### RabbitMQ

Для обмена сообщениями создается direct exchange.

#### Producer

[Код](../social_network/services/rabbitmq/producer.py)

При добавлении новости json с данными (аналогично добавлению в кеш из предыдущего задания)
отправляется в RabbitMQ, в качестве routing key используется id получателя новости.

#### Consumer

[Код](../social_network/services/rabbitmq/consumer.py)


Когда пользователь заходит на страницу `/feed` приложения устанавливается вебсокет-соединение.
Вебсокет добавляется в [сервис вебсокетов](../social_network/services/ws/service.py) приложения.
В нем вебсокеты хранятся в словаре, где ключ - id пользователя, а значение - массив
вебсокетов (на случай работающих одновременно нескольких вкладок/разных клиентов).
Вебсокет будет закрыт, когда юзер покинет страницу `/feed`.

На время соединения создается консьюмер. В нем создается очередь, привязывающаяся к exchange по 
id пользователя. Когда консьюмер вычитывает сообщение из очереди он отправляет его на все вебсокеты юзера.

Если юзер закрывает последний вебсокет, то консьюмер (и очередь) уничтожается.


#### Масштабируемость

Приложение допускает наращивание инстансов, так как консьюмеры создаются для каждого подключения юзера.
За счет того, что в качестве routing key используется id юзера сообщение попадет только на те инстансы приложения, 
где в данный момент открыто подключение целевого юзера. 

