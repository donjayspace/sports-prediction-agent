export default async function MatchPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <main style={{ padding: 32 }}><h1>Event {id}</h1><p>Research evidence, model outputs, and evaluation history.</p></main>;
}
