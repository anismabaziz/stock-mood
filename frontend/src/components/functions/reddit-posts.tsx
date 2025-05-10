import PostCard from "./post-card";
import {
  BarChart3,
  Filter,
  ChevronDown,
  Calendar,
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
import { useState, useMemo } from "react";
import { Badge } from "../ui/badge";

export default function RedditPosts() {
  const { stockData } = useStockStore();
  const posts = stockData!.results!;

  const [sentimentFilter, setSentimentFilter] = useState<
    "all" | "positive" | "neutral" | "negative"
  >("all");
  const [sortOption, setSortOption] = useState<"relevance" | "date">(
    "relevance"
  );

  const filteredAndSortedPosts = useMemo(() => {
    let result = [...posts];

    if (sentimentFilter !== "all") {
      result = result.filter(
        (post) => post.sentiment.toLowerCase() === sentimentFilter
      );
    }

    if (sortOption === "date") {
      result.sort(
        (a, b) =>
          new Date(b.created_utc).getTime() - new Date(a.created_utc).getTime()
      );
    }

    if (sortOption === "relevance") {
      result.sort((a, b) => b.upvotes - a.upvotes);
    }

    return result;
  }, [posts, sentimentFilter, sortOption]);

  return (
    <div className="md:w-3/4 space-y-6">
      <div className="flex items-center gap-4 justify-between">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-emerald-500" />
          Reddit Posts
        </h2>
        <div className="flex items-center gap-2">
          <FilterMenu
            setFilter={setSentimentFilter}
            filterOption={sentimentFilter}
          />
          <SortingMenu setSort={setSortOption} sortOption={sortOption} />
        </div>
      </div>

      <div className="space-y-4">
        {filteredAndSortedPosts.map((post) => {
          return <PostCard post={post} />;
        })}
      </div>
    </div>
  );
}

interface FilterMenuProps {
  setFilter: (filter: "all" | "positive" | "neutral" | "negative") => void;
  filterOption: "all" | "positive" | "neutral" | "negative";
}

function FilterMenu({ setFilter, filterOption }: FilterMenuProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="h-8 gap-1">
          <Filter className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Filter</span>
          <Badge
            variant="secondary"
            className={filterOption === "all" ? "hidden" : "ml-1 h-5 px-1.5"}
          >
            {filterOption}
          </Badge>
          <ChevronDown className="h-3.5 w-3.5 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuLabel>Filter by Sentiment</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem onClick={() => setFilter("all")}>
            All Posts
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setFilter("positive")}>
            <span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span>
            Positive
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setFilter("neutral")}>
            <span className="w-2 h-2 rounded-full bg-gray-500 mr-2"></span>
            Neutral
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setFilter("negative")}>
            <span className="w-2 h-2 rounded-full bg-red-500 mr-2"></span>
            Negative
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

interface SortingMenuProps {
  setSort: (criteria: "relevance" | "date") => void;
  sortOption: "relevance" | "date";
}
function SortingMenu({ setSort, sortOption }: SortingMenuProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="h-8 gap-1">
          <SortAsc className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Sort</span>
          <Badge variant="secondary" className="ml-1 h-5 px-1.5">
            {sortOption}
          </Badge>
          <ChevronDown className="h-3.5 w-3.5 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuLabel>Sort Posts By</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem
            onClick={() => setSort("relevance")}
            className={`${sortOption == "relevance" && "bg-accent"}`}
          >
            Relevance
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => setSort("date")}
            className={`${sortOption == "date" && "bg-accent"}`}
          >
            <Calendar className="h-4 w-4 mr-2" />
            Date (Newest)
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
