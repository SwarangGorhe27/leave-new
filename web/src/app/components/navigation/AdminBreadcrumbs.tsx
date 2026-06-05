export function AdminBreadcrumbs({
  items,
}: {
  items: string[];
}) {
  return (
    <div className="flex items-center gap-1.5 text-[11px] text-neutral-400">
      {items.map((item, idx) => (
        <div key={`${item}-${idx}`} className="inline-flex items-center gap-1.5">
          {idx > 0 && <span className="text-neutral-600">/</span>}
          <span className={idx === items.length - 1 ? "text-neutral-200" : ""}>{item}</span>
        </div>
      ))}
    </div>
  );
}

