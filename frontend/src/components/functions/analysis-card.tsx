import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "../ui/card";
import { TrendingUp } from "lucide-react";

import Charts from "./charts";
import useStockStore from "@/stores/stock-store";

export default function AnalysisCard() {
  const { stockData, stockName } = useStockStore();
  const sentimentDistribution = stockData?.distribution;

  return (
    <Card className="mb-8 shadow-md md:w-3/4 rounded-sm pt-0">
      <CardHeader className="bg-slate-50 dark:bg-slate-900 border-b pt-6">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-2xl font-semibold">
              <TrendingUp className="h-5 w-5 text-emerald-500" />
              Sentiment Analysis for {stockName}
            </CardTitle>
            <CardDescription>
              Based on 100 posts from r/stocks subreddit
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <div className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
              {sentimentDistribution?.positive}% Positive
            </div>
            <div className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100">
              {sentimentDistribution?.neutral}% Neutral
            </div>
            <div className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100">
              {sentimentDistribution?.negative}% Negative
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Charts />
      </CardContent>
    </Card>
  );
}
