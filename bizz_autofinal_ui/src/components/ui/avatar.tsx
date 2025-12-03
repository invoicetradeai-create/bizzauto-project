"use client";

import * as React from "react";
import * as AvatarPrimitive from "@radix-ui/react-avatar";
import { cn } from "@/lib/utils";

function Avatar({
  className,
  ...props
}: React.ComponentProps<typeof AvatarPrimitive.Root>) {
  return (
    <AvatarPrimitive.Root
      data-slot="avatar"
      className={cn(
        "relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full bg-blue-600 text-white",
        className
      )}
      {...props}
    />
  );
}

function AvatarImage({
  className,
  ...props
}: React.ComponentProps<typeof AvatarPrimitive.Image>) {
  return (
    <AvatarPrimitive.Image
      data-slot="avatar-image"
      className={cn("aspect-square h-full w-full", className)}
      {...props}
    />
  );
}

function AvatarFallback({
  className,
  ...props
}: React.ComponentProps<typeof AvatarPrimitive.Fallback>) {
  const [avatarLetter, setAvatarLetter] = React.useState<string>("");

  React.useEffect(() => {
    // ✅ Check if we are on client-side
    if (typeof window !== "undefined") {
      const storedLetter = localStorage.getItem("user_avatar");
      setAvatarLetter(storedLetter ? storedLetter.toUpperCase() : "?");
    }
  }, []);

  return (
    <AvatarPrimitive.Fallback
      data-slot="avatar-fallback"
      className={cn(
        "flex items-center justify-center rounded-full bg-blue-600 text-white font-semibold text-sm w-full h-full",
        className
      )}
      {...props}
    >
      {props.children || avatarLetter || "?"}
    </AvatarPrimitive.Fallback>
  );
}

export { Avatar, AvatarImage, AvatarFallback };
