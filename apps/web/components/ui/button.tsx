"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-2xl text-sm font-semibold transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-95",
  {
    variants: {
      variant: {
        primary: "bg-primary text-white shadow-soft hover:shadow-primary/30 hover:-translate-y-0.5 hover:bg-primaryHover",
        secondary: "bg-white/80 backdrop-blur-md text-slateText border border-slate-200 shadow-sm hover:shadow-md hover:bg-white hover:-translate-y-0.5",
        danger: "bg-danger text-white shadow-soft hover:shadow-danger/30 hover:bg-danger/90 hover:-translate-y-0.5",
        ghost: "text-slateText hover:bg-slate-100",
      },
      size: {
        md: "h-11 px-5",
        lg: "h-14 px-8 text-base shadow-glass",
        sm: "h-8 px-3 text-xs",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
  VariantProps<typeof buttonVariants> { }

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant, size, ...props }, ref) => {
  return <button className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />;
});
Button.displayName = "Button";

export { Button, buttonVariants };

