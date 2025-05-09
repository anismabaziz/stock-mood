import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "../ui/card";
import { Button } from "../ui/button";
import { ArrowRight, Search } from "lucide-react";
import { Input } from "../ui/input";

export default function SentimentAnalyzer() {
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
              placeholder="Enter stock symbol (e.g., AAPL, TSLA, MSFT)"
              className="pl-10"
            />
          </div>
          <Button type="submit" className="gap-2">
            Analyze
            <ArrowRight className="h-4 w-4" />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
