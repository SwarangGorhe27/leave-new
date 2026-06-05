import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShoppingBag, Wallet, X,
  Plus, Minus,
  Star, Coffee, CreditCard, BadgeIndianRupee, ArrowUpCircle,
  Edit2, Trash2, ChefHat, Tag,
} from 'lucide-react';
import { Tabs } from '@components/ui';
import { cn } from '@utils/utils';
import { useUIStore } from '@store/uiStore';
import {
  useCanteenLocations, useMenuCategories, useMenuItems,
  useBreakSlots,
  useMyOrders, usePlaceOrder, useCancelOrder,
  useMyWallet, useWalletTransactions, useRechargeWallet, useKitchenDashboard,
  useUpdateOrderStatus,
  useAllMenuItems, useCreateMenuItem, useUpdateMenuItem, useDeleteMenuItem,
  useCreateMenuCategory, useDeleteMenuCategory,
  type CanteenLocation, type MenuItem, type CanteenBreakSlot,
  type CanteenWallet, type WalletTransaction,
} from '@hooks/useCanteen';

// ─── Helpers ─────────────────────────────────────

const statusColors: Record<string, string> = {
  DRAFT: 'bg-gray-100 text-gray-600',
  PLACED: 'bg-blue-100 text-blue-700',
  CONFIRMED: 'bg-indigo-100 text-indigo-700',
  PREPARING: 'bg-amber-100 text-amber-700',
  READY: 'bg-green-100 text-green-700',
  COLLECTED: 'bg-emerald-100 text-emerald-700',
  CANCELLED: 'bg-red-100 text-red-600',
  REFUNDED: 'bg-gray-100 text-gray-600',
};

interface CartItem {
  menuItem: MenuItem;
  quantity: number;
}

// ─── Order Menu (Employee order flow — Groniva-style) ────────────

function formatSlot(slot: CanteenBreakSlot): string {
  const today = new Date();
  const dd = String(today.getDate()).padStart(2, '0');
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const yyyy = today.getFullYear();
  const start = slot.slot_start.slice(0, 5);
  const end = slot.slot_end.slice(0, 5);
  return `${dd}-${mm}-${yyyy} ${start}-${end}`;
}

