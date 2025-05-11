import { Tabs, TabsTrigger, TabsList, TabsContent } from "../ui/tabs";
import SentimentDonutChart from "@/components/charts/donut-chart";
import SentimentBarChart from "@/components/charts/normal-chart";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import useStockStore from "@/stores/stock-store";

export default function Charts() {
  const { stockData } = useStockStore();
  const sentimentDistribution = stockData!.distribution!;

  const colorStyles = {
    positive: {
      bg: "bg-green-50",
      border: "border-green-200",
      text: "text-green-600",
      subtext: "text-green-600/70",
    },
    negative: {
      bg: "bg-red-50",
      border: "border-red-200",
      text: "text-red-600",
      subtext: "text-red-600/70",
    },
    neutral: {
      bg: "bg-gray-50",
      border: "border-gray-200",
      text: "text-gray-600",
      subtext: "text-gray-600/70",
    },
  };
  const sentimentArr = Object.entries(sentimentDistribution).map((entry) => {
    return {
      sentiment: entry[0],
      count: entry[1],
    };
  });

  return (
    <>
      <Tabs defaultValue="donut">
        <TabsList className="mb-4 rounded-sm h-10">
          <TabsTrigger value="donut" className="rounded-sm">
            Donut Chart
          </TabsTrigger>
          <TabsTrigger value="bar" className="rounded-sm">
            Bar Chart
          </TabsTrigger>
        </TabsList>
        <TabsContent value="donut" className="flex justify-center">
          <div className="w-64 h-64">
            <SentimentDonutChart distribution={sentimentDistribution} />
          </div>
        </TabsContent>
        <TabsContent value="bar">
          <SentimentBarChart distribution={sentimentDistribution} />
        </TabsContent>
      </Tabs>
      <div className="grid md:grid-cols-3 grid-cols-1 gap-4 mt-6 text-center">
        {sentimentArr.map((arr, idx) => {
          const styles = colorStyles[arr.sentiment as keyof typeof colorStyles];
          return (
            <Card className={cn("rounded-sm", styles.bg)} key={idx}>
              <CardContent className="p-4">
                <p className={cn("text-sm", styles.text)}>{arr.sentiment}</p>
                <p className={cn("text-3xl font-bold", styles.text)}>
                  {arr.count}%
                </p>
                <p className={cn("text-xs", styles.subtext)}>
                  {arr.count} posts
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </>
  );
}
