import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import Link from "next/link";
import { IconType } from "react-icons";
import { FaApple, FaDiscord, FaGithub, FaGoogle } from "react-icons/fa";

interface SocialLogin {
  label: string;
  icon: IconType;
  href: string;
}
const socialLogins = [
  {
    label: "Google",
    icon: FaGoogle,
    href: "/auth/google",
  },
  {
    label: "Discord",
    icon: FaDiscord,
    href: "/auth/discord",
  },
  {
    label: "Apple",
    icon: FaApple,
    href: "/auth/apple",
  },
  {
    label: "Github",
    icon: FaGithub,
    href: "/auth/github",
  },
];

export default function loginPage() {
  return (
    <main className="container mx-auto min-h-screen">
      <form className="flex flex-col gap-4 max-w-128 mx-auto mt-24">
        <h1 className="text-2xl text-center font-bold">Sign in to Dufu</h1>
        <p className="text-center text-sm text-muted-foreground">Welcome back! Please sign in.</p>
        <div className="flex flex-col gap-4">
          {socialLogins.map((login) => (
            <Button key={login.href} asChild>
              <Link href={login.href}>
                <login.icon />
                {login.label}
              </Link>
            </Button>
          ))}
        </div>
        <div className="flex gap-2 items-center justify-center w-full">
          <Separator className="flex-1 min-w-0" />
          <p className="whitespace-nowrap text-sm text-muted-foreground px-2">OR CONTINUE WITH</p>
          <Separator className="flex-1 min-w-0" />
        </div>
        <div className="flex flex-col gap-2">
          <Label>Email</Label>
          <Input type="email" />
        </div>
        <div className="flex flex-col gap-2">
          <Label>Password</Label>
          <Input type="password" />
        </div>
        <Button type="submit">Sign in</Button>
      </form>
    </main>
  );
}
