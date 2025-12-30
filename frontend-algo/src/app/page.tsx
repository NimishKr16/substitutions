"use client";

import { useState } from "react";

interface Substitution {
  part_number: string;
  type: string;
  details: string;
}

interface SingleMpnResult {
  mpn: string;
  series: string;
  substitutions: Substitution[];
}

interface BatchApiResponse {
  brand: string;
  total: number;
  results: SingleMpnResult[];
}

export default function Home() {
  const [brand, setBrand] = useState("yageo");
  const [mpnInput, setMpnInput] = useState("");
  const [batchResults, setBatchResults] = useState<SingleMpnResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [openAccordions, setOpenAccordions] = useState<Set<number>>(new Set());

  const handleSearch = async () => {
    const trimmedInput = mpnInput.trim();
    if (!trimmedInput) return;

    // Split by newlines and clean up
    const mpns = trimmedInput
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    if (mpns.length === 0) return;

    setLoading(true);
    setError("");
    setBatchResults([]);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/generate/batch`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            brand: brand,
            mpns: mpns,
          }),
        }
      );

      const data: BatchApiResponse = await response.json();
      console.log("API Response:", data);

      if (data.results && data.results.length > 0) {
        setBatchResults(data.results);
        // Auto-open first accordion if multiple results
        if (data.results.length > 1) {
          setOpenAccordions(new Set([0]));
        }
      } else {
        setError("No results found. Please check the MPNs.");
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      setError(
        "Failed to connect to the API. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const toggleAccordion = (index: number) => {
    setOpenAccordions((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const handleExportToExcel = async () => {
    const trimmedInput = mpnInput.trim();
    if (!trimmedInput) {
      setError("Please enter at least one MPN to export.");
      return;
    }

    // Split by newlines and clean up
    const mpns = trimmedInput
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    if (mpns.length === 0) {
      setError("Please enter at least one MPN to export.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/generate/batch/export`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            brand: brand,
            mpns: mpns,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to generate Excel file");
      }

      // Get the blob and download it
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `yageo_substitutions_${new Date().getTime()}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error exporting to Excel:", error);
      setError("Failed to export to Excel. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const renderSubstitutionTable = (substitutions: Substitution[]) => (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-zinc-100 dark:bg-zinc-700">
            <th className="px-4 py-3 text-left text-sm font-semibold text-zinc-900 dark:text-zinc-100 border-b border-zinc-300 dark:border-zinc-600">
              Part Number
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-zinc-900 dark:text-zinc-100 border-b border-zinc-300 dark:border-zinc-600">
              Type
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-zinc-900 dark:text-zinc-100 border-b border-zinc-300 dark:border-zinc-600">
              Details
            </th>
          </tr>
        </thead>
        <tbody>
          {substitutions.map((row, index) => (
            <tr
              key={index}
              className="border-b border-zinc-200 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
            >
              <td className="px-4 py-3 text-sm font-mono text-zinc-900 dark:text-zinc-100">
                {row.part_number}
              </td>
              <td className="px-4 py-3 text-sm text-zinc-900 dark:text-zinc-100">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    row.type === "Original"
                      ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                      : row.type === "Packaging Substitute"
                      ? "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400"
                      : "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400"
                  }`}
                >
                  {row.type}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-zinc-600 dark:text-zinc-400">
                {row.details}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="min-h-screen bg-zinc-50 font-sans dark:bg-zinc-900 py-12 px-4">
      <main className="max-w-4xl mx-auto">
        <div className="bg-white dark:bg-zinc-800 rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-8">
            Component Substitution Finder
          </h1>

          <div className="space-y-6">
            {/* Brand Selector */}
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Brand
              </label>
              <select
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                className="w-full px-4 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="yageo">Yageo</option>
              </select>
            </div>

            {/* MPN Input */}
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Enter MPN(s) - One per line
              </label>
              <div className="space-y-2">
                <textarea
                  value={mpnInput}
                  onChange={(e) => setMpnInput(e.target.value)}
                  placeholder="e.g., RC0603FR-0710KL&#10;CC0603KRX5R7BB475&#10;RT0603DRD07127RL"
                  rows={5}
                  className="w-full px-4 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleSearch}
                    disabled={loading}
                    className="flex-1 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-zinc-400 transition-colors font-medium"
                  >
                    {loading ? "Processing..." : "Generate Substitutions"}
                  </button>
                  <button
                    onClick={handleExportToExcel}
                    disabled={loading}
                    className="flex-1 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-zinc-400 transition-colors font-medium flex items-center justify-center gap-2"
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    {loading ? "Exporting..." : "Export to Excel"}
                  </button>
                </div>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-600 dark:text-red-400">
                  {error}
                </p>
              </div>
            )}

            {/* Results */}
            {batchResults.length > 0 && (
              <div className="mt-8">
                <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
                  Results ({batchResults.length} MPN
                  {batchResults.length > 1 ? "s" : ""})
                </h2>

                {batchResults.length === 1 ? (
                  // Single result - show table directly
                  <div className="space-y-4">
                    <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                      <p className="text-sm text-blue-900 dark:text-blue-100">
                        <span className="font-semibold">MPN:</span>{" "}
                        {batchResults[0].mpn}
                        <span className="ml-4 font-semibold">Series:</span>{" "}
                        {batchResults[0].series}
                        <span className="ml-4 font-semibold">
                          Substitutions:
                        </span>{" "}
                        {batchResults[0].substitutions.length}
                      </p>
                    </div>
                    {renderSubstitutionTable(batchResults[0].substitutions)}
                  </div>
                ) : (
                  // Multiple results - show accordions
                  <div className="space-y-3">
                    {batchResults.map((result, index) => (
                      <div
                        key={index}
                        className="border border-zinc-300 dark:border-zinc-600 rounded-lg overflow-hidden"
                      >
                        <button
                          onClick={() => toggleAccordion(index)}
                          className="w-full px-4 py-2.5 bg-zinc-50 dark:bg-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-600 transition-colors flex items-center justify-between text-sm"
                        >
                          <div className="flex items-center gap-3 text-left">
                            <span className="font-mono font-medium text-zinc-900 dark:text-zinc-100">
                              {result.mpn}
                            </span>
                            <span className="text-xs text-zinc-500 dark:text-zinc-400">
                              Series: {result.series}
                            </span>
                            <span className="text-xs text-zinc-500 dark:text-zinc-400">
                              {result.substitutions.length} substitution
                              {result.substitutions.length > 1 ? "s" : ""}
                            </span>
                          </div>
                          <svg
                            className={`w-4 h-4 text-zinc-500 dark:text-zinc-400 transition-transform flex-shrink-0 ${
                              openAccordions.has(index) ? "rotate-180" : ""
                            }`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 9l-7 7-7-7"
                            />
                          </svg>
                        </button>
                        {openAccordions.has(index) && (
                          <div className="p-4 bg-white dark:bg-zinc-800">
                            {renderSubstitutionTable(result.substitutions)}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
