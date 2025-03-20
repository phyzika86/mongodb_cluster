## Описание Docker Compose для MongoDB Cluster

Этот файл `docker-compose.yml` настраивает кластер MongoDB с использованием Docker. Кластер состоит из нескольких компонентов: конфигурационных серверов, шардов (shards) и маршрутизатора. Давайте разберем, что здесь происходит.

---

### 1. **Конфигурационные серверы**
Конфигурационные серверы хранят информацию о том, как устроен кластер (например, где находятся шарды и как к ним обращаться).

- **Сервисы**: `config1`, `config2`, `config3`.
- **Что делают**: Запускают MongoDB в режиме конфигурационного сервера.
- **Порты**: Каждый сервер слушает на порту `27019`, но на хосте они доступны на разных портах (`27019`, `27020`, `27021`).
- **Логи и конфиги**: 
  - Конфигурационный файл берется из локальной папки `./mongo-config/mongod.conf`.
  - Логи сохраняются в папки `./mongo-logs/config1`, `./mongo-logs/config2`, `./mongo-logs/config3`.

---

### 2. **Шарды (Shards)**
Шарды — это серверы, которые хранят данные. Каждый шард состоит из нескольких реплик (например, `shard1a`, `shard1b`, `shard1c`), чтобы данные не потерялись, если один из серверов упадет.

- **Сервисы**:
  - Шард 1: `shard1a`, `shard1b`, `shard1c`.
  - Шард 2: `shard2a`, `shard2b`, `shard2c`.
  - Шард 3: `shard3a`, `shard3b`, `shard3c`.
- **Что делают**: Запускают MongoDB в режиме шарда.
- **Порты**: Каждый шард слушает на порту `27018`, но на хосте они доступны на разных портах (например, `27018`, `27028`, `27038` и т.д.).
- **Логи и конфиги**:
  - Конфигурационный файл берется из локальной папки `./mongo-config/mongod.conf`.
  - Логи сохраняются в папки `./mongo-logs/shard1a`, `./mongo-logs/shard1b` и т.д.

---

### 3. **Маршрутизатор (Router)**
Маршрутизатор (`mongos`) — это главный компонент, который принимает запросы от клиентов и решает, на какой шард их отправить.

- **Сервис**: `router`.
- **Что делает**: Запускает маршрутизатор и связывает его с конфигурационными серверами.
- **Порты**: Слушает на порту `27017` (стандартный порт MongoDB) и доступен на хосте на том же порту.
- **Логи**: Логи сохраняются в папку `./mongo-logs/router`.
- **Зависимости**: Маршрутизатор ждет, пока запустятся все конфигурационные серверы и шарды.

---

### 4. **Сеть**
Все компоненты кластера общаются через сеть `mongoCluster`. Это изолированная сеть, которая позволяет контейнерам взаимодействовать друг с другом.

---

### 5. **Volumes**
- **Конфигурационные файлы**: Берутся из локальной папки `./mongo-config/mongod.conf`.
- **Логи**: Логи каждого сервиса сохраняются в отдельные папки на хосте (например, `./mongo-logs/config1`, `./mongo-logs/shard1a` и т.д.).

---

### 6. **Как это работает**
1. **Конфигурационные серверы** хранят информацию о том, как устроен кластер.
2. **Шарды** хранят данные и обеспечивают отказоустойчивость за счет репликации.
3. **Маршрутизатор** принимает запросы от клиентов и перенаправляет их на нужные шарды.
4. Все компоненты общаются через сеть `mongoCluster`.

---

### 7. **Как запустить**
Чтобы запустить кластер, выполните команду:
```bash
docker-compose up -d
