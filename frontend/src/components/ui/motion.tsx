import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Tilt from 'react-parallax-tilt'

export const PageTransition = ({ children, className, style }: { children: React.ReactNode, className?: string, style?: React.CSSProperties }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15, filter: 'blur(5px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      exit={{ opacity: 0, y: -15, filter: 'blur(5px)' }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={className}
      style={style}
    >
      {children}
    </motion.div>
  )
}

export const StaggerContainer = ({ children, delay = 0.1, className }: { children: React.ReactNode, delay?: number, className?: string }) => {
  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={{
        hidden: {},
        show: {
          transition: {
            staggerChildren: delay
          }
        }
      }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

export const StaggerItem = ({ children, className }: { children: React.ReactNode, className?: string }) => {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
      }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

export const MotionTiltCard = ({ children, className }: { children: React.ReactNode, className?: string }) => {
  return (
    <Tilt
      tiltMaxAngleX={3}
      tiltMaxAngleY={3}
      scale={1.01}
      transitionSpeed={400}
      className={className}
      glareEnable={true}
      glareMaxOpacity={0.06}
      glareColor="#ffffff"
      glarePosition="all"
    >
      {children}
    </Tilt>
  )
}
