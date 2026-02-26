'use client'

import { useState } from 'react'
import { OrderFormPanel } from './order-form-panel'
import { ExecutionHistory } from './execution-history'
import { LiveTerminal } from './live-terminal'

export interface OrderLog {
  id: string
  timestamp: string
  type: 'request' | 'response' | 'error'
  data: Record<string, unknown>
}

export interface ExecutionOrder {
  id: string
  orderId: string
  symbol: string
  side: 'BUY' | 'SELL'
  type: 'MARKET' | 'LIMIT' | 'STOP'
  quantity: number
  price: number | null
  status: 'Filled' | 'Pending' | 'Failed'
  timestamp: string
}

/** Map Binance order statuses to a UI-friendly badge label. */
export function mapBinanceStatus(
  apiStatus: string | undefined
): ExecutionOrder['status'] {
  switch (apiStatus?.toUpperCase()) {
    case 'FILLED':
    case 'PARTIALLY_FILLED':
      return 'Filled'
    case 'NEW':
    case 'PENDING_NEW':
      return 'Pending'
    default:
      return 'Failed'
  }
}

export function TradingDashboard() {
  const [orders, setOrders] = useState<ExecutionOrder[]>([])
  const [logs, setLogs] = useState<OrderLog[]>([])

  const handleAddOrder = (order: ExecutionOrder) => {
    setOrders((prev) => [order, ...prev])
  }

  const handleAddLog = (log: OrderLog) => {
    setLogs((prev) => [log, ...prev])
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 p-4 h-screen overflow-hidden">
      {/* Left Panel — Order Form */}
      <div className="lg:col-span-1 overflow-y-auto">
        <OrderFormPanel onOrderPlaced={handleAddOrder} onLogAdded={handleAddLog} />
      </div>

      {/* Right Panel — Execution History & Terminal */}
      <div className="lg:col-span-2 flex flex-col gap-4 overflow-hidden">
        <div className="flex-1 overflow-y-auto">
          <ExecutionHistory orders={orders} />
        </div>

        <div className="h-48 overflow-hidden">
          <LiveTerminal logs={logs} />
        </div>
      </div>
    </div>
  )
}
