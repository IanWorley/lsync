# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest

from lftp import LftpJobStatus


class TestLftpJobStatus(unittest.TestCase):
    def test_id(self):
        status = LftpJobStatus(
            job_id=42,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.QUEUED,
            name="",
            flags="",
        )
        self.assertEqual(42, status.id)

    def test_type(self):
        status = LftpJobStatus(
            job_id=-1,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.QUEUED,
            name="",
            flags="",
        )
        self.assertEqual(LftpJobStatus.Type.MIRROR, status.type)
        status = LftpJobStatus(
            job_id=-1,
            job_type=LftpJobStatus.Type.PGET,
            state=LftpJobStatus.State.QUEUED,
            name="",
            flags="",
        )
        self.assertEqual(LftpJobStatus.Type.PGET, status.type)

    def test_state(self):
        status = LftpJobStatus(
            job_id=-1,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.QUEUED,
            name="",
            flags="",
        )
        self.assertEqual(LftpJobStatus.State.QUEUED, status.state)
        status = LftpJobStatus(
            job_id=-1,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.RUNNING,
            name="",
            flags="",
        )
        self.assertEqual(LftpJobStatus.State.RUNNING, status.state)

    def test_name(self):
        status = LftpJobStatus(
            job_id=-1,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.QUEUED,
            name="hello",
            flags="",
        )
        self.assertEqual("hello", status.name)
        status = LftpJobStatus(
            job_id=-1,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.QUEUED,
            name="bye",
            flags="",
        )
        self.assertEqual("bye", status.name)

    def test_total_transfer_state(self):
        status = LftpJobStatus(
            job_id=-1,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.RUNNING,
            name="",
            flags="",
        )
        status.total_transfer_state = LftpJobStatus.TransferState(10, 20, 50, 0, 0)
        self.assertEqual(
            LftpJobStatus.TransferState(10, 20, 50, 0, 0), status.total_transfer_state
        )
        status.total_transfer_state = LftpJobStatus.TransferState(15, 20, 75, 0, 0)
        self.assertEqual(
            LftpJobStatus.TransferState(15, 20, 75, 0, 0), status.total_transfer_state
        )

    def test_total_transfer_state_fails_on_queued(self):
        status = LftpJobStatus(
            job_id=-1,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.QUEUED,
            name="",
            flags="",
        )
        with self.assertRaises(TypeError) as context:
            status.total_transfer_state = LftpJobStatus.TransferState(10, 20, 50, 0, 0)
        self.assertTrue(
            "Cannot set transfer state on job of type queue" in str(context.exception)
        )

    def test_active_transfer_state(self):
        status = LftpJobStatus(
            job_id=-1,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.RUNNING,
            name="",
            flags="",
        )
        status.add_active_file_transfer_state(
            "a", LftpJobStatus.TransferState(10, 20, 50, 0, 0)
        )
        status.add_active_file_transfer_state(
            "b", LftpJobStatus.TransferState(25, 100, 25, 0, 0)
        )
        self.assertEqual(
            {
                ("a", LftpJobStatus.TransferState(10, 20, 50, 0, 0)),
                ("b", LftpJobStatus.TransferState(25, 100, 25, 0, 0)),
            },
            set(status.get_active_file_transfer_states()),
        )

    def test_active_transfer_state_fails_on_queued(self):
        status = LftpJobStatus(
            job_id=-1,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.QUEUED,
            name="",
            flags="",
        )
        with self.assertRaises(TypeError) as context:
            status.add_active_file_transfer_state(
                "filename", LftpJobStatus.TransferState(10, 20, 50, 0, 0)
            )
        self.assertTrue(
            "Cannot set transfer state on job of type queue" in str(context.exception)
        )

    def test_equality_operator(self):
        s1 = LftpJobStatus(
            job_id=3,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.RUNNING,
            name="name",
            flags="flags",
        )
        s1.total_transfer_state = LftpJobStatus.TransferState(10, 20, 50, 1, 2)
        s1.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(1, 2, 3, 4, 5)
        )
        s1.add_active_file_transfer_state(
            "ab", LftpJobStatus.TransferState(6, 7, 8, 9, 0)
        )

        # test equality
        s2 = LftpJobStatus(
            job_id=3,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.RUNNING,
            name="name",
            flags="flags",
        )
        s2.total_transfer_state = LftpJobStatus.TransferState(10, 20, 50, 1, 2)
        s2.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(1, 2, 3, 4, 5)
        )
        s2.add_active_file_transfer_state(
            "ab", LftpJobStatus.TransferState(6, 7, 8, 9, 0)
        )
        self.assertTrue(s1 == s2)

        # test equality - different order of active file transfer state
        s2 = LftpJobStatus(
            job_id=3,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.RUNNING,
            name="name",
            flags="flags",
        )
        s2.total_transfer_state = LftpJobStatus.TransferState(10, 20, 50, 1, 2)
        s2.add_active_file_transfer_state(
            "ab", LftpJobStatus.TransferState(6, 7, 8, 9, 0)
        )
        s2.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(1, 2, 3, 4, 5)
        )
        self.assertTrue(s1 == s2)

        # inequality - job id
        s2 = LftpJobStatus(
            job_id=2,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.RUNNING,
            name="name",
            flags="flags",
        )
        s2.total_transfer_state = LftpJobStatus.TransferState(10, 20, 50, 1, 2)
        s2.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(1, 2, 3, 4, 5)
        )
        s2.add_active_file_transfer_state(
            "ab", LftpJobStatus.TransferState(6, 7, 8, 9, 0)
        )
        self.assertFalse(s1 == s2)

        # inequality - job type
        s2 = LftpJobStatus(
            job_id=3,
            job_type=LftpJobStatus.Type.PGET,
            state=LftpJobStatus.State.RUNNING,
            name="name",
            flags="flags",
        )
        s2.total_transfer_state = LftpJobStatus.TransferState(10, 20, 50, 1, 2)
        s2.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(1, 2, 3, 4, 5)
        )
        s2.add_active_file_transfer_state(
            "ab", LftpJobStatus.TransferState(6, 7, 8, 9, 0)
        )
        self.assertFalse(s1 == s2)

        # inequality - job state
        s1_q = LftpJobStatus(
            job_id=3,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.QUEUED,
            name="name",
            flags="flags",
        )
        s2 = LftpJobStatus(
            job_id=3,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.RUNNING,
            name="name",
            flags="flags",
        )
        self.assertFalse(s1_q == s2)

        # inequality - job total transfer state
        s2 = LftpJobStatus(
            job_id=3,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.RUNNING,
            name="name",
            flags="flags",
        )
        s2.total_transfer_state = LftpJobStatus.TransferState(10, 20, 50, 1, 3)
        s2.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(1, 2, 3, 4, 5)
        )
        s2.add_active_file_transfer_state(
            "ab", LftpJobStatus.TransferState(6, 7, 8, 9, 0)
        )
        self.assertFalse(s1 == s2)

        # inequality - active file transfer state
        s2 = LftpJobStatus(
            job_id=3,
            job_type=LftpJobStatus.Type.MIRROR,
            state=LftpJobStatus.State.RUNNING,
            name="name",
            flags="flags",
        )
        s2.total_transfer_state = LftpJobStatus.TransferState(10, 20, 50, 1, 2)
        s2.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(1, 2, 3, 4, 5)
        )
        s2.add_active_file_transfer_state(
            "ab", LftpJobStatus.TransferState(6, 7, 8, 9, 10)
        )
        self.assertFalse(s1 == s2)
