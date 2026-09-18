import type { LlmResearch } from "@/types/api";

interface Props {
  research: LlmResearch | null;
}

function Section({ title, items }: { title: string; items: string[] }): JSX.Element | null {
  if (items.length === 0) return null;
  return (
    <div className="mb-4">
      <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
        {title}
      </h3>
      <ul className="list-inside list-disc space-y-1 text-sm text-slate-200">
        {items.map((item, i) => (
          <li key={`${title}-${i}`}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export function ResearchPanel({ research }: Props): JSX.Element {
  if (!research) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <h2 className="mb-4 text-xl font-semibold">Research</h2>
        <p className="text-sm text-slate-500">No LLM research recorded for this fixture.</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
      <h2 className="mb-4 text-xl font-semibold">Research</h2>
      <Section title="Injuries" items={research.injuries} />
      <Section title="Form" items={research.form_notes} />
      <Section title="Tactical" items={research.tactical_observations} />
      <Section title="Risk factors" items={research.risk_factors} />
      {research.raw_text && (
        <details className="mt-4 text-xs text-slate-500">
          <summary className="cursor-pointer">Raw LLM output</summary>
          <pre className="mt-2 whitespace-pre-wrap">{research.raw_text}</pre>
        </details>
      )}
    </div>
  );
}
