// apps/dashboard/src/lib/websocket.ts
export function useLivePredictions(matchIds: string[]) {
  const [updates, setUpdates] = useState<Record<string, PredictionUpdate>>({});

  useEffect(() => {
    const ws = new WebSocket(`wss://api.yourdomain.com/ws/predictions`);

    ws.onopen = () => {
      ws.send(JSON.stringify({ action: "subscribe", match_ids: matchIds }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setUpdates((prev) => ({ ...prev, [data.match_id]: data }));
    };

    return () => ws.close();
  }, [matchIds.join(",")]);

  return updates;
}
