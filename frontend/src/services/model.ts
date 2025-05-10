import type { Post } from "@/types/app";
import axiosClient from ".";

interface AnalyzeResponse {
  results: Post[];
  distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
  stock_symbol: string;
}

export async function analyze(stock_symbol: string) {
  const response = axiosClient.post<AnalyzeResponse>("/api/analyze", {
    symbol: stock_symbol,
  });
  return (await response).data;
}
