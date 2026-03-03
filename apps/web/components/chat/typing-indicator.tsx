import { motion } from "framer-motion";

export function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="inline-flex items-center gap-1 rounded-xl border border-slate-200 bg-white px-3 py-2"
    >
      {[0, 1, 2].map((idx) => (
        <motion.span
          key={idx}
          className="h-2 w-2 rounded-full bg-slate-400"
          animate={{ y: [0, -4, 0] }}
          transition={{ duration: 0.9, repeat: Infinity, delay: idx * 0.15 }}
        />
      ))}
    </motion.div>
  );
}

