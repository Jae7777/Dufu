"use client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { authClient } from "@/lib/auth-client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { IconType } from "react-icons";
import { FaApple, FaDiscord, FaGithub, FaGoogle } from "react-icons/fa";

interface SocialLogin {
  id: string;
  label: string;
  icon: IconType;
  href: string;
}
const socialLogins: SocialLogin[] = [
  {
    id: "google",
    label: "Google",
    icon: FaGoogle,
    href: "/auth/google",
  },
  {
    id: "discord",
    label: "Discord",
    icon: FaDiscord,
    href: "/auth/discord",
  },
  {
    id: "apple",
    label: "Apple",
    icon: FaApple,
    href: "/auth/apple",
  },
  {
    id: "github",
    label: "Github",
    icon: FaGithub,
    href: "/auth/github",
  },
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSocialLogin = async (provider: string) => {
    try {
      setIsLoading(true);
      setError("");
      await authClient.signIn.social({
        provider: provider,
        callbackURL: "/",
      });
    } catch (err) {
      setError("Failed to sign in with " + provider);
      console.error("Social login error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailPasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError("Please fill in all fields");
      return;
    }

    try {
      setIsLoading(true);
      setError("");
      
      const result = await authClient.signIn.email({
        email,
        password,
        callbackURL: "/",
      });

      if (result.error) {
        setError(result.error.message || "Failed to sign in");
      } else {
        router.push("/");
        router.refresh();
      }
    } catch (err) {
      setError("An unexpected error occurred");
      console.error("Login error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="container mx-auto min-h-screen">
      <form onSubmit={handleEmailPasswordLogin} className="flex flex-col gap-4 max-w-md mx-auto mt-24">
        <h1 className="text-2xl text-center font-bold">Sign in to Dufu</h1>
        <p className="text-center text-sm text-muted-foreground">Welcome back! Please sign in.</p>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
            {error}
          </div>
        )}

        <div className="flex flex-col gap-4">
          {socialLogins.map((login) => (
            <Button 
              key={login.id} 
              type="button"
              variant="outline"
              disabled={isLoading}
              onClick={() => handleSocialLogin(login.id)}
              className="flex items-center gap-2"
            >
              <login.icon />
              {login.label}
            </Button>
          ))}
        </div>
        
        <div className="flex gap-2 items-center justify-center w-full">
          <Separator className="flex-1 min-w-0" />
          <p className="whitespace-nowrap text-sm text-muted-foreground px-2">OR CONTINUE WITH</p>
          <Separator className="flex-1 min-w-0" />
        </div>
        
        <div className="flex flex-col gap-2">
          <Label htmlFor="email">Email</Label>
          <Input 
            id="email"
            type="email" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isLoading}
            required
          />
        </div>
        
        <div className="flex flex-col gap-2">
          <Label htmlFor="password">Password</Label>
          <Input 
            id="password"
            type="password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            required
          />
        </div>
        
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Signing in..." : "Sign in"}
        </Button>
        
        <p className="text-center text-sm text-muted-foreground">
          Don&apos;t have an account?{" "}
          <Link href="/signup" className="text-primary hover:underline">
            Sign up
          </Link>
        </p>
      </form>
    </main>
  );
}
