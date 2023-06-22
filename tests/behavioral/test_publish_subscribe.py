import unittest
from unittest.mock import call, patch

from patterns.behavioral.publish_subscribe import Provider, Publisher, Subscriber


class TestProvider(unittest.TestCase):
    """
    Integration tests ~ provider class with as little mocking as possible.
    """

    def test_subscriber_shall_be_attachable_to_subscriptions(self):
        subscription = "sub msg"
        pro = Provider()
        self.assertEqual(len(pro.subscribers), 0)
        sub = Subscriber("sub name", pro)
        sub.subscribe(subscription)
        self.assertEqual(len(pro.subscribers[subscription]), 1)

    def test_subscriber_shall_be_detachable_from_subscriptions(self):
        subscription = "sub msg"
        pro = Provider()
        sub = Subscriber("sub name", pro)
        sub.subscribe(subscription)
        self.assertEqual(len(pro.subscribers[subscription]), 1)
        sub.unsubscribe(subscription)
        self.assertEqual(len(pro.subscribers[subscription]), 0)

    def test_publisher_shall_append_subscription_message_to_queue(self):
        """msg_queue ~ Provider.notify(msg) ~ Publisher.publish(msg)"""
        expected_msg = "expected msg"
        pro = Provider()
        pub = Publisher(pro)
        Subscriber("sub name", pro)
        self.assertEqual(len(pro.msg_queue), 0)
        pub.publish(expected_msg)
        self.assertEqual(len(pro.msg_queue), 1)
        self.assertEqual(pro.msg_queue[0], expected_msg)

    def test_provider_shall_update_affected_subscribers_with_published_subscription(self):
        pro = Provider()
        pub = Publisher(pro)
        sub1 = Subscriber("sub 1 name", pro)
        sub1.subscribe("sub 1 msg 1")
        sub1.subscribe("sub 1 msg 2")
        sub2 = Subscriber("sub 2 name", pro)
        sub2.subscribe("sub 2 msg 1")
        sub2.subscribe("sub 2 msg 2")
        with (patch.object(sub1, "run") as mock_subscriber1_run, patch.object(
                sub2, "run"
            ) as mock_subscriber2_run):
            pro.update()
            self.assertEqual(mock_subscriber1_run.call_count, 0)
            self.assertEqual(mock_subscriber2_run.call_count, 0)
        pub.publish("sub 1 msg 1")
        pub.publish("sub 1 msg 2")
        pub.publish("sub 2 msg 1")
        pub.publish("sub 2 msg 2")
        with patch.object(sub1, "run") as mock_subscriber1_run, patch.object(
            sub2, "run"
        ) as mock_subscriber2_run:
            pro.update()
            expected_sub1_calls = [call("sub 1 msg 1"), call("sub 1 msg 2")]
            mock_subscriber1_run.assert_has_calls(expected_sub1_calls)
            expected_sub2_calls = [call("sub 2 msg 1"), call("sub 2 msg 2")]
            mock_subscriber2_run.assert_has_calls(expected_sub2_calls)
