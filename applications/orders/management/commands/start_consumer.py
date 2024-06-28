import time

from django.core.management.base import BaseCommand
from django.utils import timezone
from rocketmq.client import ConsumeStatus, PushConsumer

from applications.orders.models import Order


class Command(BaseCommand):
    help = "Start RocketMQ consumer to cancel unpaid orders"

    def handle(self, *args, **options):
        consumer = PushConsumer("CID_order_cancel")
        consumer.set_name_server_address("rocketmq-namesrv:9876")
        consumer.subscribe("OrderCancel", self.callback)
        consumer.start()

        self.stdout.write(self.style.SUCCESS("RocketMQ consumer started"))

        try:
            while True:
                time.sleep(
                    3600
                )  # 让循环每隔一小时运行一次，这里主要是为了保持消费者运行
        except KeyboardInterrupt:
            consumer.shutdown()
            self.stdout.write(self.style.SUCCESS("RocketMQ consumer stopped"))

    def callback(self, msg):
        order_id = int(msg.body.decode("utf-8"))
        try:
            order = Order.objects.get(id=order_id)
            if order.status == 1:
                order.status = 6
                order.cancel_time = timezone.now()
                order.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Order {order_id} canceled successfully")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Order {order_id} already processed")
                )
        except Order.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Order {order_id} does not exist"))

        return ConsumeStatus.CONSUME_SUCCESS
