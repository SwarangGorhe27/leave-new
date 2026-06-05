import React from 'react';
import { motion } from 'motion';

interface FormSectionProps {
  id: string;
  children: React.ReactNode;
  className?: string;
}

export function FormSection({ id, children, className = "" }: FormSectionProps) {
  return (
    <motion.div 
      id={id}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      className={`bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-[2.5rem] border border-white/40 dark:border-gray-800/40 p-8 shadow-[0_20px_50px_rgba(0,0,0,0.04)] scroll-mt-32 ${className}`}
    >
      {children}
    </motion.div>
  );
}
