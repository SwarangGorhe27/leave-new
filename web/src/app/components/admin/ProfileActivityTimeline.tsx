import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../../store";
import { fetchActivities } from "../../../store/slices/activitySlice";
import { Clock, CheckCircle2 } from "lucide-react";

export function ProfileActivityTimeline({ employeeId }: { employeeId: string }) {
  const dispatch = useDispatch<AppDispatch>();
  const activities = useSelector((state: RootState) => state.activities.activities);
  const status = useSelector((state: RootState) => state.activities.status);

  useEffect(() => {
    dispatch(fetchActivities(employeeId));
  }, [dispatch, employeeId]);

  if (status === "loading") {
    return <div className="text-sm text-muted-foreground">Loading timeline...</div>;
  }

  const employeeActivities = activities.filter((a) => a.employeeId === employeeId);

  if (employeeActivities.length === 0) {
    return (
      <div className="p-6 border border-border rounded-xl bg-card">
        <h3 className="text-base font-bold mb-2 flex items-center gap-2">
          <Clock className="w-4 h-4" />
          Recent Admin Activities
        </h3>
        <p className="text-sm text-muted-foreground">No recent activities found.</p>
      </div>
    );
  }

  return (
    <div className="p-6 border border-border rounded-xl bg-card">
      <h3 className="text-base font-bold mb-6 flex items-center gap-2">
        <Clock className="w-5 h-5 text-primary" />
        Recent Admin Activities
      </h3>
      <div className="space-y-6 relative before:absolute before:inset-0 before:ml-2.5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
        {employeeActivities.map((activity) => (
          <div
            key={activity.id}
            className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active"
          >
            <div className="flex items-center justify-center w-6 h-6 rounded-full border-2 border-background bg-primary text-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
              <CheckCircle2 className="w-3 h-3" />
            </div>

            <div className="w-[calc(100%-2.5rem)] md:w-[calc(50%-1.5rem)] p-4 rounded-xl border border-border bg-background shadow-sm transition-all hover:shadow-md hover:border-primary/30">
              <div className="flex flex-col gap-1">
                <span className="text-[10px] font-bold uppercase tracking-widest text-primary">
                  {activity.editedSection}
                </span>
                <p className="text-sm text-foreground leading-relaxed">
                  <span className="font-semibold">{activity.adminName}</span> updated{" "}
                  <span className="font-medium text-foreground/90">{activity.changedField}</span> in{" "}
                  <span className="text-primary font-medium">{activity.editedSection}</span>
                  {" — "}
                  <span className="text-muted-foreground line-through decoration-destructive/50">
                    {String(activity.oldValue ?? "—")}
                  </span>
                  {" → "}
                  <span className="font-semibold text-foreground">{String(activity.newValue ?? "—")}</span>
                </p>
                <time className="text-[10px] font-medium text-muted-foreground mt-2 block">
                  {new Date(activity.timestamp).toLocaleString("en-IN", {
                    day: "2-digit",
                    month: "short",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </time>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
