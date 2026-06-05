import { useState } from "react";
import { Coffee, Plus, Minus, ShoppingCart, Clock } from "lucide-react";

/* ── Mock Menu Data ─────────────────────────────────────────── */
const MENU_ITEMS = [
  { id: "1",  name: "Masala Chai",         category: "Beverages", price: 15,  prep: "2 min",  desc: "Freshly brewed spiced tea"          },
  { id: "2",  name: "Filter Coffee",       category: "Beverages", price: 20,  prep: "3 min",  desc: "South Indian filter coffee"         },
  { id: "3",  name: "Veg Sandwich",        category: "Snacks",    price: 55,  prep: "8 min",  desc: "Grilled vegetable sandwich"         },
  { id: "4",  name: "Paneer Roll",         category: "Snacks",    price: 75,  prep: "10 min", desc: "Soft roll with spiced paneer"       },
  { id: "5",  name: "Dal Rice",            category: "Meals",     price: 80,  prep: "5 min",  desc: "Comfort dal with steamed rice"      },
  { id: "6",  name: "Rajma Chawal",        category: "Meals",     price: 90,  prep: "5 min",  desc: "Kidney beans curry with rice"       },
  { id: "7",  name: "Mango Lassi",         category: "Beverages", price: 40,  prep: "5 min",  desc: "Chilled mango yogurt drink"         },
  { id: "8",  name: "Veg Biryani",         category: "Meals",     price: 120, prep: "15 min", desc: "Aromatic basmati with vegetables"   },
  { id: "9",  name: "Samosa (2 pcs)",      category: "Snacks",    price: 30,  prep: "5 min",  desc: "Crispy potato-filled pastry"        },
  { id: "10", name: "Cold Brew Coffee",    category: "Beverages", price: 60,  prep: "1 min",  desc: "Smooth cold brew, ready to serve"   },
];

const CATEGORIES = ["All", "Beverages", "Snacks", "Meals"];

type CartItem = { id: string; name: string; price: number; qty: number };

