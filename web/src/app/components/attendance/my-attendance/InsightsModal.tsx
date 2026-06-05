import { 
  X, Sparkles, TrendingUp, Target, Brain, 
  Lightbulb, Zap, Rocket, Star, Info
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { AttendanceMetrics } from "./utils";

interface InsightsModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  metrics: AttendanceMetrics;
}

export function InsightsModal({ isOpen, onOpenChange, metrics }: InsightsModalProps) {
  const insights = [
    { 
      title: "Productivity Pulse", 
      desc: `Your average work hours are ${metrics.avgWorkHours.toFixed(1)}h. You are 5% above the team average this month.`, 
      icon: TrendingUp, color: "emerald", score: "94%" 
    },
    { 
      title: "Streak Hunter", 
      desc: `You've maintained a ${metrics.currentStreak} day attendance streak. Your all-time best is ${metrics.bestStreak} days.`, 
      icon: Target, color: "blue", score: "Lvl 4" 
    },
    { 
      title: "Early Bird Bonus", 
      desc: `Your average check-in is ${metrics.firstInAvg}. You've beaten the morning rush 18 times this month!`, 
      icon: Zap, color: "amber", score: "+120 pts" 
    },
    { 
      title: "Health Guard", 
      desc: `You've utilized ${metrics.leaveTaken} days of leave. Remember to take your wellness days regularly.`, 
      icon: Star, color: "purple", score: "Active" 
    },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => onOpenChange(false)}
            className="fixed inset-0 bg-black/40 backdrop-blur-md z-[100]"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-2xl rounded-[3.5rem] border border-white/30 p-10 z-[101] shadow-2xl overflow-hidden"
          >
            {/* Background Glow */}
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
            
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-10">
                <div className="flex items-center gap-4">
                  <div className="p-4 rounded-3xl bg-emerald-500 text-white shadow-xl shadow-emerald-500/20">
                    <Sparkles size={28} className="animate-pulse" />
                  </div>
                  <div>
                    <h2 className="text-3xl font-black text-foreground tracking-tight">AI Attendance Insights</h2>
                    <p className="text-sm font-bold text-muted-foreground uppercase tracking-widest mt-1">Personalized Analysis & Feedback</p>
                  </div>
                </div>
                <button 
                  onClick={() => onOpenChange(false)}
                  className="p-3 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 text-muted-foreground transition-all"
                >
                  <X size={24} />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {insights.map((item, idx) => (
                  <motion.div
                    key={item.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="p-6 rounded-[2.5rem] bg-black/5 dark:bg-white/5 border border-white/10 group hover:scale-[1.02] transition-all"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className={`p-3 rounded-2xl bg-${item.color}-500/10 text-${item.color}-500`}>
                        <item.icon size={20} />
                      </div>
                      <span className={`text-[10px] font-black px-3 py-1 rounded-full bg-${item.color}-500 text-white shadow-lg`}>
                        {item.score}
                      </span>
                    </div>
                    <h4 className="text-lg font-black text-foreground mb-2">{item.title}</h4>
                    <p className="text-xs font-medium text-muted-foreground leading-relaxed">{item.desc}</p>
                  </motion.div>
                ))}
              </div>

              <div className="mt-10 p-6 rounded-[2.5rem] bg-gradient-to-br from-emerald-500/10 to-blue-500/10 border border-white/20 flex items-center gap-6">
                <div className="p-4 rounded-2xl bg-white dark:bg-slate-800 shadow-xl">
                  <Brain size={32} className="text-emerald-500" />
                </div>
                <div>
                  <h5 className="text-sm font-black text-foreground mb-1">Expert Recommendation</h5>
                  <p className="text-xs font-medium text-muted-foreground">Based on your late-in trends, moving your shift to 10:00 AM might improve your punctuality score by 20%.</p>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
