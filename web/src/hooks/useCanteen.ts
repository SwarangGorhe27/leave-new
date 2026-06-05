import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@api/client';

// ─── Types ───────────────────────────────────────

export interface CanteenLocation {
  id: string;
  name: string;
  building: string;
  floor: string;
  is_active: boolean;
  operating_hours_start: string;
  operating_hours_end: string;
  pre_order_cutoff_minutes: number;
  max_orders_per_slot: number;
}

export interface MenuCategory {
  id: string;
  name: string;
  display_order: number;
  icon: string;
  is_active: boolean;
  canteen: string;
}

export interface MenuItem {
  id: string;
  category: string;
  category_name: string;
  canteen: string;
  name: string;
  description: string;
  item_type: 'VEG' | 'NON_VEG' | 'EGG' | 'VEGAN';
  price: number;
  employee_price: number | null;
  effective_price: number;
  company_subsidy_per_item: number;
  is_available: boolean;
  image: string | null;
  calories: number | null;
  preparation_time_minutes: number;
  is_featured: boolean;
  daily_quota: number | null;
}

export interface CanteenBreakSlot {
  id: string;
  canteen: string;
  name: string;
  slot_start: string;
  slot_end: string;
  max_orders: number | null;
  is_active: boolean;
}

export interface CanteenOrderItem {
  id: string;
  menu_item: string;
  item_name: string;
  item_type: string;
  quantity: number;
  unit_price: number;
  unit_subsidy: number;
  special_instructions: string;
  line_total: number;
}

export interface CanteenOrder {
  id: string;
  order_number: string;
  employee: string;
  employee_name: string;
  employee_code: string;
  canteen: string;
  canteen_name: string;
  break_slot: string | null;
  break_slot_name: string | null;
  order_date: string;
  status: 'DRAFT' | 'PLACED' | 'CONFIRMED' | 'PREPARING' | 'READY' | 'COLLECTED' | 'CANCELLED' | 'REFUNDED';
  payment_mode: string;
  subtotal: number;
  discount_amount: number;
  company_subsidy: number;
  employee_payable: number;
  placed_at: string | null;
  pickup_token: string;
  special_instructions: string;
  items: CanteenOrderItem[];
  created_at: string;
}

export interface CanteenWallet {
  id: string;
  employee: string;
  balance: number;
  last_recharged_at: string | null;
  is_active: boolean;
}

export interface WalletTransaction {
  id: string;
  transaction_type: string;
  amount: number;
  balance_before: number;
  balance_after: number;
  reference: string;
  notes: string;
  created_at: string;
}

export interface PlaceOrderPayload {
  canteen: string;
  break_slot?: string | null;
  payment_mode?: string;
  special_instructions?: string;
  items: { menu_item: string; quantity: number; special_instructions?: string }[];
}

// ─── Extract helpers ─────────────────────────────

function extract<T>(res: unknown): T[] {
  const d = res as Record<string, unknown>;
  return (d?.data as Record<string, unknown>)?.results as T[]
    ?? (d?.data as Record<string, unknown>)?.data as T[]
    ?? d?.data as T[]
    ?? d?.results as T[]
    ?? (Array.isArray(d) ? d : []) as T[];
}

function extractOne<T>(res: unknown): T {
  const d = res as Record<string, unknown>;
  return ((d?.data as Record<string, unknown>)?.data ?? d?.data ?? d) as T;
}

// ─── Demo seed data ──────────────────────────────

const DEMO_LOCATIONS: CanteenLocation[] = [
  {
    id: 'cant-1',
    name: 'Main Cafeteria',
    building: 'Block A',
    floor: 'Ground Floor',
    is_active: true,
    operating_hours_start: '07:30',
    operating_hours_end: '20:00',
    pre_order_cutoff_minutes: 30,
    max_orders_per_slot: 80,
  },
  {
    id: 'cant-2',
    name: 'IT Block Pantry',
    building: 'Block B',
    floor: '2nd Floor',
    is_active: true,
    operating_hours_start: '08:00',
    operating_hours_end: '18:00',
    pre_order_cutoff_minutes: 20,
    max_orders_per_slot: 30,
  },
];