function OrderMenu({ locations }: { locations: CanteenLocation[] }) {
  const [selectedLocation, setSelectedLocation] = useState<string>(locations[0]?.id ?? '');
  const [selectedSlot, setSelectedSlot] = useState<string>('');
  const [cart, setCart] = useState<CartItem[]>([]);
  const [search, setSearch] = useState('');
  const [paymentMode, setPaymentMode] = useState<string>('WALLET');

  const { data: walletRaw } = useMyWallet();
  const wallet = walletRaw as CanteenWallet | undefined;
  const walletBalance = Number(wallet?.balance ?? 0);

  const { data: breakSlots = [] } = useBreakSlots(selectedLocation || undefined);
  const { data: categories = [] } = useMenuCategories(selectedLocation);
  const { data: items = [] } = useMenuItems(selectedLocation);
  const placeOrder = usePlaceOrder();

  // Auto-select first location when data loads
  useEffect(() => {
    if (locations.length > 0 && !selectedLocation) {
      setSelectedLocation(locations[0].id);
    }
  }, [locations, selectedLocation]);

  // Auto-select first available break slot
  useEffect(() => {
    if (breakSlots.length > 0 && !selectedSlot) {
      setSelectedSlot(breakSlots[0].id);
    }
  }, [breakSlots, selectedSlot]);

  const cartTotal = useMemo(
    () => cart.reduce((sum, c) => sum + c.menuItem.effective_price * c.quantity, 0),
    [cart],
  );

  const categoryMap = useMemo(
    () => Object.fromEntries(categories.map((c) => [c.id, c.name])),
    [categories],
  );

  const filteredItems = useMemo(
    () => !search ? items : items.filter((i) => i.name.toLowerCase().includes(search.toLowerCase())),
    [items, search],
  );

  function toggleItem(item: MenuItem) {
    setCart((prev) => {
      const existing = prev.find((c) => c.menuItem.id === item.id);
      if (existing) return prev.filter((c) => c.menuItem.id !== item.id);
      return [...prev, { menuItem: item, quantity: 1 }];
    });
  }

  function setQty(item: MenuItem, qty: number) {
    if (qty <= 0) {
      setCart((prev) => prev.filter((c) => c.menuItem.id !== item.id));
    } else {
      setCart((prev) => {
        const existing = prev.find((c) => c.menuItem.id === item.id);
        if (existing) return prev.map((c) => c.menuItem.id === item.id ? { ...c, quantity: qty } : c);
        return [...prev, { menuItem: item, quantity: qty }];
      });
    }
  }

  function handlePlaceOrder() {
    if (!cart.length || !selectedLocation) return;
    placeOrder.mutate(
      {
        canteen: selectedLocation,
        items: cart.map((c) => ({ menu_item: c.menuItem.id, quantity: c.quantity })),
        break_slot: selectedSlot || null,
        payment_mode: paymentMode,
      },
      { onSuccess: () => setCart([]) },
    );
  }

  if (!locations.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Coffee className="h-10 w-10 text-surface-300 dark:text-white/20" />
        <p className="mt-3 text-sm text-surface-500 dark:text-white/40">No canteen locations configured yet.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      {/* ── Controls bar ─────────────────────────── */}
      <div className="flex flex-wrap items-end gap-x-6 gap-y-3 border-b border-surface-100 bg-white px-5 py-4 dark:border-white/5 dark:bg-surface-900">
        {/* Location switcher */}
        {locations.length > 1 && (
          <div className="flex gap-2">
            {locations.map((loc) => (
              <button
                key={loc.id}
                onClick={() => { setSelectedLocation(loc.id); setSelectedSlot(''); }}
                className={cn(
                  'rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                  selectedLocation === loc.id
                    ? 'bg-surface-900 text-white dark:bg-white dark:text-surface-900'
                    : 'bg-surface-100 text-surface-600 hover:bg-surface-200 dark:bg-white/5 dark:text-white/60',
                )}
              >
                {loc.name}
              </button>
            ))}
          </div>
        )}

        {/* Break slot dropdown */}
        <div>
          <p className="mb-1.5 text-xs font-semibold text-surface-700 dark:text-white/70">Break Slot</p>
          <select
            value={selectedSlot}
            onChange={(e) => setSelectedSlot(e.target.value)}
            className="min-w-[220px] rounded-lg border border-surface-200 bg-white px-3 py-1.5 text-xs text-surface-800 shadow-sm focus:border-blue-400 focus:outline-none dark:border-white/10 dark:bg-surface-800 dark:text-white"
          >
            {breakSlots.length === 0 && <option value="">No slots available</option>}
            {breakSlots.map((slot) => (
              <option key={slot.id} value={slot.id}>
                {formatSlot(slot)}{slot.name ? ` — ${slot.name}` : ''}
              </option>
            ))}
          </select>
        </div>

        {/* Search */}
        <div className="ml-auto">
          <input
            type="text"
            placeholder="Search menu..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="rounded-lg border border-surface-200 bg-white px-3 py-1.5 text-xs text-surface-800 placeholder-surface-400 shadow-sm focus:border-blue-400 focus:outline-none dark:border-white/10 dark:bg-surface-800 dark:text-white"
          />
        </div>
      </div>

      {/* ── Menu grid ────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2">
        {filteredItems.map((item, idx) => {
          const inCart = cart.find((c) => c.menuItem.id === item.id);
          const checked = !!inCart;
          const qty = inCart?.quantity ?? 1;

          return (
            <motion.div
              key={item.id}
              layout
              className={cn(
                'flex items-center gap-3 border-b border-surface-100 p-3 dark:border-white/5',
                idx % 2 === 0 ? 'sm:border-r' : '',
              )}
            >
              {/* Row number */}
              <span className="w-5 shrink-0 text-center text-xs font-medium text-surface-400 dark:text-white/30">
                {idx + 1}
              </span>

              {/* Checkbox */}
              <input
                type="checkbox"
                checked={checked}
                onChange={() => toggleItem(item)}
                className="h-4 w-4 shrink-0 cursor-pointer accent-blue-600"
              />

              {/* Food image */}
              {item.image ? (
                <img
                  src={item.image}
                  alt={item.name}
                  className="h-16 w-16 shrink-0 rounded-lg object-cover"
                />
              ) : (
                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-lg bg-surface-100 dark:bg-white/5">
                  <Coffee className="h-6 w-6 text-surface-300 dark:text-white/20" />
                </div>
              )}

              {/* Info + stepper */}
              <div className="flex flex-1 flex-col gap-0.5 min-w-0">
                <p className="text-xs text-surface-500 dark:text-white/50">
                  <span className="font-semibold text-surface-700 dark:text-white/70">Menu Label : </span>
                  {item.name}
                  {item.is_featured && (
                    <Star className="ml-1 inline h-3 w-3 fill-amber-400 text-amber-400" />
                  )}
                </p>
                <p className="text-xs text-surface-500 dark:text-white/50">
                  <span className="font-semibold text-surface-700 dark:text-white/70">Meal Session : </span>
                  {item.category_name || categoryMap[item.category] || '—'}
                </p>
                <div className="mt-1.5 flex items-center gap-1">
                  <button
                    onClick={() => { if (checked) setQty(item, qty - 1); }}
                    disabled={!checked}
                    className="flex h-6 w-6 items-center justify-center rounded border border-red-300 bg-red-50 text-red-600 transition hover:bg-red-100 disabled:opacity-30 dark:border-red-800 dark:bg-red-950/20"
                  >
                    <Minus className="h-3 w-3" />
                  </button>
                  <span className="w-6 text-center text-xs font-bold text-surface-800 dark:text-white">
                    {checked ? qty : 1}
                  </span>
                  <button
                    onClick={() => checked ? setQty(item, qty + 1) : toggleItem(item)}
                    className="flex h-6 w-6 items-center justify-center rounded border border-green-300 bg-green-50 text-green-700 transition hover:bg-green-100 dark:border-green-800 dark:bg-green-950/20"
                  >
                    <Plus className="h-3 w-3" />
                  </button>
                </div>
              </div>

              {/* Price */}
              <div className="shrink-0 text-right">
                <p className="text-[10px] text-surface-400 dark:text-white/30">Price :</p>
                <p className="text-sm font-bold text-surface-900 dark:text-white">{item.effective_price}</p>
              </div>
            </motion.div>
          );
        })}

        {filteredItems.length === 0 && (
          <div className="col-span-full py-12 text-center text-sm text-surface-400 dark:text-white/30">
            No items available.
          </div>
        )}
      </div>

      {/* ── Grand Total + Place Order ─────────────── */}
      {/* ── Payment Method + Place Order ─────────── */}
      <div className="border-t border-surface-100 bg-white dark:border-white/5 dark:bg-surface-900">
        {/* Payment method row */}
        <div className="flex flex-wrap items-center gap-2 px-5 pt-3">
          <span className="text-xs font-semibold text-surface-500 dark:text-white/40">Pay via:</span>
          {([
            { value: 'WALLET', label: '💳 Wallet', sub: walletBalance > 0 ? `₹${walletBalance.toFixed(2)}` : 'Add money first' },
            { value: 'PAYROLL_DEDUCTION', label: '💼 Salary', sub: 'Deducted from payslip' },
            { value: 'UPI', label: '📱 UPI', sub: 'Google Pay / PhonePe' },
            { value: 'CASH', label: '💵 Cash', sub: 'At counter' },
          ] as const).map((pm) => (
            <button
              key={pm.value}
              type="button"
              onClick={() => setPaymentMode(pm.value)}
              className={cn(
                'flex flex-col rounded-xl border px-3 py-1.5 text-left transition-all',
                paymentMode === pm.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-surface-200 bg-surface-50 dark:border-white/10 dark:bg-white/5',
              )}
            >
              <span className={cn('text-xs font-semibold', paymentMode === pm.value ? 'text-blue-700 dark:text-blue-400' : 'text-surface-700 dark:text-white/60')}>
                {pm.label}
              </span>
              <span className="text-[10px] text-surface-400 dark:text-white/30">{pm.sub}</span>
            </button>
          ))}
        </div>
        {/* Total + button row */}
        <div className="flex items-center justify-between px-5 py-3">
          <div className="flex items-center gap-3">
            <span className="text-sm font-semibold text-surface-700 dark:text-white/70">Grand Total:</span>
            <span className="rounded-full bg-blue-100 px-3 py-0.5 text-sm font-bold text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
              ₹{cartTotal.toFixed(2)}
            </span>
            {paymentMode === 'WALLET' && cartTotal > 0 && walletBalance < cartTotal && (
              <span className="text-xs font-medium text-red-500">Insufficient balance</span>
            )}
          </div>
          {cart.length > 0 && (
            <button
              type="button"
              onClick={handlePlaceOrder}
              disabled={placeOrder.isPending || (paymentMode === 'WALLET' && cartTotal > walletBalance)}
              className="rounded-lg bg-green-600 px-4 py-1.5 text-xs font-semibold text-white shadow hover:bg-green-700 disabled:opacity-50"
            >
              {placeOrder.isPending ? 'Placing…' : `Place Order (${cart.length} item${cart.length > 1 ? 's' : ''})`}
            </button>
          )}
        </div>
        {placeOrder.isError && (
          <p className="px-5 pb-2 text-xs text-red-600 dark:text-red-400">
            {(placeOrder.error as Error)?.message ?? 'Failed to place order. Please try again.'}
          </p>
        )}
      </div>
    </div>
  );
}

