import * as React from 'react'
import { cn } from 'cn'
import { Progress as ProgressPrimitive } from 'radix-ui'

/** Without a value, a short bar sweeps across the track. */
function Progress({ className, value, ...props }: React.ComponentProps<typeof ProgressPrimitive.Root>) {
  return (
    <ProgressPrimitive.Root
      data-slot="progress"
      value={value}
      className={cn('relative h-1 w-full overflow-hidden rounded-full bg-muted', className)}
      {...props}
    >
      <ProgressPrimitive.Indicator
        data-slot="progress-indicator"
        className={cn(
          'h-full rounded-full bg-primary transition-[transform,background-color] duration-500',
          value == null ? 'w-2/5 animate-indeterminate' : 'w-full',
        )}
        style={value == null ? undefined : { transform: `translateX(-${100 - value}%)` }}
      />
    </ProgressPrimitive.Root>
  )
}

export { Progress }
