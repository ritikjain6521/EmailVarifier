import Link from "next/link";
import { CheckCircle, Shield, Zap } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col justify-center">
      {/* Background blobs */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-2xl opacity-20 animate-blob dark:opacity-10"></div>
      <div className="absolute top-0 -right-4 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-2xl opacity-20 animate-blob animation-delay-2000 dark:opacity-10"></div>
      <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-2xl opacity-20 animate-blob animation-delay-4000 dark:opacity-10"></div>

      <main className="relative z-10 flex flex-col items-center max-w-5xl mx-auto px-6 py-20 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 mb-8 text-sm font-medium rounded-full bg-primary/10 text-primary ring-1 ring-inset ring-primary/20">
          <Zap className="w-4 h-4" />
          <span>v2.0 is now live</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-foreground mb-6">
          Verify Emails with <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-600">
            Absolute Precision
          </span>
        </h1>
        
        <p className="max-w-2xl text-lg text-slate-600 dark:text-slate-400 mb-10 leading-relaxed">
          The most robust and lightning-fast email verification system. 
          Catch disposables, role-based, and invalid syntax in milliseconds. 
          Upload a JSON bundle and let our asynchronous engine handle the rest.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 mb-16 w-full justify-center">
          <Link href="/signup" className="flex items-center justify-center px-8 py-4 text-base font-medium text-white bg-primary hover:bg-primary-hover rounded-xl shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5 duration-200">
            Get Started For Free
          </Link>
          <Link href="/login" className="flex items-center justify-center px-8 py-4 text-base font-medium text-foreground bg-white dark:bg-card-bg border border-border-color rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-all duration-200">
            Sign In to Dashboard
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left w-full mt-10">
          {[
            {
              title: "Lightning Fast",
              desc: "Fully asynchronous processing backed by FastAPI to verify hundreds of emails per second.",
              icon: <Zap className="w-6 h-6 text-yellow-500" />
            },
            {
              title: "Deep SMTP Checks",
              desc: "Verifies the actual inbox existence without sending an email. We connect cleanly and back out safely.",
              icon: <Shield className="w-6 h-6 text-green-500" />
            },
            {
              title: "JSON Upload Support",
              desc: "Effortlessly upload JSON payloads directly into your dashboard and immediately view the full verification status.",
              icon: <CheckCircle className="w-6 h-6 text-primary" />
            }
          ].map((feature, i) => (
            <div key={i} className="p-6 rounded-2xl bg-white dark:bg-card-bg border border-border-color shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center mb-4 border border-border-color">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-slate-600 dark:text-slate-400">{feature.desc}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
