"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { Button } from "./ui/Button";
import { Input } from "./ui/Input";
import { Select } from "./ui/Select";
import { CheckCircle2, AlertCircle, ArrowRight, ArrowLeft, Send } from "lucide-react";

const STEPS = ["Business Info", "Financials", "Assets"];

export function LoanForm() {
  const [step, setStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const [formData, setFormData] = useState({
    applicant_name: "",
    applicant_email: "",
    no_of_dependents: "0",
    education: "1",
    self_employed: "0",
    income_annum: "",
    loan_amount: "",
    loan_term: "",
    cibil_score: "",
    residential_assets_value: "0",
    commercial_assets_value: "0",
    luxury_assets_value: "0",
    bank_asset_value: "0",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const nextStep = () => setStep((s) => Math.min(s + 1, STEPS.length - 1));
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (step < STEPS.length - 1) {
      nextStep();
      return;
    }

    setIsSubmitting(true);
    setResult(null);

    const payload = {
      ...formData,
      no_of_dependents: parseInt(formData.no_of_dependents),
      education: parseInt(formData.education),
      self_employed: parseInt(formData.self_employed),
      income_annum: parseFloat(formData.income_annum),
      loan_amount: parseFloat(formData.loan_amount),
      loan_term: parseInt(formData.loan_term),
      cibil_score: parseInt(formData.cibil_score),
      residential_assets_value: parseFloat(formData.residential_assets_value),
      commercial_assets_value: parseFloat(formData.commercial_assets_value),
      luxury_assets_value: parseFloat(formData.luxury_assets_value),
      bank_asset_value: parseFloat(formData.bank_asset_value),
    };

    try {
      const response = await fetch("http://localhost:8000/api/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        setResult({
          type: "success",
          message: `Application submitted! Reference ID: ${data.loan_id}. We'll contact you soon.`,
        });
      } else {
        setResult({ type: "error", message: data.detail || "Submission failed." });
      }
    } catch (err) {
      setResult({ type: "error", message: "Network error. Please try again." });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (result?.type === "success") {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-10 rounded-3xl text-center max-w-xl mx-auto"
      >
        <div className="w-20 h-20 bg-accent/20 rounded-full flex items-center justify-center mx-auto mb-6 text-accent">
          <CheckCircle2 size={40} />
        </div>
        <h2 className="text-3xl font-display font-bold mb-4">Application Success!</h2>
        <p className="text-gray-400 mb-8">{result.message}</p>
        <Button onClick={() => window.location.reload()} className="w-full">
          Submit Another Request
        </Button>
      </motion.div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress Stepper */}
      <div className="flex items-center justify-between mb-12 px-4">
        {STEPS.map((s, i) => (
          <div key={s} className="flex flex-col items-center gap-2 relative">
            <div
              className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 z-10",
                i <= step
                  ? "border-primary bg-primary text-white"
                  : "border-white/10 bg-white/5 text-gray-500"
              )}
            >
              {i < step ? <CheckCircle2 size={20} /> : i + 1}
            </div>
            <span className={cn("text-xs font-medium", i <= step ? "text-primary" : "text-gray-500")}>
              {s}
            </span>
            {i < STEPS.length - 1 && (
              <div className="absolute top-5 left-10 w-[calc(100%-10px)] h-[2px] bg-white/10 -z-0">
                <motion.div
                  initial={{ width: "0%" }}
                  animate={{ width: i < step ? "100%" : "0%" }}
                  className="h-full bg-primary"
                />
              </div>
            )}
          </div>
        ))}
      </div>

      <motion.form
        layout
        onSubmit={handleSubmit}
        className="glass-card p-8 md:p-10 rounded-3xl relative overflow-hidden"
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {step === 0 && (
              <>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Name / Company</label>
                  <Input
                    placeholder="Full legal name"
                    name="applicant_name"
                    value={formData.applicant_name}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Email Address</label>
                  <Input
                    type="email"
                    placeholder="name@company.com"
                    name="applicant_email"
                    value={formData.applicant_email}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300">Dependents</label>
                    <Input
                      type="number"
                      name="no_of_dependents"
                      value={formData.no_of_dependents}
                      onChange={handleChange}
                      min="0"
                      max="10"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300">Education</label>
                    <Select name="education" value={formData.education} onChange={handleChange}>
                      <option value="1">Graduate</option>
                      <option value="0">High School</option>
                    </Select>
                  </div>
                </div>
              </>
            )}

            {step === 1 && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300">Income (₹)</label>
                    <Input
                      type="number"
                      name="income_annum"
                      value={formData.income_annum}
                      onChange={handleChange}
                      placeholder="Annual Income"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300">Loan Amount (₹)</label>
                    <Input
                      type="number"
                      name="loan_amount"
                      value={formData.loan_amount}
                      onChange={handleChange}
                      placeholder="Requested Amount"
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300">Term (Years)</label>
                    <Input
                      type="number"
                      name="loan_term"
                      value={formData.loan_term}
                      onChange={handleChange}
                      placeholder="e.g. 10"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300">CIBIL Score</label>
                    <Input
                      type="number"
                      name="cibil_score"
                      value={formData.cibil_score}
                      onChange={handleChange}
                      placeholder="300-900"
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Self Employed</label>
                  <Select name="self_employed" value={formData.self_employed} onChange={handleChange}>
                    <option value="0">No (Salaried)</option>
                    <option value="1">Yes (Business Owner)</option>
                  </Select>
                </div>
              </>
            )}

            {step === 2 && (
              <div className="grid grid-cols-2 gap-x-4 gap-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Residential</label>
                  <Input
                    type="number"
                    name="residential_assets_value"
                    value={formData.residential_assets_value}
                    onChange={handleChange}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Commercial</label>
                  <Input
                    type="number"
                    name="commercial_assets_value"
                    value={formData.commercial_assets_value}
                    onChange={handleChange}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Luxury</label>
                  <Input
                    type="number"
                    name="luxury_assets_value"
                    value={formData.luxury_assets_value}
                    onChange={handleChange}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Bank Assets</label>
                  <Input
                    type="number"
                    name="bank_asset_value"
                    value={formData.bank_asset_value}
                    onChange={handleChange}
                  />
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {result?.type === "error" && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-500 flex items-center gap-3 text-sm"
          >
            <AlertCircle size={18} />
            {result.message}
          </motion.div>
        )}

        <div className="mt-10 flex items-center justify-between gap-4">
          <Button
            type="button"
            variant="ghost"
            onClick={prevStep}
            className={cn(step === 0 && "invisible")}
          >
            <ArrowLeft className="mr-2 w-4 h-4" />
            Back
          </Button>

          <Button type="submit" disabled={isSubmitting} className="flex-1 sm:flex-none">
            {isSubmitting ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Processing...
              </span>
            ) : step === STEPS.length - 1 ? (
              <span className="flex items-center gap-2">
                Submit Application <Send size={16} />
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Continue <ArrowRight size={16} />
              </span>
            )}
          </Button>
        </div>
      </motion.form>
    </div>
  );
}
