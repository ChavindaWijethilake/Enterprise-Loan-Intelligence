import { LoanForm } from "@/components/LoanForm";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4 selection:bg-blue-100 selection:text-blue-900">

      {/* Header Section */}
      <div className="text-center max-w-2xl mb-10 w-full">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-600 text-white font-bold text-xl mb-6 shadow-sm">
          LI
        </div>
        <h1 className="text-3xl font-outfit font-bold text-gray-900 tracking-tight mb-3">
          Enterprise Loan Origination
        </h1>
        <p className="text-gray-600 text-sm md:text-base leading-relaxed">
          Securely submit applicant financial profiles for automated AI underwriting and credit evaluation.
        </p>
      </div>

      {/* Form Container */}
      <div className="w-full max-w-[1100px] bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <LoanForm />
      </div>
    </main>
  );
}
