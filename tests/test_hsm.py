import unittest
from unittest.mock import patch

from patterns.other.hsm.hsm import (
    Active,
    HierachicalStateMachine,
    Standby,
    Suspect,
    UnsupportedMessageType,
    UnsupportedState,
    UnsupportedTransition,
)


class HsmMethodTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hsm = HierachicalStateMachine()

    def test_initial_state_shall_be_standby(self):
        self.assertEqual(isinstance(self.hsm._current_state, Standby), True)

    def test_unsupported_state_shall_raise_exception(self):
        with self.assertRaises(UnsupportedState):
            self.hsm._next_state("missing")

    def test_unsupported_message_type_shall_raise_exception(self):
        with self.assertRaises(UnsupportedMessageType):
            self.hsm.on_message("trigger")

    def test_calling_next_state_shall_change_current_state(self):
        self.hsm._current_state = Standby
        self.hsm._next_state("active")
        self.assertEqual(isinstance(self.hsm._current_state, Active), True)
        self.hsm._current_state = Standby(self.hsm)

    def test_method_perform_switchover_shall_return_specifically(self):
        """Exemplary HierachicalStateMachine method test.
        (here: _perform_switchover()). Add additional test cases..."""
        return_value = self.hsm._perform_switchover()
        expected_return_value = "perform switchover"
        self.assertEqual(return_value, expected_return_value)


class StandbyStateTest(unittest.TestCase):
    """Exemplary 2nd level state test class (here: Standby state). Add missing
    state test classes..."""

    @classmethod
    def setUpClass(cls):
        cls.hsm = HierachicalStateMachine()

    def setUp(self):
        self.hsm._current_state = Standby(self.hsm)

    def test_given_standby_on_message_switchover_shall_set_active(self):
        self.hsm.on_message("switchover")
        self.assertEqual(isinstance(self.hsm._current_state, Active), True)

    def test_given_standby_on_message_switchover_shall_call_hsm_methods(self):
        with (patch.object(self.hsm, "_perform_switchover") as mock_perform_switchover, patch.object(self.hsm, "_check_mate_status") as mock_check_mate_status, patch.object(self.hsm, "_send_switchover_response") as mock_send_switchover_response, patch.object(self.hsm, "_next_state") as mock_next_state):
            self.hsm.on_message("switchover")
            self.assertEqual(mock_perform_switchover.call_count, 1)
            self.assertEqual(mock_check_mate_status.call_count, 1)
            self.assertEqual(mock_send_switchover_response.call_count, 1)
            self.assertEqual(mock_next_state.call_count, 1)

    def test_given_standby_on_message_fault_trigger_shall_set_suspect(self):
        self.hsm.on_message("fault trigger")
        self.assertEqual(isinstance(self.hsm._current_state, Suspect), True)

    def test_given_standby_on_message_diagnostics_failed_shall_raise_exception_and_keep_in_state(self):
        with self.assertRaises(UnsupportedTransition):
            self.hsm.on_message("diagnostics failed")
        self.assertEqual(isinstance(self.hsm._current_state, Standby), True)

    def test_given_standby_on_message_diagnostics_passed_shall_raise_exception_and_keep_in_state(self):
        with self.assertRaises(UnsupportedTransition):
            self.hsm.on_message("diagnostics passed")
        self.assertEqual(isinstance(self.hsm._current_state, Standby), True)

    def test_given_standby_on_message_operator_inservice_shall_raise_exception_and_keep_in_state(self):
        with self.assertRaises(UnsupportedTransition):
            self.hsm.on_message("operator inservice")
        self.assertEqual(isinstance(self.hsm._current_state, Standby), True)