// ─── My Orders ───────────────────────────────────

function MyOrdersList() {
  const { data: orders = [], isLoading } = useMyOrders();
  const cancelOrder = useCancelOrder();

  if (isLoading) {
    return (
      <div className="space-y-3 p-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-20 animate-pulse rounded-xl bg-surface-100 dark:bg-white/5" />
        ))}
      </div>
    );
  }

  if (!orders.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <ShoppingBag className="h-10 w-10 text-surface-300 dark:text-white/20" />
        <p className="mt-3 text-sm text-surface-500 dark:text-white/40">No orders yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 p-4">
      {orders.map((order) => (
        <div key={order.id} className="rounded-xl border border-surface-100 p-3 dark:border-white/5">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-surface-900 dark:text-white">{order.order_number}</span>
                <span className={cn('rounded-md px-2 py-0.5 text-xs font-medium', statusColors[order.status])}>{order.status}</span>
              </div>
              <p className="mt-0.5 text-xs text-surface-500 dark:text-white/40">
                {order.canteen_name} · {new Date(order.order_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}
              </p>
            </div>
            <div className="text-right">
              <span className="text-sm font-bold text-surface-900 dark:text-white">₹{order.employee_payable}</span>
              {order.pickup_token && order.status === 'READY' && (
                <p className="mt-0.5 text-xs font-bold text-green-600">Token: {order.pickup_token}</p>
              )}
            </div>
          </div>
          <div className="mt-2 flex flex-wrap gap-1">
            {order.items.map((item) => (
              <span key={item.id} className="rounded-md bg-surface-50 px-2 py-0.5 text-xs text-surface-600 dark:bg-white/5 dark:text-white/50">
                {item.item_name} ×{item.quantity}
              </span>
            ))}
          </div>
          {['PLACED', 'CONFIRMED'].includes(order.status) && (
            <button onClick={() => cancelOrder.mutate({ orderId: order.id })} className="mt-2 text-xs text-red-600 hover:underline dark:text-red-400">
              Cancel Order
            </button>
          )}
        </div>
      ))}
    </div>
  );
}

// ─── Wallet ──────────────────────────────────────

const TXN_LABEL: Record<string, string> = {
  CREDIT_RECHARGE: 'Wallet Recharge',
  CREDIT_REFUND: 'Order Refund',
  CREDIT_SUBSIDY: 'Company Subsidy',
  DEBIT_ORDER: 'Order Payment',
  DEBIT_EXPIRED: 'Balance Expired',
};

type UpiApp = 'gpay' | 'phonepe' | 'paytm' | 'other';

const UPI_APPS: { id: UpiApp; label: string }[] = [
  { id: 'gpay', label: 'Google Pay' },
  { id: 'phonepe', label: 'PhonePe' },
  { id: 'paytm', label: 'Paytm' },
  { id: 'other', label: 'Other UPI' },
];

