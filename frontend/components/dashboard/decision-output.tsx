"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Cpu, ArrowDownRight, DollarSign, Shield } from "lucide-react"

export interface DecisionResult {
  rlAction: string
  reduction: number
  costSaved: number
  stabilityScore: number
  timestamp: string
}

export function DecisionOutput({
  result,
  error,
}: {
  result: DecisionResult | null
  error?: string | null
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.4, duration: 0.5 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      <div className="mb-5 flex items-center gap-2">
        <Cpu className="size-4 text-neon-purple" />
        <h3 className="font-mono text-xs uppercase tracking-widest text-neon-purple">
          AI Decision Output
        </h3>
      </div>

      <AnimatePresence mode="wait">
        {error ? (
          <motion.div
            key="decision-error"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="rounded-lg border border-neon-red/30 bg-neon-red/10 p-3 font-mono text-xs text-neon-red"
          >
            {error}
          </motion.div>
        ) : result ? (
          <motion.div
            key={result.timestamp}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.4 }}
            className="space-y-4"
          >
            <div className="rounded-lg border border-neon-cyan/20 bg-neon-cyan/5 p-3">
              <div className="mb-1 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                RL Action
              </div>
              <div className="font-mono text-lg font-bold text-neon-cyan">{result.rlAction}</div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="rounded-lg border border-border bg-secondary/50 p-3">
                <div className="mb-2 flex items-center gap-1">
                  <ArrowDownRight className="size-3 text-neon-green" />
                  <span className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">
                    Reduction
                  </span>
                </div>
                <div className="font-mono text-xl font-bold text-neon-green">{result.reduction}%</div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/50 p-3">
                <div className="mb-2 flex items-center gap-1">
                  <DollarSign className="size-3 text-neon-amber" />
                  <span className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">
                    Cost Saved
                  </span>
                </div>
                <div className="font-mono text-xl font-bold text-neon-amber">
                  Rs {result.costSaved}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/50 p-3">
                <div className="mb-2 flex items-center gap-1">
                  <Shield className="size-3 text-neon-cyan" />
                  <span className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">
                    Stability
                  </span>
                </div>
                <div className="font-mono text-xl font-bold text-neon-cyan">
                  {result.stabilityScore}
                </div>
              </div>
            </div>

            <div className="font-mono text-[10px] text-muted-foreground">
              Generated at {result.timestamp}
            </div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex min-h-[180px] flex-col items-center justify-center gap-2 text-muted-foreground"
          >
            <div className="relative">
              <div className="size-12 rounded-full border border-border" />
              <div className="absolute inset-0 animate-ping rounded-full border border-neon-cyan/20" />
            </div>
            <span className="font-mono text-xs">Awaiting decision input...</span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

