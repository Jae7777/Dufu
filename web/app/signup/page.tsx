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

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSocialSignup = async (provider: string) => {
    try {
      setIsLoading(true);
      setError("");
      await authClient.signIn.social({
        provider: provider as any,
        callbackURL: "/",
      });
    } catch (err) {
      setError("Failed to sign up with " + provider);
      console.error("Social signup error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = () => {
    if (!name.trim()) {
      setError("Please enter your name");
      return false;
    }
    if (!email.trim()) {
      setError("Please enter your email");
      return false;
    }
    if (!email.includes("@")) {
      setError("Please enter a valid email address");
      return false;
    }
    if (!password) {
      setError("Please enter a password");
      return false;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters long");
      return false;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return false;
    }
    return true;
  };

  const handleEmailPasswordSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setIsLoading(true);
      setError("");
      
      const result = await authClient.signUp.email({
        email,
        password,
        name,
        callbackURL: "/",
      });

      if (result.error) {
        setError(result.error.message || "Failed to create account");
      } else {
        router.push("/");
        router.refresh();
      }
    } catch (err) {
      setError("An unexpected error occurred");
      console.error("Signup error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="container mx-auto min-h-screen">
      <form onSubmit={handleEmailPasswordSignup} className="flex flex-col gap-4 max-w-md mx-auto mt-24">
        <h1 className="text-2xl text-center font-bold">Create your Dufu account</h1>
        <p className="text-center text-sm text-muted-foreground">Join us today! Create your account to get started.</p>
        
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
              onClick={() => handleSocialSignup(login.id)}
              className="flex items-center gap-2"
            >
              <login.icon />
              Continue with {login.label}
            </Button>
          ))}
        </div>
        
        <div className="flex gap-2 items-center justify-center w-full">
          <Separator className="flex-1 min-w-0" />
          <p className="whitespace-nowrap text-sm text-muted-foreground px-2">OR CONTINUE WITH</p>
          <Separator className="flex-1 min-w-0" />
        </div>
        
        <div className="flex flex-col gap-2">
          <Label htmlFor="name">Full Name</Label>
          <Input 
            id="name"
            type="text" 
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={isLoading}
            required
            placeholder="Enter your full name"
          />
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
            placeholder="Enter your email"
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
            placeholder="Create a password"
            minLength={6}
          />
        </div>
        
        <div className="flex flex-col gap-2">
          <Label htmlFor="confirmPassword">Confirm Password</Label>
          <Input 
            id="confirmPassword"
            type="password" 
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            disabled={isLoading}
            required
            placeholder="Confirm your password"
            minLength={6}
          />
        </div>
        
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Creating account..." : "Create account"}
        </Button>
        
        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href="/signin" className="text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </form>
    </main>
  );
}
