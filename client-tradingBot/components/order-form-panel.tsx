'use client'

import { useState, useMemo } from 'react'
import { toast } from 'sonner'
import { Card } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Spinner } from '@/components/ui/spinner'
import { ArrowUpCircle, ArrowDownCircle } from 'lucide-react'
import { API_BASE_URL } from '@/lib/config'
import { ExecutionOrder, OrderLog, mapBinanceStatus } from './trading-dashboard'

/* ------------------------------------------------------------------ */
/*  Types                                                             */
/* ------------------------------------------------------------------ */

interface OrderRequest {
  symbol: string
  side: 'BUY' | 'SELL'
  order_type: 'MARKET' | 'LIMIT' | 'STOP'
  quantity: number
  price: number | null
  stop_price: number | null
}

interface OrderFormPanelProps {
  onOrderPlaced: (order: ExecutionOrder) => void
  onLogAdded: (log: OrderLog) => void
}

/* ------------------------------------------------------------------ */
/*  Component                                                         */
/* ------------------------------------------------------------------ */

export function OrderFormPanel({ onOrderPlaced, onLogAdded }: OrderFormPanelProps) {
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY')
  const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT' | 'STOP'>('MARKET')
  const [symbol, setSymbol] = useState('BTCUSDT')
  const [quantity, setQuantity] = useState('')
  const [price, setPrice] = useState('')
  const [stopPrice, setStopPrice] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  /* ---------- Derived validation state ---------- */

  const needsPrice = orderType === 'LIMIT' || orderType === 'STOP'
  const needsStopPrice = orderType === 'STOP'

  const isFormValid = useMemo(() => {
    if (!symbol.trim()) return false
    if (!quantity || parseFloat(quantity) <= 0) return false
    if (needsPrice && (!price || parseFloat(price) <= 0)) return false
    if (needsStopPrice && (!stopPrice || parseFloat(stopPrice) <= 0)) return false
    return true
  }, [symbol, quantity, price, stopPrice, needsPrice, needsStopPrice])

  /* ---------- Submit handler ---------- */

  const handleSubmit = async () => {
    // Client-side guards (belt-and-suspenders — button is already disabled)
    if (!quantity || parseFloat(quantity) <= 0) {
      toast.error('Please enter a valid quantity.')
      return
    }
    if (needsPrice && (!price || parseFloat(price) <= 0)) {
      toast.error('Price is required for this order type.')
      return
    }
    if (needsStopPrice && (!stopPrice || parseFloat(stopPrice) <= 0)) {
      toast.error('Stop price is required for Stop-Limit orders.')
      return
    }

    const orderRequest: OrderRequest = {
      symbol: symbol.toUpperCase(),
      side,
      order_type: orderType,
      quantity: parseFloat(quantity),
      price: needsPrice ? parseFloat(price) : null,
      stop_price: needsStopPrice ? parseFloat(stopPrice) : null,
    }

    setIsLoading(true)

    // Log the outgoing request
    const requestLog: OrderLog = {
      id: `${Date.now()}-req`,
      timestamp: new Date().toISOString(),
      type: 'request',
      data: { method: 'POST', endpoint: '/order', body: orderRequest },
    }
    onLogAdded(requestLog)

    try {
      const res = await fetch(`${API_BASE_URL}/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderRequest),
      })

      const data = await res.json()

      // Log the response
      onLogAdded({
        id: `${Date.now()}-res`,
        timestamp: new Date().toISOString(),
        type: res.ok ? 'response' : 'error',
        data: { status: res.status, ...data },
      })

      if (!res.ok) {
        const detail = data?.detail || 'Order rejected by server.'
        toast.error(`Order failed — ${detail}`)

        onOrderPlaced({
          id: `${Date.now()}`,
          orderId: '-',
          symbol: orderRequest.symbol,
          side,
          type: orderType,
          quantity: parseFloat(quantity),
          price: needsPrice ? parseFloat(price) : null,
          status: 'Failed',
          timestamp: new Date().toISOString(),
        })
        return
      }

      // Build execution record from the real API response
      const order = data.order ?? {}
      const newOrder: ExecutionOrder = {
        id: `${Date.now()}`,
        orderId: String(order.orderId ?? '-'),
        symbol: order.symbol ?? orderRequest.symbol,
        side: order.side ?? side,
        type: order.type ?? orderType,
        quantity: parseFloat(order.executedQty ?? order.origQty ?? quantity),
        price: order.avgPrice ? parseFloat(order.avgPrice) : null,
        status: mapBinanceStatus(order.status),
        timestamp: new Date().toISOString(),
      }

      onOrderPlaced(newOrder)
      toast.success(
        `Order #${newOrder.orderId} placed — ${newOrder.status}`,
        { description: `${newOrder.side} ${newOrder.quantity} ${newOrder.symbol}` }
      )

      // Reset inputs on success
      setQuantity('')
      setPrice('')
      setStopPrice('')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Network error'
      toast.error(`Request failed — ${message}`)

      onLogAdded({
        id: `${Date.now()}-err`,
        timestamp: new Date().toISOString(),
        type: 'error',
        data: { error: message },
      })
    } finally {
      setIsLoading(false)
    }
  }

  /* ---------- Render ---------- */

  const buttonColor =
    side === 'BUY'
      ? 'bg-[#2ebd85] hover:bg-[#26a674]'
      : 'bg-[#f6465d] hover:bg-[#d93b50]'

  return (
    <Card className="bg-zinc-900 border-zinc-800 h-full">
      <div className="p-4 space-y-4">
        <h2 className="text-lg font-semibold">Place Order</h2>

        {/* Buy / Sell Toggle */}
        <Tabs value={side} onValueChange={(v) => setSide(v as typeof side)}>
          <TabsList className="w-full bg-zinc-800">
            <TabsTrigger value="BUY" className="flex-1 data-[state=active]:bg-[#2ebd85]">
              <ArrowUpCircle className="w-4 h-4 mr-2" />
              BUY
            </TabsTrigger>
            <TabsTrigger value="SELL" className="flex-1 data-[state=active]:bg-[#f6465d]">
              <ArrowDownCircle className="w-4 h-4 mr-2" />
              SELL
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Order Type */}
        <div className="space-y-2">
          <Label className="text-zinc-400">Order Type</Label>
          <Select
            value={orderType}
            onValueChange={(v) => setOrderType(v as typeof orderType)}
          >
            <SelectTrigger className="bg-zinc-800 border-zinc-700">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-zinc-800 border-zinc-700">
              <SelectItem value="MARKET">Market</SelectItem>
              <SelectItem value="LIMIT">Limit</SelectItem>
              <SelectItem value="STOP">Stop-Limit</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Symbol */}
        <div className="space-y-2">
          <Label className="text-zinc-400">Symbol</Label>
          <Input
            placeholder="BTCUSDT"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            className="bg-zinc-800 border-zinc-700"
          />
        </div>

        {/* Quantity */}
        <div className="space-y-2">
          <Label className="text-zinc-400">Quantity</Label>
          <Input
            type="number"
            placeholder="0.001"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            className="bg-zinc-800 border-zinc-700"
            min={0}
            step="0.001"
          />
        </div>

        {/* Price — visible for LIMIT and STOP */}
        {needsPrice && (
          <div className="space-y-2 animate-in fade-in-0 slide-in-from-top-1">
            <Label className="text-zinc-400">
              {orderType === 'STOP' ? 'Limit Price' : 'Price'}
            </Label>
            <Input
              type="number"
              placeholder="0.00"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="bg-zinc-800 border-zinc-700"
              min={0}
              step="0.01"
            />
          </div>
        )}

        {/* Stop Price — visible for STOP only */}
        {needsStopPrice && (
          <div className="space-y-2 animate-in fade-in-0 slide-in-from-top-1">
            <Label className="text-zinc-400">Stop Trigger Price</Label>
            <Input
              type="number"
              placeholder="0.00"
              value={stopPrice}
              onChange={(e) => setStopPrice(e.target.value)}
              className="bg-zinc-800 border-zinc-700"
              min={0}
              step="0.01"
            />
          </div>
        )}

        {/* Submit */}
        <Button
          onClick={handleSubmit}
          disabled={isLoading || !isFormValid}
          className={`w-full text-white font-semibold py-6 text-lg ${buttonColor} disabled:opacity-40`}
        >
          {isLoading ? (
            <>
              <Spinner className="w-4 h-4 mr-2" />
              Placing Order…
            </>
          ) : (
            `Place ${side} Order`
          )}
        </Button>

        {/* Info Box */}
        <div className="bg-zinc-800 p-3 rounded text-xs text-zinc-400 border border-zinc-700 space-y-1">
          <p>💡 <strong>Market</strong> — executes immediately at the best available price.</p>
          <p>📌 <strong>Limit</strong> — waits until the market reaches your specified price.</p>
          <p>🛡️ <strong>Stop-Limit</strong> — triggers a limit order when the stop price is hit.</p>
        </div>
      </div>
    </Card>
  )
}
