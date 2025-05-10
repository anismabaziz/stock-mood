import { Label, Pie, PieChart } from "recharts";
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

interface SentimentDonutChartProps {
  distribution: { positive: number; negative: number; neutral: number };
}

const chartConfig = {
  posts: {
    label: "Posts",
  },
  positive: {
    label: "Positive",
    color: "#10b981",
  },
  negative: {
    label: "Negative",
    color: "#ef4444",
  },
  neutral: {
    label: "Neutral",
    color: "#6b7280",
  },
} satisfies ChartConfig;

export default function SentimentDonutChart({
  distribution,
}: SentimentDonutChartProps) {
  const totalPosts =
    distribution.negative + distribution.positive + distribution.neutral;

  const chartData = [
    {
      browser: "positive",
      posts: distribution.positive,
      fill: "#10b981",
    },
    {
      browser: "neutral",
      posts: distribution.neutral,
      fill: "#6b7280",
    },
    {
      browser: "negative",
      posts: distribution.negative,
      fill: "#ef4444",
    },
  ];

  return (
    <ChartContainer
      config={chartConfig}
      className="mx-auto aspect-square max-h-[250px]"
    >
      <PieChart>
        <ChartTooltip
          cursor={false}
          content={<ChartTooltipContent hideLabel />}
        />
        <Pie
          data={chartData}
          dataKey="posts"
          nameKey="browser"
          innerRadius={60}
          strokeWidth={5}
        >
          <Label
            content={({ viewBox }) => {
              if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                return (
                  <text
                    x={viewBox.cx}
                    y={viewBox.cy}
                    textAnchor="middle"
                    dominantBaseline="middle"
                  >
                    <tspan
                      x={viewBox.cx}
                      y={viewBox.cy}
                      className="fill-foreground text-3xl font-bold"
                    >
                      {totalPosts.toLocaleString()}
                    </tspan>
                    <tspan
                      x={viewBox.cx}
                      y={(viewBox.cy || 0) + 24}
                      className="fill-muted-foreground"
                    >
                      Posts
                    </tspan>
                  </text>
                );
              }
            }}
          />
        </Pie>
      </PieChart>
    </ChartContainer>
  );
}
