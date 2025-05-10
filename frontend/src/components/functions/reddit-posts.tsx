import PostCard from "./post-card";
import {
  BarChart3,
  Filter,
  ChevronDown,
  Calendar,
  TrendingUp,
  SortAsc,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuGroup,
  DropdownMenuSeparator,
} from "../ui/dropdown-menu";
import { Button } from "../ui/button";
import useStockStore from "@/stores/stock-store";

export default function RedditPosts() {
  const { stockData } = useStockStore();
  const posts = stockData!.results!;

  return (
    <div className="md:w-3/4 space-y-6">
      <div className="flex items-center gap-4 justify-between">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-emerald-500" />
          Reddit Posts
        </h2>
        <div className="flex items-center gap-2">
          <FilterMenu />
          <SortingMenu />
        </div>
      </div>

      <div className="space-y-4">
        {posts.map((post) => {
          return <PostCard post={post} />;
        })}
      </div>
    </div>
  );
}

function FilterMenu() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="h-8 gap-1">
          <Filter className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Filter</span>
          <ChevronDown className="h-3.5 w-3.5 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuLabel>Filter by Sentiment</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem>All Posts</DropdownMenuItem>
          <DropdownMenuItem>
            <span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span>
            Positive
          </DropdownMenuItem>
          <DropdownMenuItem>
            <span className="w-2 h-2 rounded-full bg-gray-500 mr-2"></span>
            Neutral
          </DropdownMenuItem>
          <DropdownMenuItem>
            <span className="w-2 h-2 rounded-full bg-red-500 mr-2"></span>
            Negative
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function SortingMenu() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="h-8 gap-1">
          <SortAsc className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Sort</span>

          <ChevronDown className="h-3.5 w-3.5 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuLabel>Sort Posts By</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem>Relevance</DropdownMenuItem>
          <DropdownMenuItem>
            <Calendar className="h-4 w-4 mr-2" />
            Date (Newest)
          </DropdownMenuItem>
          <DropdownMenuItem>
            <TrendingUp className="h-4 w-4 mr-2" />
            Sentiment Score
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
