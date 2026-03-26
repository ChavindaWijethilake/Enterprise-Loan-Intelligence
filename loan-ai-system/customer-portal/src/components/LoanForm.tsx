"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "./ui/Button";
import { Input } from "./ui/Input";
import { Select } from "./ui/Select";
import { CheckCircle2, Building2, User, Landmark } from "lucide-react";

export function LoanForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const [formData, setFormData] = useState({
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Mocking an processing delay structure disconnected from backend 
    setTimeout(() => {
      setIsSubmitting(false);
      setIsSuccess(true);
    }, 1500);
  };

  if (isSuccess) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        className="p-[32px] w-full text-center py-24"
      >
        <div className="w-20 h-20 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-6 text-green-600 border border-green-200 shadow-sm">
          <CheckCircle2 size={40} />
        </div>
        <h2 className="text-2xl font-bold font-outfit text-gray-900 mb-2">Application Submitted Successfully</h2>
        <p className="text-gray-600 mb-8 max-w-md mx-auto">
          The application data has been registered into the AI underwriting matrix. A decision logic sequence has been triggered.
        </p>
        <Button
          onClick={() => setIsSuccess(false)}
          className="px-8 bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
        >
          Submit Another Application
        </Button>
      </motion.div>
    );
  }

  return (
    <motion.form
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      onSubmit={handleSubmit}
      className="p-[32px] w-full"
    >
      {/* 
        Section 1: Applicant Profile
      */}
      <div className="mb-[24px]">
        <div className="flex items-center gap-2 mb-4 border-b border-gray-200 pb-2">
          <User size={18} className="text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Applicant Profile</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-[16px]">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Number of Dependents</label>
            <Input
              type="number"
              name="no_of_dependents"
              value={formData.no_of_dependents}
              onChange={handleChange}
              min="0"
              max="10"
              className="h-[44px] bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-900 rounded-lg shadow-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Education Background</label>
            <Select
              name="education"
              value={formData.education}
              onChange={handleChange}
              className="h-[44px] bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-900 rounded-lg shadow-sm"
            >
              <option value="1">Graduate</option>
              <option value="0">Not Graduate</option>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Employment Type</label>
            <Select
              name="self_employed"
              value={formData.self_employed}
              onChange={handleChange}
              className="h-[44px] bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-900 rounded-lg shadow-sm"
            >
              <option value="0">No (Salaried)</option>
              <option value="1">Yes (Self Employed)</option>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Annual Income (₹)</label>
            <Input
              type="number"
              name="income_annum"
              value={formData.income_annum}
              onChange={handleChange}
              placeholder="e.g. 1500000"
              required
              className="h-[44px] bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-900 rounded-lg shadow-sm"
            />
          </div>
        </div>
      </div>

      {/* 
        Section 2: Loan Requirements
      */}
      <div className="mb-[24px]">
        <div className="flex items-center gap-2 mb-4 border-b border-gray-200 pb-2">
          <Landmark size={18} className="text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Loan Requirements</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-[16px]">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Requested Loan Amount (₹)</label>
            <Input
              type="number"
              name="loan_amount"
              value={formData.loan_amount}
              onChange={handleChange}
              placeholder="e.g. 5000000"
              required
              className="h-[44px] bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-900 rounded-lg shadow-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Loan Term (Years)</label>
            <Input
              type="number"
              name="loan_term"
              value={formData.loan_term}
              onChange={handleChange}
              placeholder="e.g. 15"
              required
              className="h-[44px] bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-900 rounded-lg shadow-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Current CIBIL Score</label>
            <Input
              type="number"
              name="cibil_score"
              value={formData.cibil_score}
              onChange={handleChange}
              placeholder="300-900"
              required
              className="h-[44px] bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-900 rounded-lg shadow-sm"
            />
          </div>
        </div>
      </div>

      {/* 
        Section 3: Asset Portfolio
      */}
      <div className="mb-[32px]">
        <div className="flex items-center gap-2 mb-4 border-b border-gray-200 pb-2">
          <Building2 size={18} className="text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Asset Portfolio Verification</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-[16px]">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Residential Assets Value (₹)</label>
            <Input
              type="number"
              name="residential_assets_value"
              value={formData.residential_assets_value}
              onChange={handleChange}
              required
              className="h-[44px] bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-900 rounded-lg shadow-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Commercial Assets Value (₹)</label>
            <Input
              type="number"
              name="commercial_assets_value"
              value={formData.commercial_assets_value}
              onChange={handleChange}
              required
              className="h-[44px] bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-900 rounded-lg shadow-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Luxury Assets Value (₹)</label>
            <Input
              type="number"
              name="luxury_assets_value"
              value={formData.luxury_assets_value}
              onChange={handleChange}
              required
              className="h-[44px] bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-900 rounded-lg shadow-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Bank Assets Value (₹)</label>
            <Input
              type="number"
              name="bank_asset_value"
              value={formData.bank_asset_value}
              onChange={handleChange}
              required
              className="h-[44px] bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-gray-900 rounded-lg shadow-sm"
            />
          </div>
        </div>
      </div>

      <div className="pt-6 border-t border-gray-200 flex justify-end">
        <Button
          type="submit"
          disabled={isSubmitting}
          className="h-[44px] px-8 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium shadow-sm"
        >
          {isSubmitting ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Processing...
            </span>
          ) : (
            "Submit Enterprise Application"
          )}
        </Button>
      </div>
    </motion.form>
  );
}