const DEMO_CATEGORIES: MenuCategory[] = [
  { id: 'cat-1', name: 'Breakfast', display_order: 1, icon: '🌅', is_active: true, canteen: 'cant-1' },
  { id: 'cat-2', name: 'Main Course', display_order: 2, icon: '🍱', is_active: true, canteen: 'cant-1' },
  { id: 'cat-3', name: 'Snacks', display_order: 3, icon: '🍿', is_active: true, canteen: 'cant-1' },
  { id: 'cat-4', name: 'Beverages', display_order: 4, icon: '☕', is_active: true, canteen: 'cant-1' },
  { id: 'cat-5', name: 'Desserts', display_order: 5, icon: '🍰', is_active: true, canteen: 'cant-1' },
];

const DEMO_ITEMS: MenuItem[] = [
  // Breakfast
  { id: 'mi-1', category: 'cat-1', category_name: 'Breakfast', canteen: 'cant-1', name: 'Masala Dosa', description: 'Crispy rice crepe with spiced potato filling, served with chutney and sambar', item_type: 'VEG', price: 60, employee_price: 40, effective_price: 40, company_subsidy_per_item: 20, is_available: true, image: null, calories: 320, preparation_time_minutes: 8, is_featured: true, daily_quota: null },
  { id: 'mi-2', category: 'cat-1', category_name: 'Breakfast', canteen: 'cant-1', name: 'Poha', description: 'Flattened rice with mustard seeds, onion, turmeric & coriander', item_type: 'VEG', price: 35, employee_price: 25, effective_price: 25, company_subsidy_per_item: 10, is_available: true, image: null, calories: 250, preparation_time_minutes: 5, is_featured: false, daily_quota: null },
  { id: 'mi-3', category: 'cat-1', category_name: 'Breakfast', canteen: 'cant-1', name: 'Bread Omelette', description: 'Fresh toast with 2-egg omelette, vegetables, and ketchup', item_type: 'EGG', price: 55, employee_price: 40, effective_price: 40, company_subsidy_per_item: 15, is_available: true, image: null, calories: 400, preparation_time_minutes: 6, is_featured: false, daily_quota: null },
  { id: 'mi-4', category: 'cat-1', category_name: 'Breakfast', canteen: 'cant-1', name: 'Upma', description: 'Semolina porridge tempered with mustard seeds, curry leaves, and vegetables', item_type: 'VEG', price: 30, employee_price: 20, effective_price: 20, company_subsidy_per_item: 10, is_available: true, image: null, calories: 280, preparation_time_minutes: 5, is_featured: false, daily_quota: null },
  // Main Course
  { id: 'mi-5', category: 'cat-2', category_name: 'Main Course', canteen: 'cant-1', name: 'Dal Rice', description: 'Yellow lentil dal with steamed basmati rice and papad', item_type: 'VEG', price: 80, employee_price: 55, effective_price: 55, company_subsidy_per_item: 25, is_available: true, image: null, calories: 520, preparation_time_minutes: 10, is_featured: true, daily_quota: null },
  { id: 'mi-6', category: 'cat-2', category_name: 'Main Course', canteen: 'cant-1', name: 'Veg Thali', description: 'Complete meal: 2 sabzi, dal, rice, roti, salad, and pickle', item_type: 'VEG', price: 120, employee_price: 85, effective_price: 85, company_subsidy_per_item: 35, is_available: true, image: null, calories: 750, preparation_time_minutes: 12, is_featured: true, daily_quota: 60 },
  { id: 'mi-7', category: 'cat-2', category_name: 'Main Course', canteen: 'cant-1', name: 'Chicken Biryani', description: 'Aromatic basmati biryani with tender chicken, dum-cooked, served with raita', item_type: 'NON_VEG', price: 150, employee_price: 110, effective_price: 110, company_subsidy_per_item: 40, is_available: true, image: null, calories: 680, preparation_time_minutes: 15, is_featured: true, daily_quota: 40 },
  { id: 'mi-8', category: 'cat-2', category_name: 'Main Course', canteen: 'cant-1', name: 'Paneer Butter Masala + Roti', description: 'Rich tomato-cream gravy with paneer, served with 3 rotis', item_type: 'VEG', price: 110, employee_price: 80, effective_price: 80, company_subsidy_per_item: 30, is_available: true, image: null, calories: 620, preparation_time_minutes: 12, is_featured: false, daily_quota: null },
  // Snacks
  { id: 'mi-9', category: 'cat-3', category_name: 'Snacks', canteen: 'cant-1', name: 'Samosa (2 pcs)', description: 'Crispy pastry filled with spiced potatoes and peas', item_type: 'VEG', price: 25, employee_price: 18, effective_price: 18, company_subsidy_per_item: 7, is_available: true, image: null, calories: 200, preparation_time_minutes: 3, is_featured: false, daily_quota: null },
  { id: 'mi-10', category: 'cat-3', category_name: 'Snacks', canteen: 'cant-1', name: 'Veg Puff', description: 'Puff pastry with spiced vegetable filling, freshly baked', item_type: 'VEG', price: 20, employee_price: 15, effective_price: 15, company_subsidy_per_item: 5, is_available: true, image: null, calories: 180, preparation_time_minutes: 3, is_featured: false, daily_quota: null },
  // Beverages
  { id: 'mi-11', category: 'cat-4', category_name: 'Beverages', canteen: 'cant-1', name: 'Masala Chai', description: 'Indian spiced milk tea — the classic office favourite', item_type: 'VEG', price: 15, employee_price: 10, effective_price: 10, company_subsidy_per_item: 5, is_available: true, image: null, calories: 80, preparation_time_minutes: 3, is_featured: false, daily_quota: null },
  { id: 'mi-12', category: 'cat-4', category_name: 'Beverages', canteen: 'cant-1', name: 'Cold Coffee', description: 'Chilled coffee blended with milk and ice cream', item_type: 'VEG', price: 45, employee_price: 30, effective_price: 30, company_subsidy_per_item: 15, is_available: true, image: null, calories: 160, preparation_time_minutes: 5, is_featured: true, daily_quota: null },
  // Desserts
  { id: 'mi-13', category: 'cat-5', category_name: 'Desserts', canteen: 'cant-1', name: 'Gulab Jamun (2 pcs)', description: 'Soft milk-solid dumplings soaked in rose-flavoured sugar syrup', item_type: 'VEG', price: 30, employee_price: 20, effective_price: 20, company_subsidy_per_item: 10, is_available: true, image: null, calories: 280, preparation_time_minutes: 2, is_featured: false, daily_quota: null },
];

