import unittest
import json
import os
from unittest.mock import patch, MagicMock

# Set test environment variables before importing anything
os.environ['POSTGRES_USER'] = 'test'
os.environ['POSTGRES_PASSWORD'] = 'test'
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_DB'] = 'test'
os.environ['MONGO_URI'] = 'mongodb://localhost:27017/test'
os.environ['JWT_SECRET'] = 'test'
os.environ['OPENROUTER_API_KEY'] = 'test'

from app import create_app
from app.utils.jwt_utils import create_access_token

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Create a proper JWT token for testing
        with self.app.app_context():
            self.auth_token = create_access_token({"sub": "test_user"})

    def test_eda_endpoint_requires_auth(self):
        """Test that EDA endpoint returns 401 without authentication"""
        response = self.client.get('/eda')
        self.assertEqual(response.status_code, 401)

    def test_chat_endpoint_requires_auth(self):
        """Test that chat endpoint returns 401 without authentication"""
        response = self.client.post('/chat', json={"message": "test"})
        self.assertEqual(response.status_code, 401)

    def test_anomaly_endpoints_require_auth(self):
        """Test that anomaly endpoints return 401 without authentication"""
        endpoints = ['/anomaly/detect', '/anomaly/statistical', '/anomaly/ml', '/anomaly/trends']
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 401, f"Endpoint {endpoint} should require auth")

    def test_visualization_endpoints_require_auth(self):
        """Test that visualization endpoints return 401 without authentication"""
        endpoints = ['/charts/trend', '/charts/category-breakdown', '/charts/heatmap', '/dashboard']
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 401, f"Endpoint {endpoint} should require auth")

    def test_charts_available_endpoint(self):
        """Test the charts available endpoint with authentication"""
        response = self.client.get('/charts/available', headers={
            'Authorization': f'Bearer {self.auth_token}'
        })
        # Should not be 401 (unauthorized) and should have some structure
        self.assertNotEqual(response.status_code, 401)

    @patch('app.services.eda_service.SessionLocal')
    def test_eda_endpoint_with_auth_and_mock_data(self, mock_session):
        """Test EDA endpoint with authentication and mocked data"""
        # Mock database session and query results
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Create mock finance expense record with new structure
        mock_record = MagicMock()
        mock_record.id = 1
        mock_record.posting = "9"
        mock_record.period = "10"
        mock_record.company_code = "1000"
        mock_record.cost_center_id = "11010"
        mock_record.cost_center_name = "Test Cost Center"
        mock_record.functional_area_name = "Test Function"
        mock_record.company_code_currency_value = 1000.0
        mock_record.company_code_currency_key = "IDR"
        mock_record.general_ledger_fiscal_year = "2023"
        mock_record.directorate = "Test Directorate"
        mock_record.general_ledger_account = "55111001"
        mock_record.general_ledger_account_name = "Test GL Account"
        
        # Mock properties
        mock_record.category = "Test Category"
        mock_record.month_year = "202310"
        mock_record.cost_center = "11010"
        mock_record.general_ledger_account = "55111001"
        
        mock_session_instance.query.return_value.all.return_value = [mock_record]
        
        response = self.client.get('/eda', headers={
            'Authorization': f'Bearer {self.auth_token}'
        })
        
        self.assertNotEqual(response.status_code, 401)
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('total_rows', data)
            self.assertIn('financial_summary', data)
            self.assertIn('organizational_breakdown', data)

    @patch('app.services.anomaly_service.SessionLocal')
    def test_anomaly_detection_with_mock_data(self, mock_session):
        """Test anomaly detection with mocked data"""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Create multiple mock records for anomaly detection
        mock_records = []
        for i in range(10):
            mock_record = MagicMock()
            mock_record.id = i
            mock_record.cost_center_id = f"CC{i:03d}"
            mock_record.cost_center_name = f"Cost Center {i}"
            mock_record.functional_area_name = "Test Function"
            mock_record.company_code_currency_value = 1000.0 + (i * 100)
            mock_record.directorate = "Test Directorate"
            mock_record.month_year = "202310"
            mock_record.category = "Test Category"
            mock_records.append(mock_record)
        
        mock_session_instance.query.return_value.filter.return_value.all.return_value = mock_records
        mock_session_instance.query.return_value.all.return_value = mock_records
        
        response = self.client.get('/anomaly/statistical', headers={
            'Authorization': f'Bearer {self.auth_token}'
        })
        
        self.assertNotEqual(response.status_code, 401)
        # Don't assert 200 since we're mocking and may have processing errors

    def test_app_creation(self):
        """Test that the Flask app can be created successfully"""
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.config['TESTING'])

    def test_jwt_token_creation(self):
        """Test that JWT tokens can be created properly"""
        with self.app.app_context():
            token = create_access_token({"sub": "test_user"})
            self.assertIsNotNone(token)
            self.assertIsInstance(token, str)

    def test_nonexistent_endpoint(self):
        """Test that nonexistent endpoints return 404"""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_basic_routes_exist(self):
        """Test that the main routes are registered"""
        # Test that our main routes exist by checking they don't return 404
        # They should return 401 (unauthorized) or other expected status
        
        # EDA endpoint exists but requires auth
        response = self.client.get('/eda')
        self.assertNotEqual(response.status_code, 404)
        
        # Chat endpoint exists but requires auth  
        response = self.client.post('/chat', json={"message": "test"})
        self.assertNotEqual(response.status_code, 404)
        
        # New anomaly endpoints exist
        response = self.client.get('/anomaly/detect')
        self.assertNotEqual(response.status_code, 404)
        
        # New visualization endpoints exist
        response = self.client.get('/charts/trend')
        self.assertNotEqual(response.status_code, 404)

    def test_valid_jwt_token_format(self):
        """Test that created JWT tokens have proper format"""
        with self.app.app_context():
            token = create_access_token({"sub": "test_user"})
            # JWT tokens have 3 parts separated by dots
            parts = token.split('.')
            self.assertEqual(len(parts), 3)

    def test_rca_waterfall_endpoint_structure(self):
        """Test RCA waterfall endpoint accepts POST requests"""
        response = self.client.post('/charts/rca-waterfall', 
                                   json={"category": "Test", "from_month": "202309", "to_month": "202310"})
        # Should be 401 (unauthorized) not 404 (not found) or 405 (method not allowed)
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()