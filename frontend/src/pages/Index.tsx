import { useEffect, useState } from 'react';
import { Leaf, Zap, Building2, TrendingUp } from 'lucide-react';
import { EmissionsByYear } from '@/components/EmissionsByYear';
import { AverageEnergyChart } from '@/components/AverageEnergyChart';
import { TopEmittersChart } from '@/components/TopEmittersChart';
import { StatsCard } from '@/components/StatsCard';
import {
  parseCSV,
  getTotalEmissionsByYear,
  getAverageEnergyByCompany,
  getTopEmitters,
  type EmissionData
} from '@/utils/csvParser';

const Index = () => {
  const [data, setData] = useState<EmissionData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/src/data/emissions-data.csv')
      .then(res => res.text())
      .then(text => {
        const parsedData = parseCSV(text);
        setData(parsedData);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error loading data:', error);
        setLoading(false);
      });
  }, []);

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

  const emissionsByYear = getTotalEmissionsByYear(data);
  const averageEnergy = getAverageEnergyByCompany(data);
  const topEmitters = getTopEmitters(data, 5);

  const totalEmissions = data.reduce((sum, item) => sum + item.emissoesCO2, 0);
  const totalEnergy = data.reduce((sum, item) => sum + item.consumoEnergia, 0);
  const uniqueCompanies = new Set(data.map(item => item.empresa)).size;
  const avgEmissionsPerCompany = totalEmissions / uniqueCompanies;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Leaf className="h-8 w-8 text-primary" />
            <h1 className="text-4xl font-bold text-foreground">Environmental Dashboard</h1>
          </div>
          <p className="text-muted-foreground text-lg">
            CO₂ Emissions and Energy Consumption Analytics
          </p>
        </header>

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

        <div className="grid gap-6">
          <AverageEnergyChart data={averageEnergy} />
        </div>
      </div>
    </div>
  );
};

export default Index;
