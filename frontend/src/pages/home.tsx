import AnalysisCard from "@/components/functions/analysis-card";
import RedditPosts from "@/components/functions/reddit-posts";
import SentimentAnalyzer from "@/components/functions/sentiment-analyzer-card";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto py-10 px-4 flex flex-col items-center">
        <h1 className="text-4xl font-bold mb-2 text-center bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-teal-500 dark:from-emerald-400 dark:to-teal-300">
          Stock Sentiment Analyzer
        </h1>
        <p className="text-center mb-10 text-muted-foreground max-w-2xl mx-auto">
          Analyze sentiment from r/stocks subreddit posts about any stock. Our
          tool fetches the top 100 posts and categorizes them as positive,
          neutral, or negative to help you gauge market sentiment.
        </p>
        <SentimentAnalyzer />
        <AnalysisCard />
        <RedditPosts />
      </div>
    </main>
  );
}
