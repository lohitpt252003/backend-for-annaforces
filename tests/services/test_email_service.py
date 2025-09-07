import pytest
from unittest.mock import MagicMock, patch
import sys
import os
import importlib.util

import importlib
email_service_module = importlib.import_module("backend-for-annaforces.services.email_service")





def test_email_service_module_exists():
    assert True

def test_generate_otp_returns_six_digit_string():
    otp = email_service_module.generate_otp()
    assert isinstance(otp, str)
    assert len(otp) == 6
    assert otp.isdigit()

@patch('email_service_module.Message')
def test_send_otp_email_success(MockMessage):
    mock_mail = MagicMock()
    recipient = "test@example.com"
    otp = "123456"
    
    success, error = email_service_module.send_otp_email(mock_mail, recipient, otp)
    
    MockMessage.assert_called_once_with(
        "Your OTP for Annaforces Registration",
        recipients=[recipient]
    )
    mock_mail.send.assert_called_once()
    assert success is True
    assert error is None

@patch('email_service_module.Message')
def test_send_otp_email_failure(MockMessage):
    mock_mail = MagicMock()
    mock_mail.send.side_effect = Exception("Mail send failed")
    recipient = "test@example.com"
    otp = "123456"
    
    success, error = email_service_module.send_otp_email(mock_mail, recipient, otp)
    
    MockMessage.assert_called_once()
    mock_mail.send.assert_called_once()
    assert success is False
    assert "Mail send failed" in error

@patch('email_service_module.Message')
def test_send_welcome_email_success(MockMessage):
    mock_mail = MagicMock()
    recipient = "test@example.com"
    name = "Test User"
    username = "testuser"
    user_id = "U123"

    success, error = email_service_module.send_welcome_email(mock_mail, recipient, name, username, user_id)

    MockMessage.assert_called_once_with(
        "Welcome to Annaforces!",
        recipients=[recipient]
    )
    mock_mail.send.assert_called_once()
    assert success is True
    assert error is None
    # Further assertions could check msg.html content if needed

@patch('email_service_module.Message')
def test_send_password_reset_email_success(MockMessage):
    mock_mail = MagicMock()
    recipient = "test@example.com"
    name = "Test User"
    otp = "654321"

    success, error = email_service_module.send_password_reset_email(mock_mail, recipient, name, otp)

    MockMessage.assert_called_once_with(
        "Annaforces Password Reset OTP",
        recipients=[recipient]
    )
    mock_mail.send.assert_called_once()
    assert success is True
    assert error is None
    # Further assertions could check msg.html content if needed

# Add similar tests for send_userid_reminder_email and send_password_changed_confirmation_email
