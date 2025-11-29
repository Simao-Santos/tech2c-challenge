"""
CSV Import Configuration - Single source of truth for CSV headers and mappings
"""

# CSV Header field names (case-sensitive, must match exactly in CSV files)
CSV_HEADERS = {
    'COMPANY': 'Empresa',
    'YEAR': 'Ano',
    'SECTOR': 'Setor',
    'ENERGY_CONSUMPTION': 'Consumo de Energia (MWh)',
    'CO2_EMISSIONS': 'Emissões de CO2 (toneladas)',
}

# Required headers as a set for validation
REQUIRED_HEADERS = set(CSV_HEADERS.values())

# Mapping from CSV columns to model fields
CSV_TO_MODEL_MAPPING = {
    CSV_HEADERS['COMPANY']: 'company',
    CSV_HEADERS['YEAR']: 'year',
    CSV_HEADERS['SECTOR']: 'sector',
    CSV_HEADERS['ENERGY_CONSUMPTION']: 'energy_consumption_mwh',
    CSV_HEADERS['CO2_EMISSIONS']: 'co2_emissions_tons',
}

# Field parsing functions for data type conversion
FIELD_PARSERS = {
    'year': int,
    'energy_consumption_mwh': lambda x: float(x.replace(",", ".")),
    'co2_emissions_tons': lambda x: float(x.replace(",", ".")),
}