export function EmployeeCanteenPage() {
  const [activeCategory, setActiveCategory] = useState("All");
  const [cart, setCart] = useState<CartItem[]>([]);
  const [ordered, setOrdered] = useState(false);

  const filtered = activeCategory === "All"
    ? MENU_ITEMS
    : MENU_ITEMS.filter((m) => m.category === activeCategory);

  const getQty = (id: string) => cart.find((c) => c.id === id)?.qty ?? 0;

  const addItem = (item: typeof MENU_ITEMS[0]) => {
    setCart((prev) => {
      const existing = prev.find((c) => c.id === item.id);
      if (existing) {
        return prev.map((c) => c.id === item.id ? { ...c, qty: c.qty + 1 } : c);
      }
      return [...prev, { id: item.id, name: item.name, price: item.price, qty: 1 }];
    });
  };

  const removeItem = (id: string) => {
    setCart((prev) => {
      const existing = prev.find((c) => c.id === id);
      if (!existing) return prev;
      if (existing.qty <= 1) return prev.filter((c) => c.id !== id);
      return prev.map((c) => c.id === id ? { ...c, qty: c.qty - 1 } : c);
    });
  };

  const totalItems = cart.reduce((s, c) => s + c.qty, 0);
  const totalPrice = cart.reduce((s, c) => s + c.price * c.qty, 0);

  const handleOrder = () => {
    setOrdered(true);
    setCart([]);
    setTimeout(() => setOrdered(false), 3000);
  };

  return (
    <div className="p-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* ── Menu ────────────────────────────────────────── */}
        <div className="lg:col-span-2 space-y-5">
          {/* Header */}
          <div className="flat-card bg-card p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-secondary border border-border flex items-center justify-center">
                <Coffee className="w-5 h-5 text-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">Canteen Menu</h1>
                <p className="text-xs text-muted-foreground mt-0.5">Today's menu — order by 12:30 PM</p>
              </div>
            </div>
          </div>

          {/* Category filter */}
          <div className="flex gap-2 flex-wrap">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-4 py-2 rounded-lg text-sm font-medium border transition-all duration-150 ${
                  activeCategory === cat
                    ? "bg-foreground text-primary-foreground border-transparent"
                    : "bg-card text-muted-foreground border-border hover:bg-secondary hover:text-foreground"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Menu items grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {filtered.map((item) => {
              const qty = getQty(item.id);
              return (
                <div
                  key={item.id}
                  className="flat-card bg-card p-4 flex flex-col gap-3 hover:shadow-md transition-shadow duration-150"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-foreground">{item.name}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">{item.desc}</p>
                    </div>
                    <span className="text-xs bg-secondary border border-border text-muted-foreground px-2 py-0.5 rounded-md flex-shrink-0">
                      {item.category}
                    </span>
                  </div>

                  <div className="flex items-center justify-between mt-auto">
                    <div className="flex items-center gap-3">
                      <span className="text-base font-bold text-foreground">₹{item.price}</span>
                      <span className="flex items-center gap-1 text-[11px] text-muted-foreground">
                        <Clock className="w-3 h-3" /> {item.prep}
                      </span>
                    </div>

                    {qty === 0 ? (
                      <button
                        onClick={() => addItem(item)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-foreground text-primary-foreground text-xs font-medium rounded-md hover:bg-accent transition-colors"
                      >
                        <Plus className="w-3.5 h-3.5" /> Add
                      </button>
                    ) : (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => removeItem(item.id)}
                          className="w-7 h-7 flex items-center justify-center bg-secondary border border-border rounded-md hover:bg-[#CED4DA] transition-colors"
                        >
                          <Minus className="w-3.5 h-3.5 text-foreground" />
                        </button>
                        <span className="text-sm font-bold text-foreground w-4 text-center">{qty}</span>
                        <button
                          onClick={() => addItem(item)}
                          className="w-7 h-7 flex items-center justify-center bg-foreground text-primary-foreground rounded-md hover:bg-accent transition-colors"
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ── Cart ────────────────────────────────────────── */}
        <div className="lg:col-span-1">
          <div className="flat-card bg-card overflow-hidden sticky top-6">
            <div className="px-5 py-4 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShoppingCart className="w-4 h-4 text-foreground" />
                <h2 className="text-sm font-semibold text-foreground">Your Order</h2>
              </div>
              {totalItems > 0 && (
                <span className="text-xs font-bold text-primary-foreground bg-foreground px-2 py-0.5 rounded-md">
                  {totalItems} item{totalItems !== 1 ? "s" : ""}
                </span>
              )}
            </div>

            {ordered && (
              <div className="px-5 py-4 bg-secondary border-b border-border">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-[#212529]" />
                  <p className="text-sm font-medium text-foreground">Order placed! Ready in ~15 min.</p>
                </div>
              </div>
            )}

            {cart.length === 0 && !ordered ? (
              <div className="px-5 py-12 flex flex-col items-center text-center">
                <Coffee className="w-10 h-10 text-muted-foreground opacity-30 mb-3" />
                <p className="text-sm font-medium text-muted-foreground">Your cart is empty</p>
                <p className="text-xs text-muted-foreground mt-1">Add items from the menu</p>
              </div>
            ) : (
              <>
                <div className="divide-y divide-border max-h-[340px] overflow-y-auto">
                  {cart.map((item) => (
                    <div key={item.id} className="px-5 py-3 flex items-center justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">{item.name}</p>
                        <p className="text-xs text-muted-foreground">₹{item.price} × {item.qty}</p>
                      </div>
                      <span className="text-sm font-bold text-foreground flex-shrink-0">
                        ₹{item.price * item.qty}
                      </span>
                    </div>
                  ))}
                </div>

                <div className="px-5 py-4 border-t border-border space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Subtotal</span>
                    <span className="font-medium text-foreground">₹{totalPrice}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">GST (5%)</span>
                    <span className="font-medium text-foreground">₹{Math.round(totalPrice * 0.05)}</span>
                  </div>
                  <div className="flex justify-between font-bold text-foreground border-t border-border pt-3">
                    <span>Total</span>
                    <span>₹{totalPrice + Math.round(totalPrice * 0.05)}</span>
                  </div>

                  <button
                    onClick={handleOrder}
                    className="w-full py-3 bg-foreground text-primary-foreground text-sm font-semibold rounded-lg
                      hover:bg-accent transition-colors"
                  >
                    Place Order
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
