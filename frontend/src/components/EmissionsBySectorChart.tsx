import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface EmissionsBySectorChartProps {
  data: { sector: string; emissions: number; energy: number }[];
}

export function EmissionsBySectorChart({ data }: EmissionsBySectorChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Emissions by Sector</CardTitle>
        <CardDescription>Total CO₂ emissions and energy consumption by industry sector</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey="sector"
              className="text-muted-foreground text-sm"
              angle={-45}
              textAnchor="end"
              height={100}
            />
            <YAxis 
              className="text-muted-foreground"
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: 'var(--radius)'
              }}
              formatter={(value: number, name: string) => [
                value.toLocaleString(),
                name === 'emissions' ? 'Total CO₂ (tonnes)' : 'Total Energy (MWh)'
              ]}
            />
            <Legend />
            <Bar dataKey="emissions" fill="hsl(var(--chart-1))" radius={[8, 8, 0, 0]} name="Total CO₂" />
            <Bar dataKey="energy" fill="hsl(var(--chart-2))" radius={[8, 8, 0, 0]} name="Total Energy" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
