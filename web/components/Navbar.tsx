import { Button } from "@/components/ui/button";
import Image from "next/image";
import Link from "next/link";

interface NavItem {
  label: string;
  href: string;
}

const navItems: NavItem[] = [
  {
    label: "Pricing",
    href: "/pricing",
  },
  {
    label: "Features",
    href: "/features",
  },
]

const Navbar = () => {
  return (
    <nav className="flex justify-between container mx-auto py-4 px-6 items-center">
      <Image src="/Dufu_cropped.jpg" alt="Dufu Logo" width={100} height={50} />
      <div className="flex gap-4 items-center justify-center">
        {navItems.map((item: NavItem) => {
          return (
            <Link key={item.href} href={item.href}>
              {item.label}
            </Link>
          )
        })}
        <Button asChild>
          <Link href="/signin">
            Sign in
          </Link>
        </Button>
      </div>
    </nav>
  )
}

export default Navbar;