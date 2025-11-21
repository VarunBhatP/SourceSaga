import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Search, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface SkillsFormProps {
  onSearch: (skills: string[]) => void;
  isLoading: boolean;
}

export function SkillsForm({ onSearch, isLoading }: SkillsFormProps) {
  const [inputValue, setInputValue] = useState("");
  const [skills, setSkills] = useState<string[]>([]);

  const handleAddSkill = () => {
    const newSkills = inputValue
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0 && !skills.includes(s));
    
    if (newSkills.length > 0) {
      setSkills([...skills, ...newSkills]);
      setInputValue("");
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    setSkills(skills.filter((s) => s !== skillToRemove));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddSkill();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (skills.length > 0) {
      onSearch(skills);
    }
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="container px-4 py-12 md:px-6 md:py-16"
    >
      <div className="mx-auto max-w-2xl">
        <div className="mb-8 text-center">
          <h2 className="mb-3 text-3xl font-bold tracking-tight">
            What are your skills?
          </h2>
          <p className="text-muted-foreground">
            Enter your programming languages, frameworks, and tools to find matching issues
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="skills" className="text-base">
              Skills
            </Label>
            <div className="flex gap-2">
              <Input
                id="skills"
                type="text"
                placeholder="e.g., Python, FastAPI, React, TypeScript"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                className="flex-1"
                disabled={isLoading}
              />
              <Button
                type="button"
                variant="outline"
                onClick={handleAddSkill}
                disabled={!inputValue.trim() || isLoading}
              >
                Add
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">
              Separate multiple skills with commas
            </p>
          </div>

          {/* Skills badges */}
          {skills.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="flex flex-wrap gap-2"
            >
              {skills.map((skill) => (
                <Badge
                  key={skill}
                  variant="secondary"
                  className="gap-1 px-3 py-1.5 text-sm"
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(skill)}
                    className="ml-1 rounded-full hover:bg-muted"
                    disabled={isLoading}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </motion.div>
          )}

          <Button
            type="submit"
            size="lg"
            variant="gradient"
            className="w-full"
            disabled={skills.length === 0 || isLoading}
          >
            {isLoading ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Searching...
              </>
            ) : (
              <>
                <Search className="h-4 w-4" />
                Find Issues
              </>
            )}
          </Button>
        </form>
      </div>
    </motion.section>
  );
}
