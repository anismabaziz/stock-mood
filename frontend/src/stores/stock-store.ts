import type { Post } from "@/types/app";
import { create } from "zustand";

interface StockData {
  results: Post[];
  distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
}
interface StockState {
  stockData: StockData | null;
  stockName: string;
  setStockName: (name: string) => void;
  setStockData: (data: StockData | null) => void;
}
const useStockStore = create<StockState>((set) => ({
  stockData: null,
  stockName: "",
  setStockName: (name) => set({ stockName: name }),
  setStockData: (data) => set({ stockData: data }),
}));

export default useStockStore;
