import { useEffect, useState } from 'react';
import { Leaf, Zap, Building2, TrendingUp, AlertCircle } from 'lucide-react';
import { EmissionsByYear } from '@/components/EmissionsByYear';
import { AverageEnergyChart } from '@/components/AverageEnergyChart';
import { TopEmittersChart } from '@/components/TopEmittersChart';
import { EnergyEfficiencyChart } from '@/components/EnergyEfficiencyChart';
import { EmissionsBySectorChart } from '@/components/EmissionsBySectorChart';
import { StatsCard } from '@/components/StatsCard';
import { CSVImport } from '@/components/CSVImport';
import { api, EmissionRecord } from '@/services/api';
import { 
  getTotalEmissionsByYear, 
  getAverageEnergyByCompany, 
  getTopEmitters, 
  getEnergyEfficiency,
  getEmissionsBySector,
  EmissionData
} from '@/utils/emissions';

const Index = () => {
  const [data, setData] = useState<EmissionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const records: EmissionRecord[] = await api.getAllEmissions();
      
      // Transform API data to match your chart format
      const transformedData: EmissionData[] = records.map(record => ({
        empresa: record.company,
        ano: record.year,
        setor: record.sector,
        consumoEnergia: parseFloat(record.energy_consumption_mwh),
        emissoesCO2: parseFloat(record.co2_emissions_tons),
      }));
      
      setData(transformedData);
    } catch (err) {
      console.error('Error loading data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleImportSuccess = () => {
    // Reload data after successful import
    loadData();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-500 mb-4">
            <AlertCircle className="h-12 w-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold mb-2">Failed to Load Data</h2>
          <p className="text-muted-foreground mb-4">{error}</p>
          <button
            onClick={loadData}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const emissionsByYear = getTotalEmissionsByYear(data);
  const averageEnergy = getAverageEnergyByCompany(data);
  const topEmitters = getTopEmitters(data, 5);
  const energyEfficiency = getEnergyEfficiency(data, 10);
  const emissionsBySector = getEmissionsBySector(data);

  const totalEmissions = data.reduce((sum, item) => sum + item.emissoesCO2, 0);
  const totalEnergy = data.reduce((sum, item) => sum + item.consumoEnergia, 0);
  const uniqueCompanies = new Set(data.map(item => item.empresa)).size;
  const avgEmissionsPerCompany = uniqueCompanies > 0 ? totalEmissions / uniqueCompanies : 0;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <Leaf className="h-8 w-8 text-primary" />
                <h1 className="text-4xl font-bold text-foreground">Environmental Dashboard</h1>
              </div>
              <p className="text-muted-foreground text-lg">
                CO₂ Emissions and Energy Consumption Analytics
              </p>
            </div>
            <CSVImport onImportSuccess={handleImportSuccess} />
          </div>
        </header>

        {data.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground mb-4">No data available. Import a CSV file to get started.</p>
          </div>
        ) : (
          <>
            {/* Stats Overview */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
              <StatsCard
                title="Total Emissions"
                value={`${Math.round(totalEmissions).toLocaleString()}`}
                description="tonnes CO₂"
                icon={Leaf}
              />
              <StatsCard
                title="Total Energy"
                value={`${Math.round(totalEnergy).toLocaleString()}`}
                description="MWh consumed"
                icon={Zap}
              />
              <StatsCard
                title="Companies Tracked"
                value={uniqueCompanies}
                description="across all sectors"
                icon={Building2}
              />
              <StatsCard
                title="Avg per Company"
                value={`${Math.round(avgEmissionsPerCompany).toLocaleString()}`}
                description="tonnes CO₂"
                icon={TrendingUp}
              />
            </div>

            {/* Charts Grid */}
            <div className="grid gap-6 lg:grid-cols-2 mb-6">
              <EmissionsByYear data={emissionsByYear} />
              <TopEmittersChart data={topEmitters} />
            </div>

            <div className="grid gap-6 lg:grid-cols-2 mb-6">
              <EnergyEfficiencyChart data={energyEfficiency} />
              <EmissionsBySectorChart data={emissionsBySector} />
            </div>

            <div className="grid gap-6">
              <AverageEnergyChart data={averageEnergy} />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Index;