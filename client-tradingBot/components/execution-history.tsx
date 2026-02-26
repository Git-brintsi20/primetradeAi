'use client'

import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ExecutionOrder } from './trading-dashboard'

interface ExecutionHistoryProps {
  orders: ExecutionOrder[]
}

export function ExecutionHistory({ orders }: ExecutionHistoryProps) {
  const getStatusColor = (status: ExecutionOrder['status']) => {
    switch (status) {
      case 'Filled':
        return 'bg-emerald-900 text-emerald-100'
      case 'Pending':
        return 'bg-yellow-900 text-yellow-100'
      case 'Failed':
        return 'bg-red-900 text-red-100'
      default:
        return 'bg-zinc-800 text-zinc-100'
    }
  }

  const getSideColor = (side: ExecutionOrder['side']) => {
    return side === 'BUY' ? 'text-emerald-400' : 'text-red-400'
  }

  const formatPrice = (price: number | null) => {
    return price ? `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '-'
  }

  /** Display a quantity preserving significant decimal places. */
  const formatQty = (qty: number) => {
    return qty < 1 ? qty.toPrecision(3) : qty.toFixed(2)
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      hour12: false
    })
  }

  return (
    <Card className="bg-zinc-900 border-zinc-800 h-full flex flex-col">
      <div className="p-4 border-b border-zinc-800">
        <h2 className="text-lg font-semibold">Execution History</h2>
        <p className="text-xs text-zinc-500 mt-1">{orders.length} order(s)</p>
      </div>

      <div className="flex-1 overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-zinc-800 hover:bg-transparent">
              <TableHead className="text-zinc-400">Order ID</TableHead>
              <TableHead className="text-zinc-400">Symbol</TableHead>
              <TableHead className="text-zinc-400">Side</TableHead>
              <TableHead className="text-zinc-400">Type</TableHead>
              <TableHead className="text-zinc-400 text-right">Qty</TableHead>
              <TableHead className="text-zinc-400 text-right">Price</TableHead>
              <TableHead className="text-zinc-400">Status</TableHead>
              <TableHead className="text-zinc-400">Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {orders.length === 0 ? (
              <TableRow className="border-zinc-800">
                <TableCell colSpan={8} className="text-center text-zinc-500 py-8">
                  No orders yet
                </TableCell>
              </TableRow>
            ) : (
              orders.map((order) => (
                <TableRow key={order.id} className="border-zinc-800 hover:bg-zinc-800/50">
                  <TableCell className="font-mono text-xs text-zinc-500">
                    {('orderId' in order && order.orderId) || '-'}
                  </TableCell>
                  <TableCell className="font-mono text-sm">{order.symbol}</TableCell>
                  <TableCell className={`font-semibold ${getSideColor(order.side)}`}>
                    {order.side}
                  </TableCell>
                  <TableCell className="text-sm text-zinc-300">
                    {order.type}
                  </TableCell>
                  <TableCell className="text-right text-sm font-mono">
                    {formatQty(order.quantity)}
                  </TableCell>
                  <TableCell className="text-right text-sm font-mono text-zinc-300">
                    {formatPrice(order.price)}
                  </TableCell>
                  <TableCell>
                    <Badge className={`text-xs ${getStatusColor(order.status)}`}>
                      {order.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-zinc-500">
                    {formatTime(order.timestamp)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </Card>
  )
}
