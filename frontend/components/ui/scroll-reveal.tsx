"use client"

import { useEffect, useRef, useState, type ReactNode } from "react"
import { motion, useInView } from "framer-motion"
import { cn } from "@/lib/utils"

interface ScrollRevealProps {
  children: ReactNode
  className?: string
  delay?: number
  distance?: number
  amount?: number
  once?: boolean
}

export function ScrollReveal({
  children,
  className,
  delay = 0,
  distance = 18,
  amount = 0.1,
  once = true,
}: ScrollRevealProps) {
  const ref = useRef<HTMLDivElement | null>(null)
  const inView = useInView(ref, { amount, margin: "0px 0px -8% 0px" })
  const [revealed, setRevealed] = useState(false)

  useEffect(() => {
    if (inView) {
      setRevealed(true)
    }
  }, [inView])

  const shouldShow = once ? revealed || inView : inView

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: distance }}
      animate={shouldShow ? { opacity: 1, y: 0 } : { opacity: 0, y: distance }}
      transition={{ duration: 0.45, ease: "easeOut", delay }}
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}
