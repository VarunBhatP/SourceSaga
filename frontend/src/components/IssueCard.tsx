import { motion } from "framer-motion";
import { ExternalLink, GitBranch } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";

export interface Issue {
  url: string;
  repo: string;
  title: string;
  labels: string[];
  description?: string;
}

interface IssueCardProps {
  issue: Issue;
  isSelected: boolean;
  onToggle: (url: string) => void;
}

export function IssueCard({ issue, isSelected, onToggle }: IssueCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className={`group relative cursor-pointer overflow-hidden transition-all duration-300 hover:shadow-lg-custom ${
          isSelected ? "border-primary bg-primary/5 shadow-lg-custom" : ""
        }`}
        onClick={() => onToggle(issue.url)}
      >
        <div className="absolute inset-0 bg-gradient-primary opacity-0 transition-opacity group-hover:opacity-5" />
        
        <CardHeader className="space-y-3 pb-3">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <Checkbox
                checked={isSelected}
                onCheckedChange={() => onToggle(issue.url)}
                className="mt-1"
                onClick={(e) => e.stopPropagation()}
              />
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <GitBranch className="h-4 w-4" />
                  <span className="font-medium">{issue.repo}</span>
                </div>
                <CardTitle className="text-base leading-snug hover:text-primary">
                  {issue.title}
                </CardTitle>
              </div>
            </div>
            
            <a
              href={issue.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="flex-shrink-0 rounded-full p-2 transition-colors hover:bg-accent"
              aria-label="Open issue on GitHub"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>

          {issue.description && (
            <CardDescription className="line-clamp-2 text-sm">
              {issue.description}
            </CardDescription>
          )}
        </CardHeader>

        {issue.labels.length > 0 && (
          <CardContent className="pt-0">
            <div className="flex flex-wrap gap-1.5">
              {issue.labels.slice(0, 5).map((label) => (
                <Badge
                  key={label}
                  variant="outline"
                  className="text-xs font-normal"
                >
                  {label}
                </Badge>
              ))}
              {issue.labels.length > 5 && (
                <Badge variant="outline" className="text-xs font-normal">
                  +{issue.labels.length - 5} more
                </Badge>
              )}
            </div>
          </CardContent>
        )}
      </Card>
    </motion.div>
  );
}
