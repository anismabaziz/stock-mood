import { Progress } from "@/components/ui/progress";

interface SentimentBarChartProps {
  distribution: { positive: number; negative: number; neutral: number };
}

export default function SentimentBarChart({
  distribution,
}: SentimentBarChartProps) {
  const dotColors = {
    positive: "bg-green-500",
    negative: "bg-red-500",
    neutral: "bg-gray-500",
  };
  const sentimentArr = Object.entries(distribution).map((entry) => {
    return {
      sentiment: entry[0],
      count: entry[1],
    };
  });
  return (
    <div className="space-y-4 mb-5">
      {sentimentArr.map((arr) => {
        const dotColor = dotColors[arr.sentiment as keyof typeof dotColors];
        return (
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium flex items-center">
                <span
                  className={`inline-block w-3 h-3 rounded-full ${dotColor} mr-2`}
                ></span>
                {arr.sentiment}
              </span>
              <span className="text-sm font-medium">{arr.count}%</span>
            </div>
            <Progress
              value={arr.count}
              className="h-3 rounded-full bg-gray-100"
            />
          </div>
        );
      })}
    </div>
  );
}
