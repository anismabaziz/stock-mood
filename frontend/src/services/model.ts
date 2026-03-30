import type { Post } from "@/types/app";
import axiosClient from ".";
import axios from "axios";

interface AnalyzeResponse {
  results: Post[];
  distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
  stock_symbol: string;
}

export class AnalyzeRequestError extends Error {
  code: string;

  constructor(message: string, code: string) {
    super(message);
    this.name = "AnalyzeRequestError";
    this.code = code;
  }
}

export async function analyze(stock_symbol: string) {
  try {
    const response = await axiosClient.post<AnalyzeResponse>("/api/analyze", {
      symbol: stock_symbol,
    });
    return response.data;
  } catch (error) {
    if (!axios.isAxiosError(error)) {
      throw new AnalyzeRequestError(
        "Something went wrong while analyzing this symbol.",
        "UNKNOWN_ERROR"
      );
    }

    if (error.code === "ECONNABORTED") {
      throw new AnalyzeRequestError(
        "The request timed out. Please try again in a moment.",
        "REQUEST_TIMEOUT"
      );
    }

    if (!error.response) {
      throw new AnalyzeRequestError(
        "Cannot reach the backend API. Make sure the server is running.",
        "NETWORK_ERROR"
      );
    }

    const payload = error.response.data as
      | { detail?: { code?: string; error?: string } }
      | undefined;

    throw new AnalyzeRequestError(
      payload?.detail?.error || "Analyze request failed.",
      payload?.detail?.code || "ANALYZE_FAILED"
    );
  }
}
