import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "../ui/card";
import { Button } from "../ui/button";
import { ArrowRight, Search, Loader2 } from "lucide-react";
import { Input } from "../ui/input";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { analyze } from "@/services/model";
import useStockStore from "@/stores/stock-store";

export default function SentimentAnalyzer() {
  const [stockInput, setStockInput] = useState("");
  const { setStockName, setStockData } = useStockStore();

  const stockMutation = useMutation({
    mutationFn: analyze,
    onSuccess(data) {
      setStockName(data.stock_symbol);
      setStockData({ results: data.results, distribution: data.distribution });
      setStockInput("");
    },
  });

  const handleAnalyzeClick = async () => {
    setStockName("");
    setStockData(null);
    stockMutation.mutate(stockInput);
  };

  return (
    <Card className="mb-8 shadow-md md:w-3/4 rounded-sm">
      <CardHeader>
        <CardTitle className="text-3xl font-semibold">
          Search Stock Sentiment
        </CardTitle>
        <CardDescription>
          Enter a stock symbol to analyze Reddit sentiment from r/stocks
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              value={stockInput}
              onChange={(e) => setStockInput(e.target.value)}
              placeholder="Enter stock symbol (e.g., AAPL, TSLA, MSFT)"
              className="pl-10"
            />
          </div>
          <Button
            onClick={handleAnalyzeClick}
            className="gap-2"
            disabled={stockMutation.isPending}
          >
            {stockMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing
              </>
            ) : (
              <>
                Analyze
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
