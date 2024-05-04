import {
  Navbar,
  NavbarContent,
  NavbarItem,
  NextUIProvider,
} from "@nextui-org/react";
import { Link, Outlet, createRootRoute } from "@tanstack/react-router";
import Providers from "../components/providers";

export const Route = createRootRoute({
  component: RootComponent,
  notFoundComponent: () => {
    return <p>This is the notFoundComponent configured on root route</p>;
  },
});

function RootComponent() {
  return (
    <>
      <Providers>
        <NextUIProvider>
          <div className="dark min-h-svh min-w-svw text-foreground bg-background">
            <Navbar className="">
              <NavbarContent className="hidden sm:flex gap-4" justify="center">
                <NavbarItem>
                  <Link to="/">Home</Link>
                </NavbarItem>
                <NavbarItem>
                  <Link to="/config">Config</Link>
                </NavbarItem>
              </NavbarContent>
            </Navbar>
            <Outlet />
          </div>
        </NextUIProvider>
      </Providers>
    </>
  );
}