function WalletView() {
  const { data: walletRaw, isLoading: walletLoading } = useMyWallet();
  const wallet = walletRaw as CanteenWallet | undefined;
  const { data: txnsRaw = [] } = useWalletTransactions();
  const transactions = txnsRaw as unknown as WalletTransaction[];
  const recharge = useRechargeWallet();

  const [showAdd, setShowAdd] = useState(false);
  const [method, setMethod] = useState<'UPI' | 'SALARY'>('UPI');
  const [upiApp, setUpiApp] = useState<UpiApp>('gpay');
  const [amount, setAmount] = useState('');
  const [upiRef, setUpiRef] = useState('');

  const balance = Number(wallet?.balance ?? 0);

  function handleRecharge() {
    const amt = parseFloat(amount);
    if (!amt || amt <= 0) return;
    recharge.mutate(
      { amount: amt, method, upi_ref: upiRef || undefined },
      {
        onSuccess: () => {
          setShowAdd(false);
          setAmount('');
          setUpiRef('');
        },
      },
    );
  }

  return (
    <div className="space-y-4 p-4">
      {/* ── Balance card ─────────────────────────── */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-green-600 to-emerald-700 p-5 text-white shadow-lg">
        <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-white/10" />
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wallet className="h-5 w-5 opacity-80" />
            <span className="text-sm font-medium opacity-80">Canteen Wallet</span>
          </div>
          <button
            type="button"
            onClick={() => setShowAdd((v) => !v)}
            className="flex items-center gap-1.5 rounded-xl bg-white/20 px-3 py-1.5 text-xs font-semibold backdrop-blur-sm transition-colors hover:bg-white/30"
          >
            {showAdd ? <X className="h-3.5 w-3.5" /> : <Plus className="h-3.5 w-3.5" />}
            {showAdd ? 'Cancel' : 'Add Money'}
          </button>
        </div>
        {walletLoading ? (
          <div className="mt-3 h-9 w-32 animate-pulse rounded-lg bg-white/20" />
        ) : (
          <p className="mt-3 text-4xl font-bold">₹{balance.toFixed(2)}</p>
        )}
        <p className="mt-0.5 text-xs opacity-60">Available Balance</p>
      </div>

      {/* ── Add Money Panel ──────────────────────── */}
      <AnimatePresence>
        {showAdd && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="rounded-2xl border border-surface-200/70 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-surface-800"
          >
            <h3 className="mb-4 text-sm font-semibold text-surface-900 dark:text-white">Add Money to Wallet</h3>

            {/* Method toggle */}
            <div className="mb-4 flex gap-2">
              {(['UPI', 'SALARY'] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setMethod(m)}
                  className={cn(
                    'flex flex-1 items-center justify-center gap-2 rounded-xl py-2.5 text-sm font-medium transition-colors',
                    method === m
                      ? 'bg-green-600 text-white'
                      : 'bg-surface-100 text-surface-600 dark:bg-white/5 dark:text-white/50',
                  )}
                >
                  {m === 'UPI' ? <><CreditCard className="h-4 w-4" /> UPI / QR</> : <><BadgeIndianRupee className="h-4 w-4" /> From Salary</>}
                </button>
              ))}
            </div>

            {/* Amount input */}
            <div className="mb-3">
              <label className="mb-1.5 block text-xs font-medium text-surface-700 dark:text-white/70">Amount (₹)</label>
              <input
                type="number"
                min="1"
                placeholder="Enter amount"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full rounded-xl border border-surface-300/70 bg-surface-0 px-3 py-2.5 text-sm text-surface-900 placeholder-surface-400 focus:border-green-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white"
              />
              <div className="mt-2 flex gap-2">
                {[100, 200, 500, 1000].map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    onClick={() => setAmount(String(preset))}
                    className="flex-1 rounded-lg bg-surface-100 py-1.5 text-xs font-semibold text-surface-600 hover:bg-surface-200 dark:bg-white/5 dark:text-white/50"
                  >
                    +₹{preset}
                  </button>
                ))}
              </div>
            </div>

            {/* UPI method */}
            {method === 'UPI' && (
              <>
                <div className="mb-3">
                  <label className="mb-1.5 block text-xs font-medium text-surface-700 dark:text-white/70">Pay via</label>
                  <div className="grid grid-cols-4 gap-2">
                    {UPI_APPS.map((app) => (
                      <button
                        key={app.id}
                        type="button"
                        onClick={() => setUpiApp(app.id)}
                        className={cn(
                          'rounded-xl border-2 px-2 py-2.5 text-center text-xs font-medium transition-all',
                          upiApp === app.id
                            ? 'border-green-500 bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                            : 'border-surface-200 bg-surface-50 text-surface-600 dark:border-white/10 dark:bg-white/5 dark:text-white/50',
                        )}
                      >
                        {app.label}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="mb-4">
                  <label className="mb-1.5 block text-xs font-medium text-surface-700 dark:text-white/70">
                    UPI Transaction ID <span className="font-normal text-surface-400">(optional)</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. T2025xxxxxxxxxxxx"
                    value={upiRef}
                    onChange={(e) => setUpiRef(e.target.value)}
                    className="w-full rounded-xl border border-surface-300/70 bg-surface-0 px-3 py-2.5 text-sm text-surface-900 placeholder-surface-400 focus:border-green-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white"
                  />
                </div>
              </>
            )}

            {/* Salary note */}
            {method === 'SALARY' && (
              <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-3 dark:border-amber-900/30 dark:bg-amber-900/10">
                <p className="text-xs leading-relaxed text-amber-800 dark:text-amber-400">
                  💡 The entered amount will be deducted from your next salary payment and instantly credited to your canteen wallet.
                </p>
              </div>
            )}

            <button
              type="button"
              onClick={handleRecharge}
              disabled={!amount || parseFloat(amount) <= 0 || recharge.isPending}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-green-600 py-3 text-sm font-semibold text-white transition-colors hover:bg-green-700 disabled:opacity-50"
            >
              <ArrowUpCircle className="h-4 w-4" />
              {recharge.isPending
                ? 'Processing…'
                : method === 'UPI'
                ? `Pay ₹${amount || '0'} via ${UPI_APPS.find((a) => a.id === upiApp)?.label ?? 'UPI'}`
                : `Add ₹${amount || '0'} from Salary`}
            </button>

            {recharge.isError && (
              <p className="mt-2 text-center text-xs text-red-600 dark:text-red-400">Payment failed. Please try again.</p>
            )}
            {recharge.isSuccess && (
              <p className="mt-2 text-center text-xs font-medium text-green-600 dark:text-green-400">✓ ₹{amount} added to wallet!</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Transaction History ───────────────────── */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-surface-400 dark:text-white/30">
          Transaction History
        </h3>
        <div className="mt-2 space-y-2">
          {transactions.map((txn) => {
            const isCredit = txn.transaction_type.startsWith('CREDIT');
            const amt = Number(txn.amount);
            const balAfter = Number(txn.balance_after);
            return (
              <div
                key={txn.id}
                className="flex items-center justify-between rounded-xl border border-surface-100 p-3 dark:border-white/5"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      'flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold',
                      isCredit
                        ? 'bg-green-100 text-green-600 dark:bg-green-900/20'
                        : 'bg-red-100 text-red-600 dark:bg-red-900/20',
                    )}
                  >
                    {isCredit ? '↑' : '↓'}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-surface-900 dark:text-white">
                      {TXN_LABEL[txn.transaction_type] ?? txn.transaction_type.replace(/_/g, ' ')}
                    </p>
                    <p className="text-xs text-surface-500 dark:text-white/40">
                      {new Date(txn.created_at).toLocaleString('en-IN', {
                        day: '2-digit', month: 'short', year: 'numeric',
                        hour: '2-digit', minute: '2-digit',
                      })}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={cn('text-sm font-bold', isCredit ? 'text-green-600' : 'text-red-600')}>
                    {isCredit ? '+' : '−'}₹{amt.toFixed(2)}
                  </span>
                  <p className="text-[10px] text-surface-400 dark:text-white/30">Bal ₹{balAfter.toFixed(2)}</p>
                </div>
              </div>
            );
          })}
          {transactions.length === 0 && (
            <div className="flex flex-col items-center py-10 text-center">
              <Wallet className="h-8 w-8 text-surface-300 dark:text-white/20" />
              <p className="mt-3 text-sm text-surface-500 dark:text-white/40">No transactions yet</p>
              <p className="mt-1 text-xs text-surface-400 dark:text-white/30">Add money to get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Kitchen View (Admin) ────────────────────────

function KitchenView({ locations }: { locations: CanteenLocation[] }) {
  const [selectedLocation, setSelectedLocation] = useState<string>(locations[0]?.id ?? '');
  const { data: dashboard } = useKitchenDashboard(selectedLocation || undefined);
  const updateStatus = useUpdateOrderStatus();

  const activeStatuses = ['PLACED', 'CONFIRMED', 'PREPARING', 'READY'];

  return (
    <div className="p-4">
      {/* Location selector */}
      {locations.length > 1 && (
        <div className="mb-4 flex gap-2">
          {locations.map((loc) => (
            <button
              key={loc.id}
              onClick={() => setSelectedLocation(loc.id)}
              className={cn(
                'rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                selectedLocation === loc.id
                  ? 'bg-surface-900 text-white dark:bg-white dark:text-surface-900'
                  : 'bg-surface-100 text-surface-600 dark:bg-white/5 dark:text-white/60',
              )}
            >
              {loc.name}
            </button>
          ))}
        </div>
      )}

      {/* Status columns */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {activeStatuses.map((statusKey) => {
          const data = dashboard?.[statusKey];
          return (
            <div key={statusKey} className="rounded-xl border border-surface-100 dark:border-white/5">
              <div className="flex items-center justify-between border-b border-surface-100 p-3 dark:border-white/5">
                <span className={cn('rounded-md px-2 py-0.5 text-xs font-semibold', statusColors[statusKey])}>
                  {data?.label ?? statusKey}
                </span>
                <span className="text-sm font-bold text-surface-600 dark:text-white/60">{data?.count ?? 0}</span>
              </div>
              <div className="max-h-[400px] space-y-2 overflow-y-auto p-2">
                {(data?.orders ?? []).map((order) => (
                  <div key={order.id} className="rounded-lg bg-surface-50 p-2 dark:bg-white/[0.02]">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-surface-900 dark:text-white">{order.order_number}</span>
                      <span className="text-xs text-surface-500 dark:text-white/40">{order.pickup_token}</span>
                    </div>
                    <p className="mt-0.5 text-xs text-surface-600 dark:text-white/50">{order.employee_name}</p>
                    <div className="mt-1 space-y-0.5">
                      {order.items.map((it) => (
                        <p key={it.id} className="text-xs text-surface-500 dark:text-white/40">
                          {it.item_name} ×{it.quantity}
                        </p>
                      ))}
                    </div>
                    {/* Action button */}
                    {statusKey === 'PLACED' && (
                      <button
                        onClick={() => updateStatus.mutate({ orderId: order.id, status: 'CONFIRMED' })}
                        className="mt-2 w-full rounded-md bg-indigo-600 px-2 py-1 text-xs font-medium text-white hover:bg-indigo-700"
                      >
                        Confirm
                      </button>
                    )}
                    {statusKey === 'CONFIRMED' && (
                      <button
                        onClick={() => updateStatus.mutate({ orderId: order.id, status: 'PREPARING' })}
                        className="mt-2 w-full rounded-md bg-amber-600 px-2 py-1 text-xs font-medium text-white hover:bg-amber-700"
                      >
                        Start Preparing
                      </button>
                    )}
                    {statusKey === 'PREPARING' && (
                      <button
                        onClick={() => updateStatus.mutate({ orderId: order.id, status: 'READY' })}
                        className="mt-2 w-full rounded-md bg-green-600 px-2 py-1 text-xs font-medium text-white hover:bg-green-700"
                      >
                        Mark Ready
                      </button>
                    )}
                    {statusKey === 'READY' && (
                      <button
                        onClick={() => updateStatus.mutate({ orderId: order.id, status: 'COLLECTED' })}
                        className="mt-2 w-full rounded-md bg-emerald-600 px-2 py-1 text-xs font-medium text-white hover:bg-emerald-700"
                      >
                        Collected
                      </button>
                    )}
                  </div>
                ))}
                {(data?.orders ?? []).length === 0 && (
                  <p className="py-4 text-center text-xs text-surface-300 dark:text-white/20">No orders</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Admin: Menu Management ──────────────────────

const ITEM_TYPE_LABELS: Record<string, { label: string; color: string }> = {
  VEG: { label: 'Veg', color: 'bg-green-100 text-green-700' },
  NON_VEG: { label: 'Non-Veg', color: 'bg-red-100 text-red-700' },
  EGG: { label: 'Egg', color: 'bg-yellow-100 text-yellow-700' },
  VEGAN: { label: 'Vegan', color: 'bg-emerald-100 text-emerald-700' },
};

function AdminMenuManagement({ locations }: { locations: CanteenLocation[] }) {
  const [selectedLocation, setSelectedLocation] = useState<string>(locations[0]?.id ?? '');
  const [showAddItem, setShowAddItem] = useState(false);
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [editItem, setEditItem] = useState<MenuItem | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const [confirmCatDelete, setConfirmCatDelete] = useState<string | null>(null);

  const { data: categories = [] } = useMenuCategories(selectedLocation);
  const { data: items = [] } = useAllMenuItems(selectedLocation);
  const createItem = useCreateMenuItem();
  const updateItem = useUpdateMenuItem();
  const deleteItem = useDeleteMenuItem();
  const createCategory = useCreateMenuCategory();
  const deleteCategory = useDeleteMenuCategory();

  // ── Add/Edit item form state ──────────────────
  type ItemFormState = {
    name: string; description: string; item_type: 'VEG' | 'NON_VEG' | 'EGG' | 'VEGAN';
    price: string; employee_price: string; is_available: boolean; is_featured: boolean;
    calories: string; preparation_time_minutes: string; category: string; daily_quota: string;
  };
  const blankForm: ItemFormState = {
    name: '', description: '', item_type: 'VEG',
    price: '', employee_price: '', is_available: true,
    is_featured: false, calories: '', preparation_time_minutes: '5',
    category: categories[0]?.id ?? '', daily_quota: '',
  };
  const [form, setForm] = useState<ItemFormState>(blankForm);

  function openAdd() {
    setForm({ ...blankForm, category: categories[0]?.id ?? '' });
    setEditItem(null);
    setShowAddItem(true);
  }

  function openEdit(item: MenuItem) {
    setForm({
      name: item.name,
      description: item.description ?? '',
      item_type: item.item_type,
      price: String(item.price),
      employee_price: item.employee_price != null ? String(item.employee_price) : '',
      is_available: item.is_available,
      is_featured: item.is_featured,
      calories: item.calories != null ? String(item.calories) : '',
      preparation_time_minutes: String(item.preparation_time_minutes),
      category: item.category,
      daily_quota: item.daily_quota != null ? String(item.daily_quota) : '',
    });
    setEditItem(item);
    setShowAddItem(true);
  }

  function handleSave() {
    const payload = {
      canteen: selectedLocation,
      category: form.category,
      name: form.name,
      description: form.description,
      item_type: form.item_type,
      price: parseFloat(form.price) || 0,
      employee_price: form.employee_price ? parseFloat(form.employee_price) : null,
      is_available: form.is_available,
      is_featured: form.is_featured,
      calories: form.calories ? parseInt(form.calories) : null,
      preparation_time_minutes: parseInt(form.preparation_time_minutes) || 5,
      daily_quota: form.daily_quota ? parseInt(form.daily_quota) : null,
    };
    if (editItem) {
      updateItem.mutate({ id: editItem.id, ...payload }, { onSuccess: () => setShowAddItem(false) });
    } else {
      createItem.mutate(payload, { onSuccess: () => setShowAddItem(false) });
    }
  }

  // ── Add category form ─────────────────────────
  const [catName, setCatName] = useState('');

  function handleAddCategory() {
    if (!catName.trim()) return;
    createCategory.mutate(
      { canteen: selectedLocation, name: catName.trim() },
      { onSuccess: () => { setCatName(''); setShowAddCategory(false); } },
    );
  }

  const inputCls = 'w-full rounded-xl border border-surface-300/70 bg-surface-0 px-3 py-2 text-sm text-surface-900 placeholder-surface-400 focus:border-brand-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder-white/30';

  if (!locations.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <ChefHat className="h-10 w-10 text-surface-300 dark:text-white/20" />
        <p className="mt-3 text-sm text-surface-500 dark:text-white/40">No canteen locations configured yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      {/* Location switcher */}
      {locations.length > 1 && (
        <div className="flex flex-wrap gap-2">
          {locations.map((loc) => (
            <button key={loc.id} onClick={() => setSelectedLocation(loc.id)}
              className={cn('rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                selectedLocation === loc.id
                  ? 'bg-surface-900 text-white dark:bg-white dark:text-surface-900'
                  : 'bg-surface-100 text-surface-600 hover:bg-surface-200 dark:bg-white/5 dark:text-white/60')}>
              {loc.name}
            </button>
          ))}
        </div>
      )}

      {/* Categories section */}
      <div className="rounded-2xl border border-surface-200/70 bg-surface-0 p-4 shadow-xs dark:border-white/10 dark:bg-white/5">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-sm font-semibold text-surface-900 dark:text-white">
            <Tag className="h-4 w-4 text-brand-500" /> Categories
          </h3>
          <button onClick={() => setShowAddCategory(!showAddCategory)}
            className="flex items-center gap-1 rounded-lg bg-brand-50 px-2.5 py-1.5 text-xs font-medium text-brand-700 hover:bg-brand-100 dark:bg-brand-900/20 dark:text-brand-400">
            <Plus className="h-3.5 w-3.5" /> Add Category
          </button>
        </div>

        {showAddCategory && (
          <div className="mb-3 flex gap-2">
            <input type="text" placeholder="Category name" value={catName} onChange={(e) => setCatName(e.target.value)}
              className={cn(inputCls, 'flex-1')} />
            <button onClick={handleAddCategory} disabled={createCategory.isPending}
              className="rounded-xl bg-brand-600 px-3 py-2 text-xs font-medium text-white hover:bg-brand-700 disabled:opacity-50">
              {createCategory.isPending ? '…' : 'Save'}
            </button>
            <button onClick={() => setShowAddCategory(false)}
              className="rounded-xl border border-surface-200 px-3 py-2 text-xs text-surface-600 dark:border-white/10 dark:text-white/50">
              Cancel
            </button>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <div key={cat.id} className="flex items-center gap-1.5 rounded-lg border border-surface-200 bg-surface-50 px-2.5 py-1 dark:border-white/10 dark:bg-white/5">
              <span className="text-xs font-medium text-surface-700 dark:text-white/70">{cat.name}</span>
              {confirmCatDelete === cat.id ? (
                <>
                  <button onClick={() => { deleteCategory.mutate(cat.id); setConfirmCatDelete(null); }}
                    className="rounded px-1.5 py-0.5 text-xs text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20">Delete</button>
                  <button onClick={() => setConfirmCatDelete(null)}
                    className="rounded px-1.5 py-0.5 text-xs text-surface-400">Cancel</button>
                </>
              ) : (
                <button onClick={() => setConfirmCatDelete(cat.id)}
                  className="text-surface-300 hover:text-red-500 dark:text-white/20 dark:hover:text-red-400">
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
          ))}
          {categories.length === 0 && <p className="text-xs text-surface-400 dark:text-white/30">No categories yet</p>}
        </div>
      </div>

      {/* Menu items section */}
      <div className="rounded-2xl border border-surface-200/70 bg-surface-0 p-4 shadow-xs dark:border-white/10 dark:bg-white/5">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-sm font-semibold text-surface-900 dark:text-white">
            <ChefHat className="h-4 w-4 text-brand-500" /> Menu Items
            <span className="rounded-full bg-surface-100 px-2 py-0.5 text-xs text-surface-500 dark:bg-white/10 dark:text-white/40">{items.length}</span>
          </h3>
          <button onClick={openAdd}
            className="flex items-center gap-1 rounded-lg bg-brand-50 px-2.5 py-1.5 text-xs font-medium text-brand-700 hover:bg-brand-100 dark:bg-brand-900/20 dark:text-brand-400">
            <Plus className="h-3.5 w-3.5" /> Add Item
          </button>
        </div>

        {/* Add/Edit form */}
        <AnimatePresence>
          {showAddItem && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 overflow-hidden rounded-2xl border border-brand-200 bg-brand-50/30 p-4 dark:border-brand-800/40 dark:bg-brand-900/10"
            >
              <h4 className="mb-3 text-sm font-semibold text-surface-900 dark:text-white">
                {editItem ? 'Edit Item' : 'Add New Item'}
              </h4>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <input type="text" placeholder="Item name *" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} className={inputCls} />
                <select value={form.category} onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))} className={inputCls}>
                  {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
                <select value={form.item_type} onChange={(e) => setForm((f) => ({ ...f, item_type: e.target.value as 'VEG' | 'NON_VEG' | 'EGG' | 'VEGAN' }))} className={inputCls}>
                  <option value="VEG">Veg</option>
                  <option value="NON_VEG">Non-Veg</option>
                  <option value="EGG">Egg</option>
                  <option value="VEGAN">Vegan</option>
                </select>
                <input type="number" placeholder="Price (₹) *" value={form.price} onChange={(e) => setForm((f) => ({ ...f, price: e.target.value }))} className={inputCls} min="0" step="0.5" />
                <input type="number" placeholder="Employee price (₹, optional)" value={form.employee_price} onChange={(e) => setForm((f) => ({ ...f, employee_price: e.target.value }))} className={inputCls} min="0" step="0.5" />
                <input type="number" placeholder="Calories (optional)" value={form.calories} onChange={(e) => setForm((f) => ({ ...f, calories: e.target.value }))} className={inputCls} min="0" />
                <input type="number" placeholder="Prep time (min)" value={form.preparation_time_minutes} onChange={(e) => setForm((f) => ({ ...f, preparation_time_minutes: e.target.value }))} className={inputCls} min="1" />
                <input type="number" placeholder="Daily quota (optional)" value={form.daily_quota} onChange={(e) => setForm((f) => ({ ...f, daily_quota: e.target.value }))} className={inputCls} min="0" />
                <input type="text" placeholder="Description (optional)" value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} className={cn(inputCls, 'sm:col-span-2')} />
                <div className="flex items-center gap-4 sm:col-span-2">
                  <label className="flex cursor-pointer items-center gap-2 text-sm text-surface-700 dark:text-white/60">
                    <input type="checkbox" checked={form.is_available} onChange={(e) => setForm((f) => ({ ...f, is_available: e.target.checked }))} className="h-4 w-4 rounded" />
                    Available
                  </label>
                  <label className="flex cursor-pointer items-center gap-2 text-sm text-surface-700 dark:text-white/60">
                    <input type="checkbox" checked={form.is_featured} onChange={(e) => setForm((f) => ({ ...f, is_featured: e.target.checked }))} className="h-4 w-4 rounded" />
                    Featured
                  </label>
                </div>
              </div>
              <div className="mt-3 flex justify-end gap-2">
                <button onClick={() => setShowAddItem(false)}
                  className="rounded-xl border border-surface-200 px-4 py-2 text-sm text-surface-600 dark:border-white/10 dark:text-white/50">
                  Cancel
                </button>
                <button onClick={handleSave} disabled={!form.name || !form.price || createItem.isPending || updateItem.isPending}
                  className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
                  {(createItem.isPending || updateItem.isPending) ? 'Saving…' : (editItem ? 'Update' : 'Add Item')}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Items list */}
        {items.length === 0 ? (
          <p className="py-8 text-center text-sm text-surface-400 dark:text-white/30">No menu items yet. Add one above.</p>
        ) : (
          <div className="divide-y divide-surface-100 dark:divide-white/5">
            {items.map((item) => {
              const typeInfo = ITEM_TYPE_LABELS[item.item_type] ?? { label: item.item_type, color: 'bg-gray-100 text-gray-600' };
              return (
                <div key={item.id} className="flex items-center gap-3 py-3 first:pt-0 last:pb-0">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="font-medium text-surface-900 dark:text-white">{item.name}</p>
                      <span className={cn('rounded-full px-2 py-0.5 text-xs font-medium', typeInfo.color)}>{typeInfo.label}</span>
                      {!item.is_available && <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500 dark:bg-white/10 dark:text-white/40">Unavailable</span>}
                      {item.is_featured && <Star className="h-3.5 w-3.5 text-amber-400" />}
                    </div>
                    <p className="mt-0.5 text-xs text-surface-500 dark:text-white/40">
                      ₹{Number(item.price).toFixed(2)}
                      {item.employee_price != null && ` · Employee ₹${Number(item.employee_price).toFixed(2)}`}
                      {item.calories != null && ` · ${item.calories} kcal`}
                      {` · ~${item.preparation_time_minutes}min`}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-1">
                    <button onClick={() => openEdit(item)}
                      className="flex h-8 w-8 items-center justify-center rounded-lg text-surface-400 hover:bg-surface-100 hover:text-surface-700 dark:hover:bg-white/10 dark:hover:text-white/80">
                      <Edit2 className="h-3.5 w-3.5" />
                    </button>
                    {confirmDelete === item.id ? (
                      <div className="flex items-center gap-1">
                        <button onClick={() => { deleteItem.mutate(item.id); setConfirmDelete(null); }}
                          className="rounded-lg bg-red-600 px-2 py-1 text-xs font-medium text-white hover:bg-red-700">Delete</button>
                        <button onClick={() => setConfirmDelete(null)}
                          className="rounded-lg border border-surface-200 px-2 py-1 text-xs text-surface-600 dark:border-white/10 dark:text-white/50">Cancel</button>
                      </div>
                    ) : (
                      <button onClick={() => setConfirmDelete(item.id)}
                        className="flex h-8 w-8 items-center justify-center rounded-lg text-surface-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20 dark:hover:text-red-400">
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main CanteenPanel ───────────────────────────

export function CanteenPanel() {
  const activeModule = useUIStore((s) => s.activeModule);
  const portal = useUIStore((s) => s.portal);
  const rawModuleView = useUIStore((s) => s.moduleViews[activeModule] ?? 'employee');
  const moduleView = portal === 'ess' ? 'employee' : rawModuleView;
  const isAdmin = moduleView === 'admin';

  const { data: locations = [] } = useCanteenLocations();

  const employeeTabs = [
    {
      label: 'Order',
      value: 'order',
      content: <OrderMenu locations={locations} />,
    },
    {
      label: 'My Orders',
      value: 'my-orders',
      content: <MyOrdersList />,
    },
    {
      label: 'Wallet',
      value: 'wallet',
      content: <WalletView />,
    },
  ];

  const adminTabs = [
    {
      label: 'Kitchen View',
      value: 'kitchen',
      content: <KitchenView locations={locations} />,
    },
    {
      label: 'All Orders',
      value: 'all-orders',
      content: <MyOrdersList />, // reuses same list but with all=true
    },
    {
      label: 'Manage Menu',
      value: 'manage-menu',
      content: <AdminMenuManagement locations={locations} />,
    },
  ];

  return <Tabs items={isAdmin ? adminTabs : employeeTabs} />;
}