const DEMO_BREAK_SLOTS: CanteenBreakSlot[] = [
  { id: 'slot-1', canteen: 'cant-1', name: 'Morning Break', slot_start: '10:30', slot_end: '10:50', max_orders: 50, is_active: true },
  { id: 'slot-2', canteen: 'cant-1', name: 'Lunch Slot A', slot_start: '12:30', slot_end: '13:30', max_orders: 80, is_active: true },
  { id: 'slot-3', canteen: 'cant-1', name: 'Lunch Slot B', slot_start: '13:30', slot_end: '14:30', max_orders: 80, is_active: true },
  { id: 'slot-4', canteen: 'cant-1', name: 'Evening Snacks', slot_start: '16:30', slot_end: '17:00', max_orders: 40, is_active: true },
];

const DEMO_ORDERS: CanteenOrder[] = [
  {
    id: 'ord-1',
    order_number: 'ORD-2026-0421',
    employee: 'emp-1',
    employee_name: 'Aditi Mehra',
    employee_code: 'EMP-0001',
    canteen: 'cant-1',
    canteen_name: 'Main Cafeteria',
    break_slot: 'slot-2',
    break_slot_name: 'Lunch Slot A',
    order_date: '2026-04-28',
    status: 'COLLECTED',
    payment_mode: 'WALLET',
    subtotal: 195,
    discount_amount: 0,
    company_subsidy: 60,
    employee_payable: 135,
    placed_at: '2026-04-28T12:05:00Z',
    pickup_token: 'A14',
    special_instructions: '',
    items: [
      { id: 'oi-1', menu_item: 'mi-6', item_name: 'Veg Thali', item_type: 'VEG', quantity: 1, unit_price: 85, unit_subsidy: 35, special_instructions: '', line_total: 85 },
      { id: 'oi-2', menu_item: 'mi-12', item_name: 'Cold Coffee', item_type: 'VEG', quantity: 1, unit_price: 30, unit_subsidy: 15, special_instructions: '', line_total: 30 },
      { id: 'oi-3', menu_item: 'mi-11', item_name: 'Masala Chai', item_type: 'VEG', quantity: 2, unit_price: 10, unit_subsidy: 5, special_instructions: '', line_total: 20 },
    ],
    created_at: '2026-04-28T12:04:00Z',
  },
  {
    id: 'ord-2',
    order_number: 'ORD-2026-0418',
    employee: 'emp-1',
    employee_name: 'Aditi Mehra',
    employee_code: 'EMP-0001',
    canteen: 'cant-1',
    canteen_name: 'Main Cafeteria',
    break_slot: 'slot-1',
    break_slot_name: 'Morning Break',
    order_date: '2026-04-27',
    status: 'COLLECTED',
    payment_mode: 'WALLET',
    subtotal: 50,
    discount_amount: 0,
    company_subsidy: 15,
    employee_payable: 35,
    placed_at: '2026-04-27T10:20:00Z',
    pickup_token: 'B07',
    special_instructions: '',
    items: [
      { id: 'oi-4', menu_item: 'mi-1', item_name: 'Masala Dosa', item_type: 'VEG', quantity: 1, unit_price: 40, unit_subsidy: 20, special_instructions: '', line_total: 40 },
      { id: 'oi-5', menu_item: 'mi-11', item_name: 'Masala Chai', item_type: 'VEG', quantity: 1, unit_price: 10, unit_subsidy: 5, special_instructions: '', line_total: 10 },
    ],
    created_at: '2026-04-27T10:19:00Z',
  },
];

