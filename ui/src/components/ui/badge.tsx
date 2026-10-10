import * as React from 'react'
import { cn } from 'cn'

function Badge({ className, ...props }: React.ComponentProps<'span'>) {
  return (
    <span
      data-slot="badge"
      className={cn(
        'inline-flex h-5 w-fit shrink-0 items-center justify-center rounded-full bg-secondary px-2 text-[0.625rem] whitespace-nowrap text-secondary-foreground',
        className,
      )}
      {...props}
    />
  )
}

export { Badge }
