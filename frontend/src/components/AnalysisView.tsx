import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, FileText, Lightbulb, Code, CheckCircle2, ArrowLeft, Check, Copy } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { useState } from "react";

export interface AnalysisResult {
  solution_plan: string;
  prompt: string;
  download_url?: string;
}

interface AnalysisViewProps {
  result: AnalysisResult | null;
  isLoading: boolean;
  generateReports: boolean;
  onGenerateReportsChange: (value: boolean) => void;
  onDownload: () => void;
  onBack: () => void;
}

export function AnalysisView({
  result,
  isLoading,
  generateReports,
  onGenerateReportsChange,
  onDownload,
  onBack,
}: AnalysisViewProps) {
  const [hasCopied, setHasCopied] = useState(false);

  const handleCopyPrompt = async () => {
    if (result?.prompt) {
      await navigator.clipboard.writeText(result.prompt);
      setHasCopied(true);
      setTimeout(() => setHasCopied(false), 2000);
    }
  };

  if (!result && !isLoading) {
    return null;
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="container px-4 py-12 md:px-6"
    >
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={onBack}
            className="mb-4 -ml-2 gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Issues
          </Button>
          
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="mb-2 text-3xl font-bold tracking-tight">
                AI-Powered Analysis
              </h2>
              <p className="text-muted-foreground">
                Comprehensive solution plan and recommendations
              </p>
            </div>

            <div className="flex items-center gap-3 rounded-lg border border-border bg-card p-3">
              <Switch
                id="generate-reports"
                checked={generateReports}
                onCheckedChange={onGenerateReportsChange}
                disabled={isLoading}
              />
              <Label
                htmlFor="generate-reports"
                className="cursor-pointer text-sm font-medium"
              >
                Generate GSOC Proposal
              </Label>
            </div>
          </div>
        </div>

        {isLoading ? (
          /* Loading State */
          <Card className="overflow-hidden">
            <CardHeader className="space-y-2 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
              <div className="flex items-center gap-2">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                <CardTitle>Analyzing Issues...</CardTitle>
              </div>
              <CardDescription>
                Our AI is reviewing the selected issues and generating a comprehensive solution plan
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              <div className="space-y-3">
                {[...Array(4)].map((_, i) => (
                  <div
                    key={i}
                    className="h-4 animate-pulse rounded bg-muted"
                    style={{ width: `${100 - i * 10}%` }}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        ) : result ? (
          /* Analysis Results */
          <div className="space-y-6">
            {/* Solution Plan Card */}
            <Card className="overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
                <div className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-primary" />
                  <CardTitle>Solution Plan</CardTitle>
                </div>
                <CardDescription>
                  Step-by-step approach to tackle the selected issues
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {result.solution_plan}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Prompt Card */}
            <Card className="overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
                <div className="flex items-center gap-2">
                  <Code className="h-5 w-5 text-primary" />
                  <CardTitle>AI Prompt</CardTitle>
                </div>
                <CardDescription>
                  Use this prompt to get more detailed guidance from AI assistants
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="relative">
                  <pre className="overflow-x-auto rounded-lg bg-muted p-4 text-sm">
                    <code>{result.prompt}</code>
                  </pre>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="absolute right-2 top-2 gap-2"
                    onClick={handleCopyPrompt}
                  >
                    {hasCopied ? (
                      <>
                        <Check className="h-4 w-4 text-green-600" />
                        <span className="text-green-600">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4" />
                        <span>Copy</span>
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Download Section */}
            {generateReports && result.download_url && (
              <Card className="overflow-hidden border-primary/20 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5 text-primary" />
                    <CardTitle>GSOC Proposal Ready</CardTitle>
                  </div>
                  <CardDescription>
                    Your proposal document has been generated and is ready to download
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">GSOC_Proposal.pdf</p>
                      <p className="text-sm text-muted-foreground">
                        Professional proposal template
                      </p>
                    </div>
                    <Button
                      variant="default" // Standard variant
                      className="gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                      onClick={onDownload}
                    >
                      <Download className="h-4 w-4" />
                      Download
                    </Button>
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <p className="text-sm font-medium">What's included:</p>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      <li className="flex items-center gap-2">
                        <Badge variant="outline" className="h-5 w-5 rounded-full p-0 flex items-center justify-center">
                          <CheckCircle2 className="h-3 w-3" />
                        </Badge>
                        Project overview and objectives
                      </li>
                      <li className="flex items-center gap-2">
                        <Badge variant="outline" className="h-5 w-5 rounded-full p-0 flex items-center justify-center">
                          <CheckCircle2 className="h-3 w-3" />
                        </Badge>
                        Technical approach and timeline
                      </li>
                      <li className="flex items-center gap-2">
                        <Badge variant="outline" className="h-5 w-5 rounded-full p-0 flex items-center justify-center">
                          <CheckCircle2 className="h-3 w-3" />
                        </Badge>
                        Deliverables and milestones
                      </li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ) : null}
      </div>
    </motion.section>
  );
}
