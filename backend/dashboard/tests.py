from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import EmissionRecord
from .csv_config import CSV_HEADERS


class CSVUploadTestCase(TestCase):
    """Test cases for CSV upload functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.upload_url = '/api/emissions/import_csv/'
        # Use headers from configuration
        self.headers = [
            CSV_HEADERS['COMPANY'],
            CSV_HEADERS['YEAR'],
            CSV_HEADERS['SECTOR'],
            CSV_HEADERS['ENERGY_CONSUMPTION'],
            CSV_HEADERS['CO2_EMISSIONS'],
        ]
        self.csv_header_line = ','.join(self.headers)
        
    def create_csv_file(self, csv_content, filename='test.csv'):
        """Helper method to create a CSV file from string content"""
        csv_bytes = csv_content.encode('utf-8')
        return SimpleUploadedFile(
            filename,
            csv_bytes,
            content_type='text/csv'
        )

    # ========== SUCCESS CASES ==========

    def test_successful_csv_upload_creates_records(self):
        """Test that a valid CSV file successfully creates new records"""
        csv_content = f"""{self.csv_header_line}
Company A,2023,Energy,1000.50,500.25
Company B,2023,Manufacturing,2000.75,1000.50"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created'], 2)
        self.assertEqual(response.data['updated'], 0)
        self.assertEqual(response.data['total_processed'], 2)
        self.assertEqual(EmissionRecord.objects.count(), 2)
        
    def test_successful_csv_upload_updates_existing_records(self):
        """Test that a CSV file updates existing records with same company/year/sector"""
        # Create initial record
        EmissionRecord.objects.create(
            company='Company A',
            year=2023,
            sector='Energy',
            energy_consumption_mwh=1000,
            co2_emissions_tons=500
        )
        
        # Upload CSV with same company, year AND sector but different values
        csv_content = f"""{self.csv_header_line}
Company A,2023,Energy,2500.00,750.00"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created'], 0)
        self.assertEqual(response.data['updated'], 1)
        self.assertEqual(EmissionRecord.objects.count(), 1)
        
        # Verify the record was updated
        record = EmissionRecord.objects.get(company='Company A', year=2023, sector='Energy')
        self.assertEqual(float(record.energy_consumption_mwh), 2500.00)
        self.assertEqual(float(record.co2_emissions_tons), 750.00)

    def test_successful_csv_upload_mixed_create_and_update(self):
        """Test that CSV can both create new records and update existing ones"""
        # Create one existing record
        EmissionRecord.objects.create(
            company='Company A',
            year=2023,
            sector='Energy',
            energy_consumption_mwh=1000,
            co2_emissions_tons=500
        )
        
        csv_content = f"""{self.csv_header_line}
Company A,2023,Energy,2500.00,750.00
Company B,2023,Energy,3000.00,1500.00"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created'], 1)
        self.assertEqual(response.data['updated'], 1)
        self.assertEqual(response.data['total_processed'], 2)
        self.assertEqual(EmissionRecord.objects.count(), 2)

    def test_csv_duplicate_rows_keeps_highest_emissions(self):
        """Test that duplicate rows in CSV keep the one with highest emissions/energy"""
        csv_content = f"""{self.csv_header_line}
Company A,2023,Energy,1000.00,500.00
Company A,2023,Energy,2000.00,800.00"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        # Should succeed with 1 created record and 1 conflict logged
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created'], 1)
        self.assertEqual(response.data['updated'], 0)
        self.assertEqual(EmissionRecord.objects.count(), 1)
        
        # Verify the kept record is the one with higher values
        record = EmissionRecord.objects.get(company='Company A', year=2023, sector='Energy')
        self.assertEqual(float(record.energy_consumption_mwh), 2000.00)
        self.assertEqual(float(record.co2_emissions_tons), 800.00)
        
        # Verify conflict was logged
        self.assertEqual(len(response.data['errors']), 1)
        self.assertIn('Duplicate entry', response.data['errors'][0])
        self.assertIn('higher emissions/energy values', response.data['errors'][0])

    def test_csv_duplicate_rows_keeps_first_on_equal_totals(self):
        """Test that duplicate rows with equal totals keep the first one"""
        csv_content = f"""{self.csv_header_line}
Company A,2023,Energy,1000.00,500.00
Company A,2023,Energy,500.00,1000.00"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        # Should succeed with 1 created record and 1 conflict logged
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created'], 1)
        self.assertEqual(EmissionRecord.objects.count(), 1)
        
        # Both have same total (1500) but first one should be kept
        record = EmissionRecord.objects.get(company='Company A', year=2023, sector='Energy')
        self.assertEqual(float(record.energy_consumption_mwh), 1000.00)
        self.assertEqual(float(record.co2_emissions_tons), 500.00)

    # ========== ERROR CASES ==========

    def test_empty_csv_file(self):
        """Test that empty CSV file is rejected"""
        csv_content = ""
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('empty', response.data['error'].lower())

    def test_csv_with_only_headers(self):
        """Test that CSV with only headers and no data rows is rejected"""
        csv_content = self.csv_header_line
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No valid rows', response.data['error'])

    def test_missing_multiple_headers(self):
        """Test that error message lists all missing headers"""
        csv_content = """Empresa,Ano
Company A,2023"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required CSV headers', response.data['error'])
        # Should list multiple missing headers
        missing_count = response.data['error'].count(',')
        self.assertGreater(missing_count, 0)

    def test_incorrect_header_names(self):
        """Test that CSV with wrong header names is rejected"""
        csv_content = """Company,Year,Industry,Energy Usage,CO2 Output
Company A,2023,Energy,1000.50,500.25"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required CSV headers', response.data['error'])

    def test_missing_required_field_empresa(self):
        """Test that row with missing Empresa field is skipped with error"""
        csv_content = f"""{self.csv_header_line}
,2023,Energy,1000.50,500.25"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No valid rows', response.data['error'])
        self.assertEqual(len(response.data['errors']), 1)
        self.assertIn('Row 2', response.data['errors'][0])
        self.assertIn('Missing required fields', response.data['errors'][0])

    def test_invalid_year_format(self):
        """Test that non-integer year values cause an error for that row"""
        csv_content = f"""{self.csv_header_line}
Company A,2023abc,Energy,1000.50,500.25"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No valid rows', response.data['error'])
        self.assertEqual(len(response.data['errors']), 1)
        self.assertIn('Invalid data format', response.data['errors'][0])

    def test_invalid_energy_format(self):
        """Test that non-numeric energy values cause an error for that row"""
        csv_content = f"""{self.csv_header_line}
Company A,2023,Energy,invalid,500.25"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data['errors']), 1)
        self.assertIn('Invalid data format', response.data['errors'][0])

    def test_invalid_emissions_format(self):
        """Test that non-numeric emissions values cause an error for that row"""
        csv_content = f"""{self.csv_header_line}
Company A,2023,Energy,1000.50,not_a_number"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data['errors']), 1)
        self.assertIn('Invalid data format', response.data['errors'][0])

    def test_invalid_data_types_multiple_rows(self):
        """Test handling of multiple rows with invalid data types"""
        csv_content = f"""{self.csv_header_line}
Company A,2023abc,Energy,1000.50,500.25
Company B,2023,Manufacturing,invalid,1000.50
Company C,2023,Services,2000.50,500.25"""
        
        file = self.create_csv_file(csv_content)
        response = self.client.post(self.upload_url, {'file': file})
        
        # Should succeed with 1 valid row and 2 errors
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created'], 1)
        self.assertEqual(len(response.data['errors']), 2)
        self.assertEqual(EmissionRecord.objects.count(), 1)
