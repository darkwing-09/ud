import pytest
import hmac
import hashlib
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from app.services.payment import PaymentService
from app.core.exceptions import ValidationError

def test_razorpay_webhook_signature_verification_success():
    """Test valid webhook payload passes signature verification."""
    service = PaymentService(session=AsyncMock())
    
    raw_body = b'{"event":"payment.captured"}'
    secret = "my_super_secret"
    
    # Calculate a valid signature
    valid_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=raw_body,
        digestmod="sha256",
    ).hexdigest()

    # Mock the settings so it reads our custom secret
    with patch("app.services.payment.settings") as mock_settings:
        mock_settings.RAZORPAY_WEBHOOK_SECRET = secret
        
        # Should NOT raise an exception
        service._verify_webhook_signature(raw_body, valid_signature)

def test_razorpay_webhook_signature_verification_failure():
    """Test invalid or tampered payload fails signature verification."""
    service = PaymentService(session=AsyncMock())
    
    raw_body = b'{"event":"payment.captured"}'
    invalid_signature = "a" * 64
    
    with patch("app.services.payment.settings") as mock_settings:
        mock_settings.RAZORPAY_WEBHOOK_SECRET = "my_super_secret"
        
        with pytest.raises(ValidationError, match="Invalid Razorpay webhook signature"):
            service._verify_webhook_signature(raw_body, invalid_signature)

def test_verify_razorpay_signature_hmac():
    """Test signature validation used during order completion verification."""
    service = PaymentService(session=AsyncMock())
    
    order_id = "order_123"
    payment_id = "pay_456"
    secret = "api_secret"
    
    body = f"{order_id}|{payment_id}"
    valid_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=body.encode("utf-8"),
        digestmod="sha256",
    ).hexdigest()
    
    with patch("app.services.payment.settings") as mock_settings:
        mock_settings.RAZORPAY_KEY_SECRET = secret
        
        # Valid signature should pass cleanly
        service._verify_razorpay_signature(order_id, payment_id, valid_signature)
        
        # Invalid should raise
        with pytest.raises(ValidationError, match="Razorpay signature verification failed"):
            service._verify_razorpay_signature(order_id, payment_id, "invalid_sig")
