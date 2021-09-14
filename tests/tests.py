import os
import time
import unittest
import requests
from uuid import uuid4

API_URL = os.getenv("TIMELINE_API_BASE_URL", "http://localhost:8000")
API_WAIT_MAX_RETRIES = 60


def wait_for_api():
    for i in range(API_WAIT_MAX_RETRIES):
        try:
            resp = requests.get(API_URL + "/")
            if resp.status_code == 200:
                return
        except requests.RequestException:
            pass
        if i < API_WAIT_MAX_RETRIES - 1:
            time.sleep(1)
    raise RuntimeError("wait_for_api failed")


def setUpModule():
    wait_for_api()


def enter(timestamp: int, tracking_id: str, camera_id: str) -> requests.Response:
    data = {
        "event_id": str(uuid4()),
        "timestamp": timestamp,
        "tracking_id": tracking_id,
        "camera_id": camera_id,
    }
    return requests.post(API_URL + "/enter_event", json=data)


def exit(timestamp: int, tracking_id: str, camera_id: str) -> requests.Response:
    data = {
        "event_id": str(uuid4()),
        "timestamp": timestamp,
        "tracking_id": tracking_id,
        "camera_id": camera_id,
    }
    return requests.post(API_URL + "/exit_event", json=data)


class TestApi(unittest.TestCase):
    def setUp(self):
        self.track_id = "test_" + str(uuid4())
        self.start_ts = int(time.time())

    def test_simple(self):
        resp = enter(self.start_ts, self.track_id, camera_id="1")
        self.assertEqual(resp.status_code, 201)
        resp = exit(self.start_ts + 30, self.track_id, camera_id="1")
        self.assertEqual(resp.status_code, 201)

        resp = requests.get(API_URL + f"/timeline/{self.track_id}")
        self.assertEqual(resp.status_code, 200)
        timeline = resp.json()
        self.assertEqual(len(timeline), 1, timeline)
        self.assertDictEqual(
            timeline[0],
            {
                "start_ts": self.start_ts,
                "end_ts": self.start_ts + 30,
                "camera_ids": ["1"],
            },
        )

    def test_not_found(self):
        """
        There are no events for provided tracking ID
        """
        resp = requests.get(API_URL + f"/timeline/{self.track_id}")
        self.assertEqual(resp.status_code, 404)

    def test_empty(self):
        """
        A timeline cannot be constructed because the enter and exit events
        do not have the corresponding exit and enter events
        """
        enter(self.start_ts, self.track_id, camera_id="1")
        exit(self.start_ts + 30, self.track_id, camera_id="2")

        resp = requests.get(API_URL + f"/timeline/{self.track_id}")
        timeline = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(timeline, [])

    def test_gap(self):
        """
        A timeline should not contain entries with empty camera_ids
        when there is a gap in the timeline
        """
        enter(self.start_ts, self.track_id, camera_id="1")
        exit(self.start_ts + 30, self.track_id, camera_id="1")
        enter(self.start_ts + 35, self.track_id, camera_id="2")
        exit(self.start_ts + 50, self.track_id, camera_id="2")

        resp = requests.get(API_URL + f"/timeline/{self.track_id}")
        timeline = resp.json()
        self.assertEqual(len(timeline), 2, timeline)
        self.assertDictEqual(
            timeline[0],
            {
                "start_ts": self.start_ts,
                "end_ts": self.start_ts + 30,
                "camera_ids": ["1"],
            },
        )
        self.assertDictEqual(
            timeline[1],
            {
                "start_ts": self.start_ts + 35,
                "end_ts": self.start_ts + 50,
                "camera_ids": ["2"],
            },
        )

    def test_one_second_overlap(self):
        """
        The person left the field of view of one camera and entered the field
        of view of another camera at the same second
        """
        enter(self.start_ts, self.track_id, camera_id="1")
        exit(self.start_ts + 30, self.track_id, camera_id="1")
        enter(self.start_ts + 30, self.track_id, camera_id="2")
        exit(self.start_ts + 45, self.track_id, camera_id="2")

        resp = requests.get(API_URL + f"/timeline/{self.track_id}")
        timeline = resp.json()
        self.assertEqual(len(timeline), 3, timeline)
        self.assertDictEqual(
            timeline[0],
            {
                "start_ts": self.start_ts,
                "end_ts": self.start_ts + 29,
                "camera_ids": ["1"],
            },
        )
        self.assertDictEqual(
            timeline[1],
            {
                "start_ts": self.start_ts + 30,
                "end_ts": self.start_ts + 30,
                "camera_ids": ["1", "2"],
            },
        )
        self.assertDictEqual(
            timeline[2],
            {
                "start_ts": self.start_ts + 31,
                "end_ts": self.start_ts + 45,
                "camera_ids": ["2"],
            },
        )

    def test_start_and_end_overlap(self):
        """
        The person left and entered the field of view of the same camera
        at the same second. This is the only kind of overlap with the same
        camera_id that can happen if the system functions properly.
        """
        enter(self.start_ts, self.track_id, camera_id="1")
        exit(self.start_ts + 30, self.track_id, camera_id="1")
        enter(self.start_ts + 30, self.track_id, camera_id="1")
        exit(self.start_ts + 45, self.track_id, camera_id="1")

        resp = requests.get(API_URL + f"/timeline/{self.track_id}")
        self.assertEqual(resp.status_code, 200)
        timeline = resp.json()
        self.assertEqual(len(timeline), 1, timeline)
        # The overlapping intervals must be joined
        self.assertDictEqual(
            timeline[0],
            {
                "start_ts": self.start_ts,
                "end_ts": self.start_ts + 45,
                "camera_ids": ["1"],
            },
        )


if __name__ == "__main__":
    unittest.main()
