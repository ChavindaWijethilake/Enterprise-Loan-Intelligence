"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { ChevronDown } from "lucide-react";

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div className="relative">
        <select
          className={cn(
            "flex h-12 w-full appearance-none rounded-xl border border-white/5 bg-white/5 px-4 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 cursor-pointer transition-all",
            className
          )}
          ref={ref}
          {...props}
        >
          {children}
        </select>
        <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
      </div>
    );
  }
);
Select.displayName = "Select";

export { Select };
