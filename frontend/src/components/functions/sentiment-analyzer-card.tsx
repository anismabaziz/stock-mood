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
import { analyze, AnalyzeRequestError } from "@/services/model";
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
    if (!stockInput.trim()) {
      return;
    }

    setStockName("");
    setStockData(null);
    stockMutation.mutate(stockInput.trim());
  };

  const errorMessage =
    stockMutation.error instanceof AnalyzeRequestError
      ? stockMutation.error.message
      : stockMutation.isError
        ? "Unable to analyze this stock right now. Please try again."
        : null;

  return (
    <Card className="mb-8 shadow-md w-full mx-3 md:w-3/4 rounded-sm">
      <CardHeader>
        <CardTitle className="md:text-3xl text-xl font-semibold">
          Search Stock Sentiment
        </CardTitle>
        <CardDescription>
          Enter a stock symbol to analyze Reddit sentiment from r/stocks
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          className="md:flex md:flex-row flex-col gap-4"
          onSubmit={(e) => {
            e.preventDefault();
            void handleAnalyzeClick();
          }}
        >
          <div className="relative w-full mb-4 md:mb-0">
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
            type="submit"
            className="gap-2 md:w-fit w-full"
            disabled={stockMutation.isPending || !stockInput.trim()}
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
        {errorMessage && (
          <p className="mt-3 text-sm text-red-600 dark:text-red-400">{errorMessage}</p>
        )}
      </CardContent>
    </Card>
  );
}
