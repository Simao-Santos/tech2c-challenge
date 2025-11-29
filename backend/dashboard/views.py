from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import EmissionRecord
from .serializers import EmissionRecordSerializer
from .csv_config import REQUIRED_HEADERS, CSV_TO_MODEL_MAPPING, FIELD_PARSERS
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
        Expected CSV columns are defined in csv_config.REQUIRED_HEADERS
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
            
            if not reader.fieldnames:
                return Response(
                    {"error": "CSV file is empty or has no headers"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            actual_headers = set(reader.fieldnames)
            missing_headers = REQUIRED_HEADERS - actual_headers
            
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
            
            # Parse all rows first and handle duplicates within CSV
            parsed_rows = {}  # Use dict to handle duplicates: key = (company, year, sector)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Extract and trim data using configuration mapping
                    row_data = {
                        model_field: row.get(csv_header, '').strip()
                        for csv_header, model_field in CSV_TO_MODEL_MAPPING.items()
                    }
                    
                    # Validate required fields are not empty
                    if not all(row_data.values()):
                        errors.append(f"Row {row_num}: Missing required fields")
                        continue
                    
                    # Parse and validate data types using configured parsers
                    try:
                        parsed_data = {'row_num': row_num}
                        for field, value in row_data.items():
                            if field in FIELD_PARSERS:
                                parsed_data[field] = FIELD_PARSERS[field](value)
                            else:
                                parsed_data[field] = value
                        
                        # Create unique key for this record
                        unique_key = (parsed_data['company'], parsed_data['year'], parsed_data['sector'])
                        
                        # Check for duplicates within the CSV itself
                        if unique_key in parsed_rows:
                            existing_row = parsed_rows[unique_key]
                            # Compare emissions and energy consumption to keep the highest
                            existing_emissions = float(existing_row['co2_emissions_tons'])
                            new_emissions = float(parsed_data['co2_emissions_tons'])
                            existing_energy = float(existing_row['energy_consumption_mwh'])
                            new_energy = float(parsed_data['energy_consumption_mwh'])
                            
                            # Keep the row with highest total impact (emissions + energy)
                            existing_total = existing_emissions + existing_energy
                            new_total = new_emissions + new_energy
                            
                            if new_total > existing_total:
                                replaced_row = existing_row['row_num']
                                errors.append(
                                    f"Row {replaced_row}: Duplicate entry for {parsed_data['company']} "
                                    f"(year {parsed_data['year']}, sector {parsed_data['sector']}). "
                                    f"Keeping row {row_num} with higher emissions/energy values "
                                    f"(new total: {new_total:.2f} vs existing: {existing_total:.2f})"
                                )
                                parsed_rows[unique_key] = parsed_data
                            else:
                                errors.append(
                                    f"Row {row_num}: Duplicate entry for {parsed_data['company']} "
                                    f"(year {parsed_data['year']}, sector {parsed_data['sector']}). "
                                    f"Keeping row {existing_row['row_num']} with higher emissions/energy values "
                                    f"(existing total: {existing_total:.2f} vs new: {new_total:.2f})"
                                )
                        else:
                            parsed_rows[unique_key] = parsed_data
                        
                    except ValueError as e:
                        errors.append(f"Row {row_num}: Invalid data format - {str(e)}")
                        continue
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            # Convert dict to list for further processing
            parsed_rows_list = list(parsed_rows.values())
            
            if not parsed_rows_list:
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
                company_year_sector_tuples = [
                    (row['company'], row['year'], row['sector']) 
                    for row in parsed_rows_list
                ]
                existing_records_qs = EmissionRecord.objects.filter(
                    company__in=[t[0] for t in company_year_sector_tuples],
                    year__in=[t[1] for t in company_year_sector_tuples],
                    sector__in=[t[2] for t in company_year_sector_tuples]
                )
                
                # Create a lookup dict for existing records
                for record in existing_records_qs:
                    existing_records[(record.company, record.year, record.sector)] = record
                
                # Separate into create and update operations
                for row_data in parsed_rows_list:
                    key = (row_data['company'], row_data['year'], row_data['sector'])
                    
                    if key in existing_records:
                        # Update existing record only if values are different
                        existing_record = existing_records[key]
                        needs_update = (
                            float(existing_record.energy_consumption_mwh) != float(row_data['energy_consumption_mwh']) or
                            float(existing_record.co2_emissions_tons) != float(row_data['co2_emissions_tons'])
                        )
                        if needs_update:
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
                        ['energy_consumption_mwh', 'co2_emissions_tons']
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