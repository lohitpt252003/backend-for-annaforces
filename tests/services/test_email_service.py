import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import importlib

# Add the parent directory (backend-for-annaforces) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Direct import of email_service from services
from services import email_service

class TestEmailService(unittest.TestCase):

    def setUp(self):
        # This will be called before each test method
        pass

    def test_email_service_module_exists(self):
        print("\n*************************************************")
        print("*    Test Case 1: Email service module exists   *")
        print("*************************************************")
        # No specific input/output for module existence test
        self.assertTrue(True)

    def test_generate_otp_returns_six_digit_string(self):
        print("\n*************************************************")
        print("*    Test Case 2: Generate OTP                  *")
        print("*************************************************")
        # Input: None
        otp = email_service.generate_otp()
        print(f"Generated OTP: {otp}")
        self.assertIsInstance(otp, str)
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
        print(f"Expected: 6-digit string. Actual: {otp}")

    @patch('services.email_service.Message')
    def test_send_otp_email_success(self, MockMessage):
        print("\n*************************************************")
        print("*    Test Case 3: Send OTP Email (Success)      *")
        print("*************************************************")
        mock_mail = MagicMock()
        recipient = "test@example.com"
        otp = "123456"
        print(f"Input: Recipient={recipient}, OTP={otp}")
        
        success, error = email_service.send_otp_email(mock_mail, recipient, otp)
        
        MockMessage.assert_called_once_with(
            "Your OTP for Annaforces Registration",
            recipients=[recipient]
        )
        mock_mail.send.assert_called_once()
        print(f"Expected: Success=True, Error=None. Actual: Success={success}, Error={error}")
        self.assertTrue(success)
        self.assertIsNone(error)

    @patch('services.email_service.Message')
    def test_send_otp_email_failure(self, MockMessage):
        print("\n*************************************************")
        print("*    Test Case 4: Send OTP Email (Failure)      *")
        print("*************************************************")
        mock_mail = MagicMock()
        mock_mail.send.side_effect = Exception("Mail send failed")
        recipient = "test@example.com"
        otp = "123456"
        print(f"Input: Recipient={recipient}, OTP={otp}")
        
        success, error = email_service.send_otp_email(mock_mail, recipient, otp)
        
        MockMessage.assert_called_once()
        mock_mail.send.assert_called_once()
        print(f"Expected: Success=False, Error containing 'Mail send failed'. Actual: Success={success}, Error={error}")
        self.assertFalse(success)
        self.assertIn("Mail send failed", error)

    @patch('services.email_service.Message')
    def test_send_welcome_email_success(self, MockMessage):
        print("\n*************************************************")
        print("*    Test Case 5: Send Welcome Email (Success)  *")
        print("*************************************************")
        mock_mail = MagicMock()
        recipient = "test@example.com"
        name = "Test User"
        username = "testuser"
        user_id = "U123"
        print(f"Input: Recipient={recipient}, Name={name}, Username={username}, User ID={user_id}")

        success, error = email_service.send_welcome_email(mock_mail, recipient, name, username, user_id)

        MockMessage.assert_called_once_with(
            "Welcome to Annaforces!",
            recipients=[recipient]
        )
        mock_mail.send.assert_called_once()
        print(f"Expected: Success=True, Error=None. Actual: Success={success}, Error={error}")
        self.assertTrue(success)
        self.assertIsNone(error)
        # Further assertions could check msg.html content if needed

    @patch('services.email_service.Message')
    def test_send_password_reset_email_success(self, MockMessage):
        print("\n*************************************************")
        print("*    Test Case 6: Send Password Reset Email (Success) *")
        print("*************************************************")
        mock_mail = MagicMock()
        recipient = "test@example.com"
        name = "Test User"
        otp = "654321"
        print(f"Input: Recipient={recipient}, Name={name}, OTP={otp}")

        success, error = email_service.send_password_reset_email(mock_mail, recipient, name, otp)

        MockMessage.assert_called_once_with(
            "Annaforces Password Reset OTP",
            recipients=[recipient]
        )
        mock_mail.send.assert_called_once()
        print(f"Expected: Success=True, Error=None. Actual: Success={success}, Error={error}")
        self.assertTrue(success)
        self.assertIsNone(error)
        # Further assertions could check msg.html content if needed

    @patch('services.email_service.Message')
    def test_send_userid_reminder_email_success(self, MockMessage):
        print("\n*************************************************")
        print("*    Test Case 7: Send User ID Reminder Email (Success) *")
        print("*************************************************")
        mock_mail = MagicMock()
        recipient = "test@example.com"
        name = "Test User"
        username = "testuser"
        user_id = "U123"
        print(f"Input: Recipient={recipient}, Name={name}, Username={username}, User ID={user_id}")

        success, error = email_service.send_userid_reminder_email(mock_mail, recipient, name, username, user_id)

        MockMessage.assert_called_once_with(
            "Your Annaforces User ID Reminder",
            recipients=[recipient]
        )
        mock_mail.send.assert_called_once()
        print(f"Expected: Success=True, Error=None. Actual: Success={success}, Error={error}")
        self.assertTrue(success)
        self.assertIsNone(error)

    @patch('services.email_service.Message')
    def test_send_userid_reminder_email_failure(self, MockMessage):
        print("\n*************************************************")
        print("*    Test Case 8: Send User ID Reminder Email (Failure) *")
        print("*************************************************")
        mock_mail = MagicMock()
        mock_mail.send.side_effect = Exception("Reminder send failed")
        recipient = "test@example.com"
        name = "Test User"
        username = "testuser"
        user_id = "U123"
        print(f"Input: Recipient={recipient}, Name={name}, Username={username}, User ID={user_id}")

        success, error = email_service.send_userid_reminder_email(mock_mail, recipient, name, username, user_id)

        MockMessage.assert_called_once()
        mock_mail.send.assert_called_once()
        print(f"Expected: Success=False, Error containing 'Reminder send failed'. Actual: Success={success}, Error={error}")
        self.assertFalse(success)
        self.assertIn("Reminder send failed", error)

    @patch('services.email_service.Message')
    def test_send_password_changed_confirmation_email_success(self, MockMessage):
        print("\n*************************************************")
        print("*    Test Case 9: Send Password Changed Confirmation Email (Success) *")
        print("*************************************************")
        mock_mail = MagicMock()
        recipient = "test@example.com"
        name = "Test User"
        print(f"Input: Recipient={recipient}, Name={name}")

        success, error = email_service.send_password_changed_confirmation_email(mock_mail, recipient, name)

        MockMessage.assert_called_once_with(
            "Annaforces Password Changed Confirmation",
            recipients=[recipient]
        )
        mock_mail.send.assert_called_once()
        print(f"Expected: Success=True, Error=None. Actual: Success={success}, Error={error}")
        self.assertTrue(success)
        self.assertIsNone(error)

    @patch('services.email_service.Message')
    def test_send_password_changed_confirmation_email_failure(self, MockMessage):
        print("\n*************************************************")
        print("*    Test Case 10: Send Password Changed Confirmation Email (Failure) *")
        print("*************************************************")
        mock_mail = MagicMock()
        mock_mail.send.side_effect = Exception("Confirmation send failed")
        recipient = "test@example.com"
        name = "Test User"
        print(f"Input: Recipient={recipient}, Name={name}")

        success, error = email_service.send_password_changed_confirmation_email(mock_mail, recipient, name)

        MockMessage.assert_called_once()
        mock_mail.send.assert_called_once()
        print(f"Expected: Success=False, Error containing 'Confirmation send failed'. Actual: Success={success}, Error={error}")
        self.assertFalse(success)
        self.assertIn("Confirmation send failed", error)

if __name__ == '__main__':
    unittest.main()
