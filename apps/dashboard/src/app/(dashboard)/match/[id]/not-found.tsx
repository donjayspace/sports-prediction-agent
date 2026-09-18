import Link from "next/link";

export default function MatchNotFound(): JSX.Element {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-12 text-center">
      <h2 className="mb-2 text-2xl font-bold">Match not found</h2>
      <p className="mb-6 text-slate-400">
        This fixture or its prediction may have been removed.
      </p>
      <Link
        href="/fixtures"
        className="rounded bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500"
      >
        Back to fixtures
      </Link>
    </div>
  );
}