const DEMO_WALLET: CanteenWallet = {
  id: 'wallet-1',
  employee: 'emp-1',
  balance: 850,
  last_recharged_at: '2026-04-20T09:00:00Z',
  is_active: true,
};

const DEMO_WALLET_TXN: WalletTransaction[] = [
  { id: 'txn-1', transaction_type: 'RECHARGE', amount: 1000, balance_before: 0, balance_after: 1000, reference: 'RECH-APR-2026', notes: 'Monthly recharge via salary deduction', created_at: '2026-04-01T09:00:00Z' },
  { id: 'txn-2', transaction_type: 'DEBIT', amount: 135, balance_before: 1000, balance_after: 865, reference: 'ORD-2026-0418', notes: 'Masala Dosa + Chai', created_at: '2026-04-27T10:20:00Z' },
  { id: 'txn-3', transaction_type: 'DEBIT', amount: 135, balance_before: 865, balance_after: 730, reference: 'ORD-2026-0421', notes: 'Veg Thali + Cold Coffee + Chai x2', created_at: '2026-04-28T12:05:00Z' },
  { id: 'txn-4', transaction_type: 'SUBSIDY_CREDIT', amount: 120, balance_before: 730, balance_after: 850, reference: 'SUBSIDY-APR-W4', notes: 'Company subsidy credit', created_at: '2026-04-28T23:59:00Z' },
];

const CANTEEN_ORDERS_KEY = 'hrms-demo-canteen-orders';

function readDemoOrders(): CanteenOrder[] {
  const raw = localStorage.getItem(CANTEEN_ORDERS_KEY);
  if (raw) { try { return JSON.parse(raw) as CanteenOrder[]; } catch { /* fallback */ } }
  localStorage.setItem(CANTEEN_ORDERS_KEY, JSON.stringify(DEMO_ORDERS));
  return DEMO_ORDERS;
}

function writeDemoOrders(orders: CanteenOrder[]) {
  localStorage.setItem(CANTEEN_ORDERS_KEY, JSON.stringify(orders));
}

// ─── Hooks ───────────────────────────────────────

export function useCanteenLocations() {
  return useQuery({
    queryKey: ['canteen', 'locations'],
    queryFn: async () => {
      try {
        const res = await api.get('/canteen/locations/');
        const rows = extract<CanteenLocation>(res);
        if (rows.length) return rows;
      } catch { /* fallback */ }
      return DEMO_LOCATIONS;
    },
  });
}

export function useMenuCategories(canteenId?: string) {
  return useQuery({
    queryKey: ['canteen', 'categories', canteenId],
    queryFn: async () => {
      try {
        const params = canteenId ? { canteen: canteenId } : {};
        const res = await api.get('/canteen/categories/', { params });
        const rows = extract<MenuCategory>(res);
        if (rows.length) return rows;
      } catch { /* fallback */ }
      return DEMO_CATEGORIES.filter((c) => !canteenId || c.canteen === canteenId);
    },
    enabled: !!canteenId,
  });
}

export function useMenuItems(canteenId?: string, categoryId?: string) {
  return useQuery({
    queryKey: ['canteen', 'items', canteenId, categoryId],
    queryFn: async () => {
      try {
        const params: Record<string, string> = {};
        if (canteenId) params.canteen = canteenId;
        if (categoryId) params.category = categoryId;
        const res = await api.get('/canteen/items/', { params });
        const rows = extract<MenuItem>(res);
        if (rows.length) return rows;
      } catch { /* fallback */ }
      return DEMO_ITEMS.filter(
        (i) => (!canteenId || i.canteen === canteenId) && (!categoryId || i.category === categoryId)
      );
    },
    enabled: !!canteenId,
  });
}

export function useBreakSlots(canteenId?: string) {
  return useQuery({
    queryKey: ['canteen', 'break-slots', canteenId],
    queryFn: async () => {
      try {
        const params = canteenId ? { canteen: canteenId } : {};
        const res = await api.get('/canteen/break-slots/', { params });
        const rows = extract<CanteenBreakSlot>(res);
        if (rows.length) return rows;
      } catch { /* fallback */ }
      return DEMO_BREAK_SLOTS.filter((s) => !canteenId || s.canteen === canteenId);
    },
    enabled: !!canteenId,
  });
}

export function useMyOrders() {
  return useQuery({
    queryKey: ['canteen', 'my-orders'],
    queryFn: async () => {
      try {
        const res = await api.get('/canteen/orders/');
        const rows = extract<CanteenOrder>(res);
        if (rows.length) return rows;
      } catch { /* fallback */ }
      return readDemoOrders();
    },
  });
}

export function useAllOrders() {
  return useQuery({
    queryKey: ['canteen', 'all-orders'],
    queryFn: async () => {
      try {
        const res = await api.get('/canteen/orders/', { params: { all: 'true' } });
        const rows = extract<CanteenOrder>(res);
        if (rows.length) return rows;
      } catch { /* fallback */ }
      return readDemoOrders();
    },
  });
}

export function usePlaceOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: PlaceOrderPayload) => {
      try {
        const res = await api.post('/canteen/orders/place/', payload);
        return extractOne<CanteenOrder>(res);
      } catch {
        const subtotal = payload.items.reduce((sum, p) => {
          const item = DEMO_ITEMS.find((i) => i.id === p.menu_item);
          return sum + (item ? item.effective_price * p.quantity : 0);
        }, 0);
        const subsidy = payload.items.reduce((sum, p) => {
          const item = DEMO_ITEMS.find((i) => i.id === p.menu_item);
          return sum + (item ? item.company_subsidy_per_item * p.quantity : 0);
        }, 0);
        const order: CanteenOrder = {
          id: crypto.randomUUID(),
          order_number: `ORD-2026-${String(Math.floor(Math.random() * 9000) + 1000)}`,
          employee: 'emp-1',
          employee_name: 'Aditi Mehra',
          employee_code: 'EMP-0001',
          canteen: payload.canteen,
          canteen_name: DEMO_LOCATIONS.find((l) => l.id === payload.canteen)?.name ?? 'Main Cafeteria',
          break_slot: payload.break_slot ?? null,
          break_slot_name: DEMO_BREAK_SLOTS.find((s) => s.id === payload.break_slot)?.name ?? null,
          order_date: new Date().toISOString().slice(0, 10),
          status: 'CONFIRMED',
          payment_mode: payload.payment_mode ?? 'WALLET',
          subtotal,
          discount_amount: 0,
          company_subsidy: subsidy,
          employee_payable: subtotal,
          placed_at: new Date().toISOString(),
          pickup_token: `T${Math.floor(Math.random() * 90) + 10}`,
          special_instructions: payload.special_instructions ?? '',
          items: payload.items.map((p) => {
            const mi = DEMO_ITEMS.find((i) => i.id === p.menu_item)!;
            return {
              id: crypto.randomUUID(),
              menu_item: p.menu_item,
              item_name: mi?.name ?? 'Item',
              item_type: mi?.item_type ?? 'VEG',
              quantity: p.quantity,
              unit_price: mi?.effective_price ?? 0,
              unit_subsidy: mi?.company_subsidy_per_item ?? 0,
              special_instructions: p.special_instructions ?? '',
              line_total: (mi?.effective_price ?? 0) * p.quantity,
            };
          }),
          created_at: new Date().toISOString(),
        };
        writeDemoOrders([order, ...readDemoOrders()]);
        return order;
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['canteen', 'my-orders'] });
      qc.invalidateQueries({ queryKey: ['canteen', 'wallet'] });
    },
  });
}

export function useCancelOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ orderId, reason }: { orderId: string; reason?: string }) => {
      try {
        const res = await api.post(`/canteen/orders/${orderId}/cancel/`, { reason });
        return extractOne<CanteenOrder>(res);
      } catch {
        const orders = readDemoOrders().map((o) => o.id === orderId ? { ...o, status: 'CANCELLED' as const } : o);
        writeDemoOrders(orders);
        return orders.find((o) => o.id === orderId);
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['canteen'] });
    },
  });
}

export function useUpdateOrderStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ orderId, status }: { orderId: string; status: string }) => {
      const res = await api.post(`/canteen/orders/${orderId}/update_status/`, { status });
      return extractOne<CanteenOrder>(res);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['canteen'] });
    },
  });
}

export function useMyWallet() {
  return useQuery({
    queryKey: ['canteen', 'wallet', 'me'],
    queryFn: async () => {
      try {
        const res = await api.get('/canteen/wallet/me/');
        const w = extractOne<CanteenWallet>(res);
        if ((w as CanteenWallet)?.id) return w;
      } catch { /* fallback */ }
      return DEMO_WALLET;
    },
  });
}

export function useWalletTransactions() {
  return useQuery({
    queryKey: ['canteen', 'wallet', 'transactions'],
    queryFn: async () => {
      try {
        const res = await api.get('/canteen/wallet/transactions/');
        const rows = extract<WalletTransaction>(res);
        if (rows.length) return rows;
      } catch { /* fallback */ }
      return DEMO_WALLET_TXN;
    },
  });
}

export function useRechargeWallet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      amount,
      method,
      upi_ref,
    }: {
      amount: number;
      method: 'UPI' | 'SALARY';
      upi_ref?: string;
    }) => {
      const res = await api.post('/canteen/wallet/recharge/', { amount, method, upi_ref });
      return extractOne<CanteenWallet>(res);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['canteen', 'wallet'] });
    },
  });
}

export function useKitchenDashboard(canteenId?: string) {
  return useQuery({
    queryKey: ['canteen', 'kitchen', canteenId],
    queryFn: async () => {
      const params = canteenId ? { canteen: canteenId } : {};
      const res = await api.get('/canteen/kitchen/', { params });
      return extractOne<Record<string, { label: string; count: number; orders: CanteenOrder[] }>>(res);
    },
    refetchInterval: 15000, // auto-refresh every 15s for kitchen view
  });
}

// ─── Admin: Menu Management ────────────────────

export interface MenuItemPayload {
  canteen: string;
  category: string;
  name: string;
  description?: string;
  item_type: 'VEG' | 'NON_VEG' | 'EGG' | 'VEGAN';
  price: number;
  employee_price?: number | null;
  company_subsidy_per_item?: number;
  is_available?: boolean;
  calories?: number | null;
  preparation_time_minutes?: number;
  is_featured?: boolean;
  daily_quota?: number | null;
}

export interface MenuCategoryPayload {
  canteen: string;
  name: string;
  display_order?: number;
  icon?: string;
  is_active?: boolean;
}

export function useAllMenuItems(canteenId?: string) {
  return useQuery({
    queryKey: ['canteen', 'admin-items', canteenId],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (canteenId) params.canteen = canteenId;
      const res = await api.get('/canteen/items/', { params });
      return extract<MenuItem>(res);
    },
  });
}

export function useCreateMenuItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: MenuItemPayload) => {
      const res = await api.post('/canteen/items/', payload);
      return extractOne<MenuItem>(res);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['canteen', 'items'] });
      qc.invalidateQueries({ queryKey: ['canteen', 'admin-items'] });
    },
  });
}

export function useUpdateMenuItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: Partial<MenuItemPayload> & { id: string }) => {
      const res = await api.patch(`/canteen/items/${id}/`, payload);
      return extractOne<MenuItem>(res);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['canteen', 'items'] });
      qc.invalidateQueries({ queryKey: ['canteen', 'admin-items'] });
    },
  });
}

export function useDeleteMenuItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/canteen/items/${id}/`);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['canteen', 'items'] });
      qc.invalidateQueries({ queryKey: ['canteen', 'admin-items'] });
    },
  });
}

export function useCreateMenuCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: MenuCategoryPayload) => {
      const res = await api.post('/canteen/categories/', payload);
      return extractOne<MenuCategory>(res);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['canteen', 'categories'] });
    },
  });
}

export function useDeleteMenuCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/canteen/categories/${id}/`);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['canteen', 'categories'] });
    },
  });
}

