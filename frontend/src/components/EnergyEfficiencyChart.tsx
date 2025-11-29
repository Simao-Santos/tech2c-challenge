import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface EnergyEfficiencyChartProps {
  data: { company: string; efficiency: number }[];
}

export function EnergyEfficiencyChart({ data }: EnergyEfficiencyChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Energy Efficiency Ratio</CardTitle>
        <CardDescription>Top 10 companies by CO₂ emissions per MWh (lower is better)</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              type="number"
              className="text-muted-foreground"
              label={{ value: 'tonnes CO₂ / MWh', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              type="category"
              dataKey="company"
              width={100}
              className="text-muted-foreground text-sm"
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: 'var(--radius)'
              }}
              formatter={(value: number) => [value.toFixed(2), 'Efficiency']}
            />
            <Bar dataKey="efficiency" fill="hsl(var(--chart-4))" radius={[0, 8, 8, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
