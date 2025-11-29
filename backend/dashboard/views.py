from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
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
            decoded_file = csv_file.read().decode('utf-8-sig')  # utf-8-sig handles BOM
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            created_count = 0
            updated_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                try:
                    # Map CSV columns to model fields
                    company = row.get('Empresa', '').strip()
                    year = row.get('Ano', '').strip()
                    sector = row.get('Setor', '').strip()
                    energy = row.get('Consumo de Energia (MWh)', '').strip()
                    emissions = row.get('Emissões de CO2 (toneladas)', '').strip()
                    
                    # Validate required fields
                    if not all([company, year, sector, energy, emissions]):
                        errors.append(f"Row {row_num}: Missing required fields")
                        continue
                    
                    # Create or update the record
                    record, created = EmissionRecord.objects.update_or_create(
                        company=company,
                        year=int(year),
                        defaults={
                            'sector': sector,
                            'energy_consumption_mwh': float(energy.replace(",", ".")),
                            'co2_emissions_tons': float(emissions.replace(",", ".")),
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                        
                except ValueError as e:
                    errors.append(f"Row {row_num}: Invalid data format - {str(e)}")
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            return Response({
                "message": "CSV import completed",
                "created": created_count,
                "updated": updated_count,
                "errors": errors,
                "total_processed": created_count + updated_count
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to process CSV: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )