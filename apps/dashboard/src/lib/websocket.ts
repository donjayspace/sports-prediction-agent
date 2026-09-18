"use client";

import { useEffect, useRef, useState } from "react";

export interface PredictionUpdate {
  match_id: string;
  final_home: number;
  final_draw: number;
  final_away: number;
  updated_at: string;
}

interface UseLiveOptions {
  matchIds: string[];
  url?: string;
  reconnectDelayMs?: number;
}

interface UseLiveResult {
  updates: Record<string, PredictionUpdate>;
  connected: boolean;
}

export function useLivePredictions({
  matchIds,
  url = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:3001",
  reconnectDelayMs = 2000,
}: UseLiveOptions): UseLiveResult {
  const [updates, setUpdates] = useState<Record<string, PredictionUpdate>>({});
  const [connected, setConnected] = useState<boolean>(false);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const matchIdsKey = matchIds.join(",");

  useEffect(() => {
    let cancelled = false;

    const connect = (): void => {
      if (cancelled) return;

      const ws = new WebSocket(`${url}/ws/predictions`);
      socketRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        ws.send(JSON.stringify({ action: "subscribe", match_ids: matchIds }));
      };

      ws.onmessage = (event: MessageEvent<string>) => {
        try {
          const data = JSON.parse(event.data) as PredictionUpdate;
          if (!data.match_id) return;
          setUpdates((prev) => ({ ...prev, [data.match_id]: data }));
        } catch {
          // Malformed frames are ignored.
        }
      };

      ws.onclose = () => {
        setConnected(false);
        if (!cancelled) {
          reconnectTimerRef.current = setTimeout(connect, reconnectDelayMs);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connect();

    return () => {
      cancelled = true;
      if (reconnectTimerRef.current !== null) clearTimeout(reconnectTimerRef.current);
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, [url, matchIdsKey, reconnectDelayMs, matchIds]);

  return { updates, connected };
}
