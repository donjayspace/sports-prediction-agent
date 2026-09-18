"use client";

import { useEffect } from "react";

interface Props {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function DashboardError({ error, reset }: Props): JSX.Element {
  useEffect(() => {
    console.error("Dashboard error:", error);
  }, [error]);

  return (
    <div className="rounded-lg border border-red-900 bg-red-950/40 p-8">
      <h2 className="mb-2 text-xl font-semibold text-red-300">Something went wrong</h2>
      <p className="mb-4 text-sm text-red-200">{error.message}</p>
      <button
        onClick={reset}
        className="rounded bg-red-600 px-4 py-2 text-sm font-medium hover:bg-red-500"
      >
        Try again
      </button>
    </div>
  );
}
