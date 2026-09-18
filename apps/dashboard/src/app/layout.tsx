import Link from "next/link";
import type { ReactNode } from "react";

const NAV = [
  { href: "/", label: "Overview" },
  { href: "/fixtures", label: "Fixtures" },
  { href: "/predictions", label: "Predictions" },
  { href: "/performance", label: "Performance" },
] as const;

export default function DashboardLayout({ children }: { children: ReactNode }): JSX.Element {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r border-slate-800 bg-slate-900 p-6">
        <h1 className="mb-8 text-xl font-bold">Sports Agent</h1>
        <nav className="space-y-2">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block rounded px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-white"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
