"use client";

import { useState } from "react";

interface Substitution {
  part_number: string;
  type: string;
  details: string;
}

interface ApiResponse {
  brand: string;
  mpn: string;
  series: string;
  substitutions: Substitution[];
}

export default function Home() {
  const [brand, setBrand] = useState("yageo");
  const [mpn, setMpn] = useState("");
  const [results, setResults] = useState<Substitution[]>([]);
  const [series, setSeries] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const handleSearch = async () => {
    if (!mpn.trim()) return;

    setLoading(true);
    setError("");
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/generate?brand=${brand}&mpn=${mpn}`
      );
      const data: ApiResponse = await response.json();
      console.log("API Response:", data);
      
      if (data.series === "UNKNOWN") {
        setError("Unknown part series. Please check the MPN.");
        setResults([]);
        setSeries("");
      } else {
        setResults(data.substitutions || []);
        setSeries(data.series);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      setError("Failed to connect to the API. Make sure the backend is running.");
      setResults([]);
      setSeries("");
    } finally {
      setLoading(false);
    }
  };

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
                Enter MPN
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={mpn}
                  onChange={(e) => setMpn(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                  placeholder="e.g., RC0603FR-0710KL"
                  className="flex-1 px-4 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-zinc-400 transition-colors font-medium"
                >
                  {loading ? "Searching..." : "Search"}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            {/* Series Info */}
            {series && (
              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <p className="text-sm text-blue-900 dark:text-blue-100">
                  <span className="font-semibold">Detected Series:</span> {series}
                </p>
              </div>
            )}

            {/* Results Table */}
            {results.length > 0 && (
              <div className="mt-8">
                <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
                  Substitutions ({results.length})
                </h2>
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
                      {results.map((row, index) => (
                        <tr
                          key={index}
                          className="border-b border-zinc-200 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                        >
                          <td className="px-4 py-3 text-sm font-mono text-zinc-900 dark:text-zinc-100">
                            {row.part_number}
                          </td>
                          <td className="px-4 py-3 text-sm text-zinc-900 dark:text-zinc-100">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              row.type === "Original" 
                                ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                                : row.type === "Packaging Substitute"
                                ? "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400"
                                : "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400"
                            }`}>
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
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
