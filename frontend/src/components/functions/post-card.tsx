import { Card, CardContent, CardFooter } from "../ui/card";
import { Button } from "../ui/button";
import { ThumbsUp, ArrowUpRight, Calendar } from "lucide-react";
import { Badge } from "../ui/badge";

interface PostCardProps {
  post: {
    title: string;
    content: string;
    author: string;
    upvotes: number;
    estimated_downvotes: number;
    sentiment: string;
    created_utc: string;
  };
}

export default function PostCard({ post }: PostCardProps) {
  return (
    <Card className="overflow-hidden transition-all hover:shadow-md py-0">
      <div
        className={`h-1 w-full ${getSentimentColor(
          post.sentiment.toLowerCase()
        )}`}
      ></div>
      <CardContent className="pt-6">
        <div className="flex justify-between items-start gap-2 mb-2">
          <h3 className="font-medium line-clamp-2">{post.title}</h3>

          <SentimentBadge sentiment={post.sentiment.toLowerCase()} />
        </div>
        <p className="text-sm text-muted-foreground mt-2 line-clamp-3">
          {post.content}
        </p>
      </CardContent>
      <CardFooter className="border-t bg-slate-50 dark:bg-slate-900 flex justify-between items-center pt-3 pb-3 text-xs text-muted-foreground">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <ThumbsUp className="h-3 w-3" />
            {post.upvotes}
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {formatDate(post.created_utc)}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span>u/{post.author}</span>
          <Button variant="ghost" size="icon" className="h-6 w-6">
            <ArrowUpRight className="h-3 w-3" />
            <span className="sr-only">View post</span>
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}

function SentimentBadge({ sentiment }: { sentiment: string }) {
  const variants = {
    positive:
      "bg-green-100 text-green-800 hover:bg-green-100 dark:bg-green-900 dark:text-green-100",
    neutral:
      "bg-gray-100 text-gray-800 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-100",
    negative:
      "bg-red-100 text-red-800 hover:bg-red-100 dark:bg-red-900 dark:text-red-100",
  };

  return (
    <Badge
      variant="outline"
      className={`${variants[sentiment]} flex items-center gap-1`}
    >
      {sentiment}
    </Badge>
  );
}

function getSentimentColor(sentiment: string) {
  switch (sentiment) {
    case "positive":
      return "bg-gradient-to-r from-green-400 to-emerald-500";
    case "neutral":
      return "bg-gradient-to-r from-gray-400 to-gray-500";
    case "negative":
      return "bg-gradient-to-r from-red-400 to-red-500";
  }
}

function formatDate(date_str: string) {
  const date = new Date(date_str);
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}
