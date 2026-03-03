import { motion } from "framer-motion";

import { cn } from "@/lib/utils";

export function ChatBubble({
  role,
  text,
  meta,
}: {
  role: "user" | "assistant";
  text: string;
  meta?: string;
}) {
  const isUser = role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn("flex", isUser ? "justify-end" : "justify-start")}
    >
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-soft",
          isUser ? "bg-primary text-white" : "border border-slate-200 bg-white text-slateText",
        )}
      >
        <p className="whitespace-pre-wrap">{text}</p>
        {meta ? <p className="mt-2 text-xs opacity-80">{meta}</p> : null}
      </div>
    </motion.div>
  );
}

