from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import EmissionRecord
from .serializers import EmissionRecordSerializer
import csv
import io

class EmissionRecordViewSet(viewsets.ModelViewSet):
    queryset = EmissionRecord.objects.all()
    serializer_class = EmissionRecordSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["company", "sector"]
    ordering_fields = ["year", "energy_consumption_mwh", "co2_emissions_tons"]

    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """
        Import emission records from CSV file
        Expected CSV columns: Empresa, Ano, Setor, Consumo de Energia (MWh), Emissões de CO2 (toneladas)
        """
        csv_file = request.FILES.get('file')
        
        if not csv_file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not csv_file.name.endswith('.csv'):
            return Response(
                {"error": "File must be a CSV"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Read and decode the CSV file
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            # Validate required headers are present
            required_headers = {
                'Empresa', 
                'Ano', 
                'Setor', 
                'Consumo de Energia (MWh)', 
                'Emissões de CO2 (toneladas)'
            }
            
            if not reader.fieldnames:
                return Response(
                    {"error": "CSV file is empty or has no headers"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            actual_headers = set(reader.fieldnames)
            missing_headers = required_headers - actual_headers
            
            if missing_headers:
                return Response(
                    {"error": f"Missing required CSV headers: {', '.join(missing_headers)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Collect records for bulk operations
            records_to_create = []
            records_to_update = []
            existing_records = {}
            errors = []
            
            # Parse all rows first
            parsed_rows = []
            for row_num, row in enumerate(reader, start=2):
                try:
                    company = row.get('Empresa', '').strip()
                    year = row.get('Ano', '').strip()
                    sector = row.get('Setor', '').strip()
                    energy = row.get('Consumo de Energia (MWh)', '').strip()
                    emissions = row.get('Emissões de CO2 (toneladas)', '').strip()
                    
                    # Validate required fields
                    if not all([company, year, sector, energy, emissions]):
                        errors.append(f"Row {row_num}: Missing required fields")
                        continue
                    
                    # Parse and validate data types
                    try:
                        year_int = int(year)
                        energy_float = float(energy.replace(",", "."))
                        emissions_float = float(emissions.replace(",", "."))
                    except ValueError as e:
                        errors.append(f"Row {row_num}: Invalid data format - {str(e)}")
                        continue
                    
                    parsed_rows.append({
                        'company': company,
                        'year': year_int,
                        'sector': sector,
                        'energy_consumption_mwh': energy_float,
                        'co2_emissions_tons': emissions_float,
                        'row_num': row_num
                    })
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            if not parsed_rows:
                return Response(
                    {
                        "error": "No valid rows to process",
                        "errors": errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use transaction for atomicity
            with transaction.atomic():
                # Get existing records for comparison
                company_year_pairs = [(row['company'], row['year']) for row in parsed_rows]
                existing_records_qs = EmissionRecord.objects.filter(
                    company__in=[pair[0] for pair in company_year_pairs],
                    year__in=[pair[1] for pair in company_year_pairs]
                )
                
                # Create a lookup dict for existing records
                for record in existing_records_qs:
                    existing_records[(record.company, record.year)] = record
                
                # Separate into create and update operations
                for row_data in parsed_rows:
                    key = (row_data['company'], row_data['year'])
                    
                    if key in existing_records:
                        # Update existing record
                        existing_record = existing_records[key]
                        existing_record.sector = row_data['sector']
                        existing_record.energy_consumption_mwh = row_data['energy_consumption_mwh']
                        existing_record.co2_emissions_tons = row_data['co2_emissions_tons']
                        records_to_update.append(existing_record)
                    else:
                        # Create new record
                        records_to_create.append(EmissionRecord(
                            company=row_data['company'],
                            year=row_data['year'],
                            sector=row_data['sector'],
                            energy_consumption_mwh=row_data['energy_consumption_mwh'],
                            co2_emissions_tons=row_data['co2_emissions_tons']
                        ))
                
                # Perform bulk operations
                created_count = 0
                updated_count = 0
                
                if records_to_create:
                    EmissionRecord.objects.bulk_create(records_to_create)
                    created_count = len(records_to_create)
                
                if records_to_update:
                    EmissionRecord.objects.bulk_update(
                        records_to_update,
                        ['sector', 'energy_consumption_mwh', 'co2_emissions_tons']
                    )
                    updated_count = len(records_to_update)
            
            return Response({
                "message": "CSV import completed successfully",
                "created": created_count,
                "updated": updated_count,
                "errors": errors,
                "total_processed": created_count + updated_count
            }, status=status.HTTP_201_CREATED if created_count > 0 else status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to process CSV: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )