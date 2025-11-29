import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface TopEmittersChartProps {
  data: { company: string; total: number }[];
}

const COLORS = [
  'hsl(var(--chart-1))',
  'hsl(var(--chart-2))',
  'hsl(var(--chart-3))',
  'hsl(var(--chart-4))',
  'hsl(var(--chart-5))',
];

export function TopEmittersChart({ data }: TopEmittersChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Top 5 Companies with Highest Emissions</CardTitle>
        <CardDescription>Total CO₂ emissions in tonnes</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={data} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              type="number"
              className="text-muted-foreground"
              label={{ value: 'Tonnes CO₂', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              type="category"
              dataKey="company"
              width={100}
              className="text-muted-foreground font-medium"
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: 'var(--radius)'
              }}
              formatter={(value: number) => [`${value.toLocaleString()} tonnes`, 'Total Emissions']}
            />
            <Bar dataKey="total" radius={[0, 8, 8, 0]}>
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
