import { Progress } from "@/components/ui/progress";

interface SentimentBarChartProps {
  distribution: { positive: number; negative: number; neutral: number };
}

export default function SentimentBarChart({
  distribution,
}: SentimentBarChartProps) {
  const colors = { positive: "green", negative: "red", neutral: "gray" };
  const sentimentArr = Object.entries(distribution).map((entry) => {
    return {
      sentiment: entry[0],
      count: entry[1],
      color: colors[`${entry[0]}`],
    };
  });
  return (
    <div className="space-y-4 mb-5">
      {sentimentArr.map((arr) => {
        return (
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium flex items-center">
                <span
                  className={`inline-block w-3 h-3 rounded-full bg-${arr.color}-500 mr-2`}
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
