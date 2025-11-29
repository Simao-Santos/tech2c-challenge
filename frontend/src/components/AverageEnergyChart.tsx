import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface AverageEnergyChartProps {
  data: { company: string; average: number }[];
}

export function AverageEnergyChart({ data }: AverageEnergyChartProps) {
  // Show only top 10 for readability
  const topData = data.slice(0, 10);
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Average Energy Consumption per Company</CardTitle>
        <CardDescription>Top 10 companies by average energy usage in MWh</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={topData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              type="number"
              className="text-muted-foreground"
              label={{ value: 'MWh', position: 'insideBottom', offset: -5 }}
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
              formatter={(value: number) => [`${value.toLocaleString()} MWh`, 'Average Consumption']}
            />
            <Bar dataKey="average" fill="hsl(var(--chart-2))" radius={[0, 8, 8, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
