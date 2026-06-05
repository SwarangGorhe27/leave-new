export function SkeletonTable({
  rows = 8,
  cols = 10,
}: {
  rows?: number;
  cols?: number;
}) {
  return (
    <div className="flat-card bg-card overflow-hidden animate-pulse">
      <div className="px-6 py-4 border-b border-border flex items-center justify-between">
        <div className="h-4 w-40 bg-secondary rounded" />
        <div className="h-8 w-28 bg-secondary rounded-lg" />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-secondary border-b border-border">
              {Array.from({ length: cols }).map((_, i) => (
                <th key={i} className="px-6 py-3">
                  <div className="h-3 w-24 bg-background rounded" />
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {Array.from({ length: rows }).map((_, r) => (
              <tr key={r}>
                {Array.from({ length: cols }).map((__, c) => (
                  <td key={c} className="px-6 py-4">
                    <div className="h-3 w-28 bg-secondary rounded" />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

