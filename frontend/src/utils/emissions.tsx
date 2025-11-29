// Type for transformed data
export interface EmissionData {
  empresa: string;
  ano: number;
  setor: string;
  consumoEnergia: number;
  emissoesCO2: number;
}

// Helper functions
export function getTotalEmissionsByYear(data: EmissionData[]) {
  const yearMap = new Map<number, number>();
  data.forEach(item => {
    yearMap.set(item.ano, (yearMap.get(item.ano) || 0) + item.emissoesCO2);
  });
  return Array.from(yearMap.entries())
    .map(([year, emissions]) => ({ year, total: emissions }))
    .sort((a, b) => a.year - b.year);
}

export function getAverageEnergyByCompany(data: EmissionData[]) {
  const companyMap = new Map<string, { total: number; count: number }>();
  data.forEach(item => {
    const current = companyMap.get(item.empresa) || { total: 0, count: 0 };
    companyMap.set(item.empresa, {
      total: current.total + item.consumoEnergia,
      count: current.count + 1,
    });
  });
  return Array.from(companyMap.entries())
    .map(([company, { total, count }]) => ({
      company,
      average: total / count,
    }))
    .sort((a, b) => b.average - a.average);
}

export function getTopEmitters(data: EmissionData[], limit: number) {
  const companyMap = new Map<string, number>();
  data.forEach(item => {
    companyMap.set(item.empresa, (companyMap.get(item.empresa) || 0) + item.emissoesCO2);
  });
  return Array.from(companyMap.entries())
    .map(([company, emissions]) => ({ company, total: emissions }))
    .sort((a, b) => b.total - a.total)
    .slice(0, limit);
}
