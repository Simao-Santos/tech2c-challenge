from rest_framework import viewsets, filters
from .models import EmissionRecord
from .serializers import EmissionRecordSerializer

class EmissionRecordViewSet(viewsets.ModelViewSet):
    queryset = EmissionRecord.objects.all()
    serializer_class = EmissionRecordSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["company", "sector"]
    ordering_fields = ["year", "energy_consumption_mwh", "co2_emissions_tons"]
