import * as React from 'react'
import { cn } from 'cn'

import { Button } from '@/components/ui/button'

/** A text field with icons, text or buttons beside its input; it draws the border and focus ring. */
function InputGroup({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="input-group"
      role="group"
      className={cn(
        'group/input-group flex h-[38px] w-full min-w-0 items-center rounded-md border border-input text-sm shadow-xs transition-[color,box-shadow,border-color] has-[input:focus-visible]:border-ring has-[input:focus-visible]:ring-3 has-[input:focus-visible]:ring-ring/50 pointer-coarse:h-11 pointer-coarse:text-base dark:bg-input/30',
        className,
      )}
      {...props}
    />
  )
}

function InputGroupAddon({
  className,
  align = 'inline-start',
  ...props
}: React.ComponentProps<'div'> & { align?: 'inline-start' | 'inline-end' }) {
  return (
    <div
      data-slot="input-group-addon"
      data-align={align}
      className={cn(
        'flex shrink-0 cursor-text items-center gap-1 text-muted-foreground select-none group-has-disabled/input-group:opacity-50 [&>svg]:size-[1em] [&>svg]:stroke-[1.5]',
        align === 'inline-start' ? 'order-first pr-2 pl-3' : 'order-last pr-1.5 pl-1',
        className,
      )}
      onClick={(event) => {
        if (!(event.target as HTMLElement).closest('button')) {
          event.currentTarget.parentElement?.querySelector('input')?.focus()
        }
      }}
      {...props}
    />
  )
}

function InputGroupButton({ className, ...props }: React.ComponentProps<typeof Button>) {
  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      className={cn('text-muted-foreground hover:bg-transparent hover:text-foreground', className)}
      {...props}
    />
  )
}

function InputGroupInput({ className, ...props }: React.ComponentProps<'input'>) {
  return (
    <input
      data-slot="input-group-control"
      className={cn(
        'h-full w-full min-w-0 flex-1 bg-transparent pr-3 outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
      {...props}
    />
  )
}

export { InputGroup, InputGroupAddon, InputGroupButton, InputGroupInput }
