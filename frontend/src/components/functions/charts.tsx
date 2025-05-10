import { Tabs, TabsTrigger, TabsList, TabsContent } from "../ui/tabs";
import SentimentDonutChart from "@/components/charts/donut-chart";
import SentimentBarChart from "@/components/charts/normal-chart";
import { Card, CardContent } from "@/components/ui/card";
import useStockStore from "@/stores/stock-store";

export default function Charts() {
  const { stockData } = useStockStore();
  const sentimentDistribution = stockData!.distribution!;

  const colors = { positive: "green", negative: "red", neutral: "gray" };
  const sentimentArr = Object.entries(sentimentDistribution).map((entry) => {
    return {
      sentiment: entry[0],
      count: entry[1],
      color: colors[`${entry[0]}`],
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
      <div className="grid grid-cols-3 gap-4 mt-6 text-center">
        {sentimentArr.map((arr) => {
          return (
            <Card
              className={`bg-${arr.color}-50 border-${arr.color}-200 rounded-sm`}
            >
              <CardContent className="p-4">
                <p className={`text-sm text-${arr.color}-600`}>
                  {arr.sentiment}
                </p>
                <p className={`text-3xl font-bold text-${arr.color}-600`}>
                  {arr.count}%
                </p>
                <p className={`text-xs text-${arr.color}-600/70`}>
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
