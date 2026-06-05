import { RouterProvider } from "react-router/dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { router } from "./routes";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { appQueryClient } from "./queryClient";

import { EmployeeNotificationPanel } from "./components/ui/EmployeeNotificationPanel";
import { AppChromeEffects } from "./components/ui/AppChromeEffects";

export default function App() {
  return (
    <QueryClientProvider client={appQueryClient}>
      <ThemeProvider>
        <AuthProvider>
          <AppChromeEffects />
          <RouterProvider router={router} />
          <EmployeeNotificationPanel />
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
