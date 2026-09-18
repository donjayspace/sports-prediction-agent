import Link from "next/link";

export default function GlobalNotFound(): JSX.Element {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="mb-4 text-6xl font-bold text-slate-700">404</h1>
        <p className="mb-6 text-slate-400">Page not found</p>
        <Link
          href="/"
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500"
        >
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}
