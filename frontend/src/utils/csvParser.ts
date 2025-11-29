export interface EmissionData {
  empresa: string;
  ano: number;
  setor: string;
  consumoEnergia: number;
  emissoesCO2: number;
}

export function parseCSV(csvText: string): EmissionData[] {
  const lines = csvText.trim().split('\n');
  const data: EmissionData[] = [];
  
  // Skip header
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    // Handle quoted values with commas
    const values = line.match(/(".*?"|[^,]+)(?=\s*,|\s*$)/g)?.map(v => v.replace(/^"|"$/g, ''));
    
    if (values && values.length >= 5) {
      data.push({
        empresa: values[0].trim(),
        ano: parseInt(values[1]),
        setor: values[2].trim(),
        // Replace comma with dot for decimal numbers
        consumoEnergia: parseFloat(values[3].replace(',', '.')),
        emissoesCO2: parseFloat(values[4].replace(',', '.'))
      });
    }
  }
  
  return data;
}

export function getTotalEmissionsByYear(data: EmissionData[]) {
  const yearTotals = new Map<number, number>();
  
  data.forEach(item => {
    const current = yearTotals.get(item.ano) || 0;
    yearTotals.set(item.ano, current + item.emissoesCO2);
  });
  
  return Array.from(yearTotals.entries())
    .map(([year, total]) => ({ year, total: Math.round(total * 100) / 100 }))
    .sort((a, b) => a.year - b.year);
}

export function getAverageEnergyByCompany(data: EmissionData[]) {
  const companyData = new Map<string, { total: number; count: number }>();
  
  data.forEach(item => {
    const current = companyData.get(item.empresa) || { total: 0, count: 0 };
    companyData.set(item.empresa, {
      total: current.total + item.consumoEnergia,
      count: current.count + 1
    });
  });
  
  return Array.from(companyData.entries())
    .map(([company, { total, count }]) => ({
      company,
      average: Math.round((total / count) * 100) / 100
    }))
    .sort((a, b) => b.average - a.average);
}

export function getTopEmitters(data: EmissionData[], limit: number = 5) {
  const companyTotals = new Map<string, number>();
  
  data.forEach(item => {
    const current = companyTotals.get(item.empresa) || 0;
    companyTotals.set(item.empresa, current + item.emissoesCO2);
  });
  
  return Array.from(companyTotals.entries())
    .map(([company, total]) => ({ company, total: Math.round(total * 100) / 100 }))
    .sort((a, b) => b.total - a.total)
    .slice(0, limit);
}
