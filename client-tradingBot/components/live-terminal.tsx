'use client'

import { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/card'
import { OrderLog } from './trading-dashboard'

interface LiveTerminalProps {
  logs: OrderLog[]
}

export function LiveTerminal({ logs }: LiveTerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [logs])

  return (
    <Card className="bg-black border-zinc-800 h-full flex flex-col font-mono text-sm">
      <div className="px-4 py-2 border-b border-zinc-800 bg-zinc-950">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
          <span className="text-emerald-400">Live Terminal</span>
          <span className="text-zinc-600 text-xs ml-auto">{logs.length} events</span>
        </div>
      </div>

      <div
        ref={terminalRef}
        className="flex-1 overflow-y-auto p-3 space-y-1 text-zinc-300"
      >
        {logs.length === 0 ? (
          <div className="text-zinc-600 text-xs py-4">
            &gt; Waiting for orders...
          </div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="space-y-1">
              <div className={`text-xs ${
                log.type === 'request'
                  ? 'text-blue-400'
                  : log.type === 'error'
                    ? 'text-red-400'
                    : 'text-emerald-400'
              }`}>
                <span className="text-zinc-600">{'>'}</span> {log.type.toUpperCase()} {log.timestamp}
              </div>
              <div className="text-xs text-zinc-400 ml-3 bg-zinc-950 p-2 rounded border border-zinc-800">
                <pre className="whitespace-pre-wrap wrap-break-word">
                  {JSON.stringify(log.data, null, 2)}
                </pre>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="px-4 py-2 border-t border-zinc-800 bg-zinc-950 text-xs text-zinc-600">
        Connected to: <span className="text-emerald-400">http://localhost:8000</span>
      </div>
    </Card>
  )
}
