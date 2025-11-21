import { useState, useEffect } from "react";
import axios from "axios";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { SkillsForm } from "@/components/SkillsForm";
import { IssuesList } from "@/components/IssuesList";
import { AnalysisView, AnalysisResult } from "@/components/AnalysisView";
import { Footer } from "@/components/Footer";
import { Issue } from "@/components/IssueCard";
import { useToast } from "@/hooks/use-toast";

// API configuration - update these to match your backend endpoints
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const Index = () => {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [issues, setIssues] = useState<Issue[]>([]);
  const [selectedIssues, setSelectedIssues] = useState<string[]>([]);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [generateReports, setGenerateReports] = useState(true);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const { toast } = useToast();

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null;
    const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
    
    const initialTheme = savedTheme || systemTheme;
    setTheme(initialTheme);
    document.documentElement.classList.toggle("dark", initialTheme === "dark");
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.classList.toggle("dark", newTheme === "dark");
  };

  const handleGetStarted = () => {
    document.getElementById("skills-form")?.scrollIntoView({ behavior: "smooth" });
  };

    const handleSearch = async (skills: string[]) => {
    setIsSearching(true);
    setShowAnalysis(false);
    setAnalysisResult(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/search-issues`, {
        skills,
      });

      // ✅ FIX: Check if response.data is an array or object
      let foundIssues = [];
      if (Array.isArray(response.data)) {
        foundIssues = response.data;
      } else if (response.data && Array.isArray(response.data.issues)) {
        foundIssues = response.data.issues;
      }

      setIssues(foundIssues);
      setSelectedIssues([]);

      if (foundIssues.length > 0) {
        toast({
          title: "Issues Found!",
          description: `Found ${foundIssues.length} beginner-friendly issues matching your skills.`,
        });
      } else {
        toast({
          title: "No Issues Found",
          description: "Try different search terms.",
          variant: "default",
        });
      }

    } catch (error) {
      console.error("Search error:", error);
      // ... keep your existing error handling ...
    } finally {
      setIsSearching(false);
    }
  };


  const handleToggleIssue = (url: string) => {
    setSelectedIssues((prev) =>
      prev.includes(url) ? prev.filter((u) => u !== url) : [...prev, url]
    );
  };

    const handleAnalyze = async () => {
    if (selectedIssues.length === 0) return;

    setIsAnalyzing(true);
    setShowAnalysis(true);

    // ... scrolling logic ...

    try {
      const response = await axios.post(`${API_BASE_URL}/api/analyze`, {
        issue_urls: selectedIssues,
        generate_reports: generateReports,
      });

      // ✅ FIX: Map backend response to frontend AnalysisResult
      const backendData = response.data;
      const firstAnalysis = backendData.analyses?.[0] || {};
      const firstDownload = backendData.report_downloads?.[0] || {};

      const mappedResult: AnalysisResult = {
        solution_plan: firstAnalysis.solution_plan || "No plan generated.",
        prompt: firstAnalysis.generated_prompt || "No prompt generated.",
        download_url: firstDownload.download_url || undefined
      };

      setAnalysisResult(mappedResult);

      toast({
        title: "Analysis Complete!",
        description: "AI has generated a comprehensive solution plan.",
      });
    } catch (error) {
      // ... keep error handling ...
    } finally {
      setIsAnalyzing(false);
    }
  };


    const handleDownload = () => {
    if (!analysisResult?.download_url) return;

    // 1. Check if the URL is already absolute (starts with http)
    let downloadUrl = analysisResult.download_url;
    
    if (!downloadUrl.startsWith("http")) {
      // If relative, prepend the base URL
      // Remove leading slash to avoid double slashes if needed
      const cleanPath = downloadUrl.startsWith("/") ? downloadUrl.slice(1) : downloadUrl;
      downloadUrl = `${API_BASE_URL}/${cleanPath}`;
    }

    console.log("Downloading from:", downloadUrl); // Debugging

    // 2. Create a temporary link element to force download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.target = "_blank"; // Open in new tab as backup
    link.setAttribute('download', ''); // Hint to browser to download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    toast({
      title: "Downloading...",
      description: "Your GSOC proposal is being downloaded.",
    });
  };


  const handleBack = () => {
    setShowAnalysis(false);
    setAnalysisResult(null);
  };

  return (
    <div className="flex min-h-screen flex-col">
      <Header theme={theme} toggleTheme={toggleTheme} />
      
      <main className="flex-1">
        {!showAnalysis && (
          <>
            <Hero onGetStarted={handleGetStarted} />
            
            <div id="skills-form">
              <SkillsForm onSearch={handleSearch} isLoading={isSearching} />
            </div>

            <IssuesList
              issues={issues}
              selectedIssues={selectedIssues}
              onToggleIssue={handleToggleIssue}
              onAnalyze={handleAnalyze}
              isLoading={isSearching}
            />
          </>
        )}

        {showAnalysis && (
          <div id="analysis">
            <AnalysisView
              result={analysisResult}
              isLoading={isAnalyzing}
              generateReports={generateReports}
              onGenerateReportsChange={setGenerateReports}
              onDownload={handleDownload}
              onBack={handleBack}
            />
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};

export default Index;
