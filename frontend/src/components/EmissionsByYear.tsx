import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface EmissionsByYearProps {
  data: { year: number; total: number }[];
}

export function EmissionsByYear({ data }: EmissionsByYearProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Total CO₂ Emissions per Year</CardTitle>
        <CardDescription>Total emissions in tonnes across all companies</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey="year" 
              className="text-muted-foreground"
            />
            <YAxis 
              className="text-muted-foreground"
              label={{ value: 'Tonnes', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: 'var(--radius)'
              }}
              formatter={(value: number) => [`${value.toLocaleString()} tonnes`, 'Total CO₂']}
            />
            <Bar dataKey="total" fill="hsl(var(--chart-1))" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
