import os
import json
import pika
import sys
import time
from bb_crawler import BBCrawler
from db import Database

URL = 'https://api.bitbucket.org/2.0/repositories/?pagelen=100&after=2020-09-01'

DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_DATABASE = os.environ['DB_DATABASE']


def create_message(repo_id, git_url):
    message = {"repo_id": repo_id, "git_url": git_url}
    return json.dumps(message)


def app(rabbitmq_host, rabbitmq_port, queue):
    # Db init
    db = Database(DB_DATABASE, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT)

    # Fetch first set of repositories
    crawler = BBCrawler()
    repos, next_page_url = crawler.fetch_repos(URL)

    while True:
        try:
            print(f"Connecting to RabbitMQ ({rabbitmq_host}:{rabbitmq_port})...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port))
            channel = connection.channel()
            channel.confirm_delivery()
            channel.queue_declare(queue=queue, durable=True)
            print("Connected")

            while repos:
                # Prepare message
                repo = repos.pop()
                message = create_message(repo["repo_id"], repo["git_url"])

                while True:
                    # Send message
                    try:
                        channel.basic_publish(exchange='',
                                              routing_key=queue,
                                              properties=pika.BasicProperties(
                                                  delivery_mode=2,  # make message persistent
                                              ),
                                              body=bytes(message, encoding='utf8'))
                        print("Message was received by RabbitMQ")
                        break
                    except pika.exceptions.NackError:
                        print("Message was REJECTED by RabbitMQ (queue full?) !")
                        time.sleep(5)

                # Save data in db
                db.connect()
                db.publish_entry(repo)
                db.close()

                # Get another set of repositories
                if not repos:
                    repos = crawler.fetch_repos(next_page_url)

        except pika.exceptions.AMQPConnectionError as exception:
            print(f"AMQP Connection Error: {exception}")
        except KeyboardInterrupt:
            print(" Exiting...")
            try:
                connection.close()
            except NameError:
                pass
            sys.exit(0)


if __name__ == '__main__':
    try:
        rabbitmq_host = os.environ['RABBITMQ_HOST']
    except KeyError:
        print("RabbitMQ host must be provided as RABBITMQ_HOST environment var!")
        sys.exit(1)

    try:
        rabbitmq_port = int(os.environ.get('RABBITMQ_PORT', '5672'))
    except ValueError:
        print("RABBITMQ_PORT must be an integer")
        sys.exit(2)

    try:
        queue = os.environ['QUEUE']
    except KeyError:
        print("Destination queue must be provided as QUEUE environment var!")
        sys.exit(3)

    app(rabbitmq_host, rabbitmq_port, queue)
