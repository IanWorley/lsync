import { RouterProvider, createRouter } from "@tanstack/react-router";
import ReactDOM from "react-dom/client";
import "./index.css";
import { routeTree } from "./routeTree.gen";

// ReactDOM.createRoot(document.getElementById("root")!).render(
//   <React.StrictMode>
//     <NextUIProvider>
//       <main className="dark w-screen h-screen text-foreground bg-background">
//         <App />
//       </main>
//     </NextUIProvider>
//   </React.StrictMode>
// );

// Set up a Router instance
const router = createRouter({
  routeTree,
  defaultPreload: "intent",
});

// Register things for typesafety
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

const rootElement = document.getElementById("root")!;

if (!rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(<RouterProvider router={router} />);
}
