import { motion } from "framer-motion";
import { IssueCard, Issue } from "./IssueCard";
import { Button } from "@/components/ui/button";
import { Sparkles, AlertCircle } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

interface IssuesListProps {
  issues: Issue[];
  selectedIssues: string[];
  onToggleIssue: (url: string) => void;
  onAnalyze: () => void;
  isLoading?: boolean;
}

export function IssuesList({
  issues = [], // ✅ Default to empty array
  selectedIssues,
  onToggleIssue,
  onAnalyze,
  isLoading = false,
}: IssuesListProps) {
  
  // ✅ Safety check: if issues is not an array, force it to be empty
  const safeIssues = Array.isArray(issues) ? issues : [];

  if (isLoading) {
    return (
      <section className="container px-4 py-12 md:px-6">
        <div className="mb-8 text-center">
          <Skeleton className="mx-auto mb-3 h-8 w-64" />
          <Skeleton className="mx-auto h-5 w-96" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-48 w-full" />
          ))}
        </div>
      </section>
    );
  }

  if (safeIssues.length === 0) {
    return null;
  }

  return (
    <motion.section
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="container px-4 py-12 md:px-6"
    >
      <div className="mb-8 text-center">
        <h2 className="mb-3 text-3xl font-bold tracking-tight">
          Good First Issues
        </h2>
        <p className="text-muted-foreground">
          Found {safeIssues.length} beginner-friendly {safeIssues.length === 1 ? "issue" : "issues"} matching your skills
        </p>
      </div>

      {/* Issues Grid */}
      <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {safeIssues.map((issue, index) => (
          <motion.div
            key={issue.url}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <IssueCard
              issue={issue}
              isSelected={selectedIssues.includes(issue.url)}
              onToggle={onToggleIssue}
            />
          </motion.div>
        ))}
      </div>

      {/* Selection Info & Analyze Button */}
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <AlertCircle className="h-4 w-4" />
          <span>
            {selectedIssues.length === 0
              ? "Select issues to analyze"
              : `${selectedIssues.length} ${selectedIssues.length === 1 ? "issue" : "issues"} selected`}
          </span>
        </div>

        <Button
          size="lg"
          variant="default" // Changed "gradient" to "default" (standard shadcn) unless you have a custom variant
          onClick={onAnalyze}
          disabled={selectedIssues.length === 0}
          className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0"
        >
          <Sparkles className="h-4 w-4 mr-2" />
          Analyze Selected Issues
        </Button>
      </div>
    </motion.section>
  );
}
