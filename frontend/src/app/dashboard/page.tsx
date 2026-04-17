"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { fetchWithAuth } from "@/lib/api";
import { 
  LogOut, 
  UploadCloud, 
  FileJson, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Loader2,
  Trash2,
  Mail,
  Zap
} from "lucide-react";

type UserStats = {
  verifications_used: number;
  verifications_limit: number;
  plan: string;
  usage_percent: number;
};

type UserData = {
  email: string;
  full_name: string;
};

type VerificationResult = {
  email: string;
  status: "valid" | "invalid" | "disposable" | "catch_all" | "role_based" | "free_email" | "unknown" | "risky";
  is_disposable: boolean;
  is_catch_all: boolean;
  is_role_based: boolean;
  is_free_email: boolean;
  smtp_check: boolean;
  mx_found: boolean;
  score: number;
};

export default function Dashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [user, setUser] = useState<UserData | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);

  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<VerificationResult[]>([]);
  const [errorMSG, setErrorMSG] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoadingStats(true);
      const [statsRes, userRes] = await Promise.all([
        fetchWithAuth("/stats"),
        fetchWithAuth("/me")
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (userRes.ok) setUser(await userRes.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingStats(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === "application/json" || selectedFile.name.endsWith(".json")) {
        setFile(selectedFile);
        setErrorMSG("");
      } else {
        setFile(null);
        setErrorMSG("Please select a JSON file only.");
      }
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selectedFile = e.dataTransfer.files[0];
      if (selectedFile.type === "application/json" || selectedFile.name.endsWith(".json")) {
        setFile(selectedFile);
        setErrorMSG("");
      } else {
        setFile(null);
        setErrorMSG("Please select a JSON file only.");
      }
    }
  };

  const handleProcess = async () => {
    if (!file) return;

    setUploading(true);
    setResults([]);
    setErrorMSG("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetchWithAuth("/upload-verify", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        throw new Error(errorData?.detail || "Upload failed");
      }

      const data = await res.json();
      setResults(data.results || []);
      
      // Refresh stats
      loadDashboardData();
      
    } catch (err: any) {
      setErrorMSG(err.message || "An error occurred during verification.");
    } finally {
      setUploading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setResults([]);
    setErrorMSG("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'valid':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800">
            <CheckCircle className="w-3.5 h-3.5" /> Valid
          </span>
        );
      case 'invalid':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800">
            <XCircle className="w-3.5 h-3.5" /> Invalid
          </span>
        );
      case 'disposable':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400 border border-orange-200 dark:border-orange-800">
            <Trash2 className="w-3.5 h-3.5" /> Disposable
          </span>
        );
      case 'catch_all':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
            <AlertTriangle className="w-3.5 h-3.5" /> Catch-All
          </span>
        );
      case 'role_based':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400 border border-purple-200 dark:border-purple-800">
            <Mail className="w-3.5 h-3.5" /> Role-Based
          </span>
        );
      case 'free_email':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
            <Mail className="w-3.5 h-3.5" /> Free Provider
          </span>
        );
      case 'unknown':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400 border border-gray-200 dark:border-gray-700">
            <Loader2 className="w-3.5 h-3.5" /> Unknown
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-800">
            <AlertTriangle className="w-3.5 h-3.5" /> Risky
          </span>
        );
    }
  };

  if (loadingStats) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
      {/* Top Navbar */}
      <header className="bg-white/80 dark:bg-card-bg/80 backdrop-blur-md border-b border-border-color sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-primary/20 text-primary p-2 rounded-xl">
              <Zap className="w-5 h-5 fill-primary" />
            </div>
            <span className="font-bold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-500">
              EmailVerifier PRO
            </span>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="hidden sm:block text-sm text-right">
              <p className="font-bold text-foreground">{user?.full_name}</p>
              <p className="text-slate-500 text-xs font-medium">{user?.email}</p>
            </div>
            <button 
              onClick={handleLogout}
              className="p-2.5 text-slate-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 rounded-xl transition-all duration-200 active:scale-95"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column: Stats & Upload */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Stats Card */}
            <div className="bg-white dark:bg-card-bg rounded-2xl border border-border-color p-8 shadow-xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-bl-full -mr-10 -mt-10 blur-3xl group-hover:bg-primary/10 transition-colors"></div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-6 relative z-10">Verification Usage</h3>
              <div className="relative z-10">
                <div className="flex items-end gap-2 mb-2">
                  <span className="text-5xl font-black tracking-tighter">{stats?.verifications_used}</span>
                  <span className="text-slate-400 mb-2 font-bold">/ {stats?.verifications_limit}</span>
                </div>
                
                <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3 mt-6">
                  <div 
                    className={`h-3 rounded-full transition-all duration-700 ease-out ${stats && stats.usage_percent > 90 ? 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.4)]' : 'bg-primary shadow-[0_0_12px_rgba(var(--primary-rgb),0.4)]'}`}
                    style={{ width: `${Math.min(stats?.usage_percent || 0, 100)}%` }}
                  ></div>
                </div>
                <div className="flex justify-between items-center mt-3">
                  <p className="text-xs text-slate-400 font-bold">Plan Type</p>
                  <p className="text-xs font-black uppercase text-primary bg-primary/10 px-2 py-0.5 rounded italic">{stats?.plan}</p>
                </div>
              </div>
            </div>

            {/* Upload Card */}
            <div className="bg-white dark:bg-card-bg rounded-2xl border border-border-color p-8 shadow-xl transition-all duration-300 hover:shadow-2xl">
              <h2 className="text-2xl font-black mb-2 tracking-tight">Bulk Verify</h2>
              <p className="text-sm text-slate-500 mb-8 font-medium">Verify entire lists with 99.9% accuracy.</p>
              
              {!file ? (
                <div 
                  className="border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl p-10 text-center hover:bg-slate-50 dark:hover:bg-slate-900/40 transition-all cursor-pointer group hover:border-primary/50"
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="w-16 h-16 bg-slate-50 dark:bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 border border-border-color">
                    <UploadCloud className="w-8 h-8 text-slate-400 group-hover:text-primary transition-colors" />
                  </div>
                  <p className="text-sm font-bold mb-1 text-foreground">Drop JSON here</p>
                  <p className="text-xs text-slate-400 font-medium">Auto-detection enabled</p>
                  <input 
                    type="file" 
                    accept=".json,application/json" 
                    className="hidden" 
                    ref={fileInputRef}
                    onChange={handleFileChange}
                  />
                </div>
              ) : (
                <div className="border border-primary/20 bg-primary/5 rounded-2xl p-5 flex items-center justify-between animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <div className="flex items-center gap-4 overflow-hidden">
                    <div className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center flex-shrink-0">
                      <FileJson className="w-6 h-6 text-primary" />
                    </div>
                    <div className="overflow-hidden">
                      <p className="text-sm font-bold truncate text-foreground">{file.name}</p>
                      <p className="text-xs text-slate-500 font-bold">{(file.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>
                  <button 
                    onClick={clearFile}
                    className="p-2.5 text-slate-400 hover:text-red-500 hover:bg-white dark:hover:bg-red-900/20 rounded-xl transition-all duration-200"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              )}

              {errorMSG && (
                <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-200 dark:border-red-900/30">
                  <p className="text-sm text-red-600 dark:text-red-400 font-bold flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 flex-shrink-0" /> {errorMSG}
                  </p>
                </div>
              )}

              <button
                onClick={handleProcess}
                disabled={!file || uploading}
                className="w-full mt-8 flex items-center justify-center gap-3 bg-foreground text-background py-4 px-6 rounded-2xl font-black text-lg transition-all hover:bg-primary hover:text-white disabled:opacity-50 disabled:bg-slate-200 dark:disabled:bg-slate-800 shadow-xl hover:shadow-primary/30 active:scale-95 duration-200"
              >
                {uploading ? (
                  <><Loader2 className="w-6 h-6 animate-spin" /> ANALYZING...</>
                ) : (
                  <>START VERIFICATION</>
                )}
              </button>
            </div>
          </div>

          {/* Right Column: Results Table */}
          <div className="lg:col-span-8">
            <div className="bg-white dark:bg-card-bg rounded-2xl border border-border-color shadow-xl overflow-hidden flex flex-col h-full min-h-[600px]">
              <div className="p-8 border-b border-border-color bg-slate-50/50 dark:bg-slate-900/20 flex justify-between items-center backdrop-blur-sm sticky top-0 z-20">
                <div>
                  <h2 className="text-2xl font-black flex items-center gap-3 tracking-tight">
                    <Mail className="w-7 h-7 text-primary" /> Delivery Insights
                  </h2>
                  <p className="text-sm text-slate-400 font-bold mt-1 uppercase tracking-widest">Real-time SMTP intelligence</p>
                </div>
                {results.length > 0 && (
                  <div className="flex gap-2">
                    <span className="text-xs font-black bg-slate-900 text-white dark:bg-white dark:text-black px-4 py-2 rounded-full uppercase tracking-tighter shadow-lg">
                      {results.length} EMAILS
                    </span>
                  </div>
                )}
              </div>
              
              <div className="flex-1 overflow-auto">
                {results.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center p-20 text-center group">
                    <div className="w-24 h-24 bg-slate-50 dark:bg-slate-800 rounded-3xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500 border border-border-color shadow-inner">
                      <Zap className="w-12 h-12 text-slate-200 dark:text-slate-700" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-400">Awaiting Data Core</h3>
                    <p className="text-sm text-slate-500 max-w-xs mt-2 font-medium">Upload a valid JSON list to initialize the verification engine sequence.</p>
                  </div>
                ) : (
                  <table className="w-full text-left text-sm whitespace-nowrap">
                    <thead className="bg-slate-50/80 dark:bg-slate-900/80 sticky top-0 border-b border-border-color z-10 backdrop-blur-sm">
                      <tr>
                        <th className="px-8 py-5 font-black text-slate-400 uppercase tracking-widest text-[10px]">Recipient</th>
                        <th className="px-8 py-5 font-black text-slate-400 uppercase tracking-widest text-[10px]">Classification</th>
                        <th className="px-8 py-5 font-black text-slate-400 uppercase tracking-widest text-[10px]">Technical Specs</th>
                        <th className="px-8 py-5 font-black text-slate-400 uppercase tracking-widest text-[10px]">Score</th>
                        <th className="px-8 py-5 font-black text-slate-400 uppercase tracking-widest text-[10px]">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border-color">
                      {results.map((r, i) => (
                        <tr key={i} className="hover:bg-primary/[0.02] dark:hover:bg-primary/[0.05] transition-colors group">
                          <td className="px-8 py-6">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-[10px] font-black text-slate-400 uppercase">
                                {r.email.slice(0, 2)}
                              </div>
                              <span className="font-bold text-foreground tracking-tight" title={r.email}>
                                {r.email}
                              </span>
                            </div>
                          </td>
                          <td className="px-8 py-6">
                            <div className="flex flex-wrap gap-1">
                              {r.is_free_email && (
                                <span className="px-2 py-0.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-[10px] font-black text-slate-500 uppercase tracking-tighter">FREE</span>
                              )}
                              {r.is_role_based && (
                                <span className="px-2 py-0.5 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 text-[10px] font-black uppercase tracking-tighter">ROLE</span>
                              )}
                              {r.is_disposable && (
                                <span className="px-2 py-0.5 rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 text-[10px] font-black uppercase tracking-tighter">TRASH</span>
                              )}
                              {r.is_catch_all && (
                                <span className="px-2 py-0.5 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-[10px] font-black uppercase tracking-tighter">CATCH-ALL</span>
                              )}
                              {!r.is_disposable && !r.is_catch_all && !r.is_role_based && !r.is_free_email && r.mx_found && (
                                <span className="px-2 py-0.5 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 text-[10px] font-black uppercase tracking-tighter">BUSINESS</span>
                              )}
                            </div>
                          </td>
                          <td className="px-8 py-6">
                            <div className="flex items-center gap-4">
                              <div className="flex flex-col items-center">
                                <span className={`text-[10px] font-black uppercase tracking-widest mb-1 ${r.mx_found ? 'text-green-500' : 'text-red-500'}`}>MX</span>
                                <div className={`w-2 h-2 rounded-full ${r.mx_found ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500'}`} />
                              </div>
                              <div className="w-[1px] h-6 bg-border-color" />
                              <div className="flex flex-col items-center">
                                <span className={`text-[10px] font-black uppercase tracking-widest mb-1 ${r.smtp_check ? 'text-green-500' : 'text-slate-300 dark:text-slate-700'}`}>SMTP</span>
                                <div className={`w-2 h-2 rounded-full ${r.smtp_check ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-slate-200 dark:bg-slate-800'}`} />
                              </div>
                            </div>
                          </td>
                          <td className="px-8 py-6">
                            <div className="flex flex-col gap-1 w-24">
                              <div className="flex justify-between items-end">
                                <span className={`text-sm font-black tracking-tighter ${r.score >= 80 ? 'text-green-600' : r.score >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                                  {r.score}%
                                </span>
                                <span className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Trust</span>
                              </div>
                              <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                                <div 
                                  className={`h-full rounded-full transition-all duration-1000 ${r.score >= 80 ? 'bg-green-500' : r.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                  style={{ width: `${r.score}%` }}
                                ></div>
                              </div>
                            </div>
                          </td>
                          <td className="px-8 py-6">
                            {getStatusBadge(r.status)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
              
              {results.length > 0 && (
                <div className="p-4 border-t border-border-color bg-slate-50/30 dark:bg-slate-900/30 flex items-center justify-between">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Classification Engine v2.4.0-Stable</p>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    <span className="text-[10px] font-black text-green-500 uppercase tracking-widest">Secure Cloud Native Deployment</span>
                  </div>
                </div>
              )}
            </div>
          </div>
          
        </div>
      </main>
    </div>
  );
}
