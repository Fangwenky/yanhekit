import * as React from 'react'
import { cn } from 'cn'
import { ToggleGroup as ToggleGroupPrimitive } from 'radix-ui'

/** A segmented control; pressed items take the primary tint. */
function ToggleGroup({ className, ...props }: React.ComponentProps<typeof ToggleGroupPrimitive.Root>) {
  return (
    <ToggleGroupPrimitive.Root
      data-slot="toggle-group"
      className={cn('flex w-fit items-center rounded-md shadow-xs', className)}
      {...props}
    />
  )
}

function ToggleGroupItem({ className, ...props }: React.ComponentProps<typeof ToggleGroupPrimitive.Item>) {
  return (
    <ToggleGroupPrimitive.Item
      data-slot="toggle-group-item"
      className={cn(
        'inline-flex h-8 shrink-0 items-center justify-center border border-l-0 border-input px-3 text-sm whitespace-nowrap text-muted-foreground transition-[color,background-color,box-shadow] outline-none first:rounded-l-md first:border-l last:rounded-r-md hover:text-foreground focus-visible:z-10 focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:opacity-50 data-[state=on]:bg-primary/10 data-[state=on]:text-primary dark:bg-input/30 dark:data-[state=on]:bg-primary/25 dark:data-[state=on]:text-foreground pointer-coarse:h-11',
        className,
      )}
      {...props}
    />
  )
}

export { ToggleGroup, ToggleGroupItem }
