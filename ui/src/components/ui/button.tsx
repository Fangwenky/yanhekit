import * as React from 'react'
import { cn } from 'cn'

const variants = {
  default: 'bg-primary text-primary-foreground hover:bg-primary/90',
  secondary:
    'bg-secondary text-secondary-foreground hover:bg-[color-mix(in_oklch,var(--secondary),var(--foreground)_5%)]',
  ghost: 'hover:bg-muted hover:text-foreground dark:hover:bg-muted/50',
  muted: 'bg-muted text-muted-foreground hover:bg-accent hover:text-foreground',
}

const sizes = {
  default: 'h-[38px] gap-1.5 px-4 text-sm pointer-coarse:h-11 pointer-coarse:text-base',
  icon: 'size-7',
  round: 'size-6 rounded-full text-xs pointer-coarse:size-8 [&_svg]:stroke-[2.5]',
}

function Button({
  className,
  variant = 'default',
  size = 'default',
  ...props
}: React.ComponentProps<'button'> & { variant?: keyof typeof variants; size?: keyof typeof sizes }) {
  return (
    <button
      data-slot="button"
      className={cn(
        "inline-flex shrink-0 items-center justify-center rounded-md font-medium whitespace-nowrap transition-all outline-none select-none focus-visible:ring-3 focus-visible:ring-ring/50 active:translate-y-px disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-[1em]",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  )
}

export { Button }
